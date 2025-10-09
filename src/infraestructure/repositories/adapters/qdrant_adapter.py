"""
Qdrant Adapter: Load and query embeddings in a vector database.

This module allows you to:
- Connect to a Qdrant server.
- Load embeddings from `.pkl` files in a directory.
- Create collections in Qdrant and store embeddings for audio, text, and video.
- Perform similarity searches in the database.

Requirements:
- `torch`, `numpy`, and `qdrant_client` for embedding processing and Qdrant connection.
- `pickle` for loading and storing embeddings in files.

Author: Marcos Infante
Date: 2025-02-25
"""

import uuid
import torch
import numpy as np
from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, Distance, PointStruct
from src.domain.repositories.adapters.vector_store import VectorStoreAdapter



class QdrantAdapter(VectorStoreAdapter):
    """
    Adapter for handling embeddings in Qdrant.
    Allows loading, storing, and searching for audio, text, and video vectors.
    """

    def __init__(self, config_path:str):
        """
        Initializes the connection with Qdrant.

        Args:
            connection_config (dict): Connection settings (host, port, api_key).
            config (dict): Common settings (collection name).
        """
        super().__init__(config_path)
        self.__config = self._config
        self.collection_name = self.__config["qdrant"]["parameters"]["collection_name"]
        self.client = None

    def connect(self):
        """Establishes a connection to the Qdrant server if not already connected."""
        if not self.client:
            self.client = QdrantClient(
                host=self.__config["qdrant"]["connection_config"]['host'],
                port=self.__config["qdrant"]["connection_config"]['port'],
                api_key=self.__config["qdrant"]["connection_config"].get('api_key', None),
                https=False
            )
        print("✅ Successfully connected to Qdrant.")



    def upload(self, embedding_dict: dict, vector_names: list = None):
        """
        Uploads selected embeddings to Qdrant as named vectors, creating the collection if needed.

        :param embedding_dict: Dictionary containing 'vectors' and 'payload'.
        :param vector_names: List of vector names to upload (e.g., ['audio', 'video']). If None, all vectors will be uploaded.
        """
        try:
            points = []

            # Extract vectors from the dictionary
            vectors = embedding_dict["vectors"]
            payload = embedding_dict["payload"]

            # If no vector names are provided, upload all vectors
            if vector_names is None:
                vector_names = list(vectors.keys())

            # Create a point for multiple vectors
            point_vector = {}

            # Loop through the selected vector names and add them to the point's vector
            for vector_name in vector_names:
                # Ensure the vector name exists in the dictionary
                if vector_name in vectors:
                    point_vector[vector_name] = vectors[vector_name]
                else:
                    print(f"⚠️ Vector name '{vector_name}' not found in the embedding dictionary.")

            # If there are any vectors to upload, create a PointStruct
            if point_vector:
                point = PointStruct(id=str(uuid.uuid4()), vector=point_vector, payload=payload)
                points.append(point)

                # Upload the point to the collection
                self.client.upsert(collection_name=self.collection_name, points=points)
                print("✅ Successfully uploaded data to Qdrant.")
            else:
                print("❌ No vectors selected for upload.")

        except Exception as e:
            print(f"❌ Error uploading data to Qdrant: {e}")
    
    def _check_collection(self):
        """
        Checks if the collection exists in Qdrant.
        """
        try:
            collections = [collection.name for collection in self.client.get_collections().collections]
            if self.collection_name in collections:
                print(f"ℹ️ Collection '{self.collection_name}' already exists.")
                return True
            else:
                print(f"ℹ️ Collection '{self.collection_name}' does not exist.")
                return False
        except Exception as e:
            print(f"❌ Error verifying collection: {e}")
            return False
        
    def _create_collection(self, vector_configs: dict):
        """
        Creates the collection in Qdrant.
        """
        try:
            vectors_config = {
                name: VectorParams(size=dim, distance=Distance.COSINE)
                for name, dim in vector_configs.items()
            }
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=vectors_config
            )
            print(f"📦 Collection '{self.collection_name}' created with config: {vector_configs}")
        except Exception as e:
            print(f"❌ Error creating collection: {e}")

    def _convert_to_list(self, embedding):
        """
        Converts an embedding into a list if necessary.

        Args:
            embedding: Can be a PyTorch tensor, NumPy array, or a list.

        Returns:
            list: List representation of the embedding.
        """
        if isinstance(embedding, torch.Tensor):
            return embedding.tolist()
        if isinstance(embedding, np.ndarray):
            return embedding.tolist()
        if isinstance(embedding, list):
            return embedding
        raise ValueError(f"❌ Invalid embedding format: {type(embedding)}")

    def close(self):
        """Closes the connection to Qdrant."""
        if self.client:
            self.client.close()
            print("🔒 Qdrant connection closed.")

    def _list_collections(self):
        """
        Retrieves a list of available collections in Qdrant.

        Returns:
            list: Names of Qdrant collections.
        """
        try:
            collections = self.client.get_collections()
            return [collection.name for collection in collections.collections]
        except Exception as e:
            print(f"❌ Error retrieving collections: {e}")
            return []

#TODO add filters.