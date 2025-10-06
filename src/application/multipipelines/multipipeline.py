"""
Class for uploading multi-vector points to the database.

Author: Marcos Infante  
Date: 2025-03-25
"""

import asyncio
import os
import pickle
import torch
import numpy as np
from src.domain.config.config_loader import ConfigLoader
from src.application.pipelines.text_pipeline import TextPipeline
from src.application.pipelines.audio_pipeline import AudioPipeline
from src.application.pipelines.video_pipeline import VideoPipeline
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
from src.infraestructure.ai_services.ollama_llm_provider import OLLamaLLMProvider
from src.infraestructure.repositories.adapters.qdrant_adapter import QdrantAdapter


class MultiplePipeline:
    """
    MultiplePipeline handles the coordination of multiple media processing pipelines (audio and video)
    and the upload of their resulting multi-vector embeddings to a Qdrant database.

    Responsibilities:
    - Run multiple pipelines concurrently or sequentially.
    - Load embeddings from disk and validate their structure.
    - Upload structured vector data with associated payloads to Qdrant.

    Attributes:
        __config (dict): Loaded configuration from the YAML file.
        pipelines (list): List of instantiated processing pipelines.
        vector_store_adapter (QdrantAdapter): Adapter for interacting with Qdrant vector database.
    """

    def __init__(self, config_path: str):
        """
        Initializes the class by loading configuration and setting up pipelines.

        Args:
            config_path (str): Path to the configuration YAML file.
        """
        self.__config = ConfigLoader.load_config(config_path)
        self.vector_store_adapter = QdrantAdapter(config_path)
        self.llm_provider = OLLamaLLMProvider(self.__config["llm_config"])
        self.pipelines = self._create_pipelines()

    def _create_pipelines(self):
        """
        Creates instances of the audio and video pipelines.

        Returns:
            list: List of initialized pipeline objects.
        """
        pipelines = []
        if "video" in self.__config["to_run"]:
            print("🎥 Video section found. Loading VideoPipeline...")
            pipelines.append(VideoPipeline(self.__config["pipelines_config"], self.llm_provider))

        if "audio" in self.__config["to_run"]:
            print("🎧 Audio section found. Loading AudioPipeline...")
            pipelines.append(AudioPipeline(self.__config["pipelines_config"], self.llm_provider))

        
        if "text" in self.__config["to_run"]:
            print("📝 Text section found. Loading TextPipeline...")
            pipelines.append(TextPipeline(self.__config["pipelines_config"]))

        return pipelines

    async def _run_concurrent_pipelines(self):
        """
        Runs multiple pipelines concurrently using a process pool.
        Waits for all tasks to complete before continuing.
        """
       
        await asyncio.gather(*(pipeline.run_pipeline() for pipeline in self.pipelines))

    async def run(self):
        """
        Main execution method:
        - Runs the pipelines 
        - Processes and uploads the generated embeddings.
        """
        await self._run_concurrent_pipelines()  
        os.makedirs(self.__config["embeddings"]["embeddings_dir"], exist_ok=True)
        self.process_and_upload_embeddings()

    def process_and_upload_embeddings(self):
        """
        Processes and uploads embeddings to Qdrant in the following steps:
        1. Connects to Qdrant and creates a new collection.
        2. Iterates through each embeddings subdirectory.
        3. Validates and uploads the multi-vector data with its metadata payload.
        """
        embeddings_root = self.__config["embeddings"]["embeddings_dir"]

        if not os.path.exists(embeddings_root):
            raise FileNotFoundError(f"❌ Directory not found: {embeddings_root}")

        self.vector_store_adapter.connect()
        vector_sizes = {
            name: params['size']
            for name, params in self.__config["embeddings"]["vector_types"].items()
        }
        self.vector_store_adapter._create_collection(vector_sizes)

        for subdir in sorted(os.listdir(embeddings_root)):
            subdir_path = os.path.join(embeddings_root, subdir)

            if os.path.isdir(subdir_path):
                print(f"📂 Processing embeddings in: {subdir_path}")

                try:
                    embeddings_data = self._create_multivector_points(subdir_path)

                    if embeddings_data:
                        named_vectors = {
                            vector_name: vector
                            for vector_name, vector in embeddings_data['vectors'].items()
                        }

                        # Llamada a validate_dimensions desde cada pipeline
                        for pipeline in self.pipelines:
                            pipeline.validate_dimensions(named_vectors, self.__config)

                        unified_payload = self._generate_formatted_payload(embeddings_data["payload"])

                        embedding_dict = {
                            "vectors": named_vectors,
                            "payload": unified_payload
                        }

                        print(f"⬆️ Uploading named vectors to Qdrant with dimensions {[vector.shape[0] for vector in named_vectors.values()]}...")
                        self.vector_store_adapter.upload(embedding_dict)

                except Exception as e:
                    print(f"⚠️ Error processing {subdir}: {e}")

    def _create_multivector_points(self, embeddings_dir: str):
        """
        Loads embeddings from a given directory and constructs multi-vector points.

        Args:
            embeddings_dir (str): Path to the directory containing embedding pickle files.

        Returns:
            dict: Dictionary with named vectors and associated payload.

        Raises:
            FileNotFoundError: If the embeddings directory does not exist.
            ValueError: If no valid embeddings or payloads are found.
        """
        embeddings = {}
        payload = {}

        if not os.path.exists(embeddings_dir):
            raise FileNotFoundError(f"Embeddings directory does not exist: {embeddings_dir}")

        for filename in os.listdir(embeddings_dir):
            filepath = os.path.join(embeddings_dir, filename)
            try:
                with open(filepath, 'rb') as file:
                    data = pickle.load(file)

                    for key, value in data.items():
                        if key != "payload" and "payload" in data:
                            if isinstance(value, (list, tuple, np.ndarray, torch.Tensor)) and len(value) > 0:
                                embeddings[key] = value
                                payload[key] = data['payload']
                            else:
                                print(f"⚠️ Empty or invalid embedding in {filename}, skipping key: {key}")
            except Exception as e:
                print(f"Error processing {filename}: {e}")

        if not embeddings:
            raise ValueError("No valid embeddings found in directory.")
        if payload is None:
            raise ValueError("No valid payload found in directory.")

        return {'vectors': embeddings, 'payload': payload}

    @staticmethod
    def _generate_formatted_payload(payload:dict, fields: list = None) -> dict:
        """
        Promotes common fields like 'start_time', 'end_time', 'clip_index' to top-level
        only if they exist with the same name in multiple nested sections (e.g., 'audio', 'video').

        Args:
            payload (dict): Original payload with nested dictionaries.
            fields (list): Fields to promote if they exist in multiple sections.

        Returns:
            dict: New payload with promoted fields + original nested structure.
        """
        if fields is None:
            fields = ["start_time", "end_time", "clip_index"]

        promoted = {}

        for field in fields:
            values = []
            for section in payload.values():
                if isinstance(section, dict) and field in section:
                    values.append(section[field])
            if len(values) > 1:
                # Promote only if field appears in multiple sections
                promoted[field] = values[0]  # Use the first occurrence

        merged = {**promoted, **payload}
        return merged

