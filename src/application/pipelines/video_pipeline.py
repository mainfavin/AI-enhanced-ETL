import os
import yaml
import uuid
import numpy as np
from src.domain.config.config_loader import ConfigLoader
from src.domain.entities.pipelines.pipeline import Pipeline
from src.application.pipelines.text_pipeline import TextPipeline
from src.infraestructure.repositories.loaders.video_loader import VideoLoader
from src.infraestructure.repositories.adapters.qdrant_adapter import QdrantAdapter 
from src.infraestructure.repositories.splitters.video_splitter import VideoSplitter
from src.infraestructure.repositories.describers.video_describer import VideoDescriber
from src.infraestructure.repositories.embeddings.video_embedding_generator import VideoEmbedder


class VideoPipeline(Pipeline):
    """
    VideoPipeline class is responsible for processing video files by:
    - Splitting videos into smaller clips.
    - Generating embeddings for each clip.
    - Storing embeddings along with metadata.
    - Uploading processed embeddings to Qdrant.

    Attributes:
        VIDEOS_DIR (str): Directory for storing video files.
        CLIPS_DIR (str): Directory for storing video clips.
        EMBEDDINGS_DIR (str): Directory for storing embeddings.
        adapter (QdrantAdapter): Adapter to interface with Qdrant.
    """

    def __init__(self, config_paths: str, llm_provider = None):
        """
        Initializes the video processing pipeline.

        Args:
            config_paths (str): Path to the configuration file.
        """
        self.config_path = config_paths
        self.__config = ConfigLoader.load_config(config_paths)
        
        # Define directories for storing video files, clips, and embeddings
        self.ensure_existing_dir("video",self.__config["video"]["videos_dir"],
                                self.__config["video"]["clips_dir"],
                                self.__config["video"]["embeddings_dir"])
        
        self.text_pipeline = TextPipeline(self.config_path)
        self.video_loader = VideoLoader()
        self.video_splitter = VideoSplitter(self.__config["video_splitter_config"])
        self.video_embedder = VideoEmbedder(self.__config["embedder_config"]) 
        self.video_describer = VideoDescriber(self.__config["describer_config"],llm_provider)
        #self.adapter = QdrantAdapter(config_paths)

    async def run_pipeline(self):
        """
        Runs the video processing pipeline.

        Steps:
        1. Splits the video into smaller clips.
        2. Generates embeddings for each clip.
        3. Stores embeddings along with metadata.
        4. Uploads processed embeddings to Qdrant.
        """
        video_path = self.__config["video"]["video_path"]
        clips_output_dir = self.get_output_dir(video_path,self.CLIPS_DIR)
        embeddings_output_dir = self.get_output_dir(video_path,self.EMBEDDINGS_DIR)
        self._update_output_dir(self.__config["video_splitter_config"], clips_output_dir) #TODO: replantear esto.

        clips_dict = self.split(video_path)
        
        # Process each video clip
        for clip_index, (clip_key, clip_info) in enumerate(clips_dict.items(), start=1):
            clip_path = clip_info["clip_path"]
            start_time = clip_info["start_time"]
            end_time = clip_info["end_time"]
            print(f"Processing clip: {clip_path} (Start: {start_time}s, End: {end_time}s)")

            # Generate embedding
            embedding = self.get_embedding(clip_path)
            description = await self.get_description(clip_path)
            # CALL TEXT PIPELINE OVER DESCRIPTION
            self.text_pipeline.run_from_text(description) #no need for await here.
            # Construct metadata payload
            params = self.__config["video"]["config"]["parameters"]
            payload = {
                'video_clip_path': clip_path,
                'clip_index': clip_index,
                'start_time': start_time,
                'end_time': end_time,
                'description': description, #Esto es un objeto corrutina.
                'params': params
            }

            # Save embedding and payload as a pickle file
            clip_dir = os.path.join(embeddings_output_dir, f"clip_{clip_index}")
            self.generate_pkl_point(os.path.join(clip_dir, "video.pkl"), embedding, payload ,"video")



    def load(self, video_path: str):
        """
        Loads an video file.

        Args:
            video_path (str): Path to the video file.

        Returns:
            np.ndarray: video data.
        """
        return self.video_loader.load(video_path)
    
    def split(self, video_path: str):
        """
        Splits a video file into smaller clips of fixed duration.

        Args:
            video_path (str): Path to the video file.

        Returns:
            dict: Dictionary containing clip paths, start times, and end times.
        """
        
        video = self.load(video_path)
        return self.video_splitter.split(video)

    def get_embedding(self, video_path: str) -> np.ndarray:
        """
        Generates an embedding for a video file.

        Args:
            video_path (str): Path to the video file.

        Returns:
            np.ndarray: Embedding vector.
        """
        
        return self.video_embedder.get_embeddings(video_path)
    
    async def get_description(self, video_path: str) -> str:
        """
        Generates a description for a video file.

        Args:
            video_path (str): Path to the video file.

        Returns:
            str: Description of the video.
        """
        
        return await self.video_describer.generate_description(video_path)
    
