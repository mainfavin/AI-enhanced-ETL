import os
import yaml
import uuid
import pickle
import librosa
import numpy as np
from src.domain.config.config_loader import ConfigLoader
from src.domain.entities.pipelines.pipeline import Pipeline
from src.application.pipelines.text_pipeline import TextPipeline

from src.infraestructure.repositories.loaders.audio_loader import AudioLoader
from src.infraestructure.repositories.loaders.video_loader import VideoLoader
from src.infraestructure.repositories.splitters.audio_splitter import AudioSplitter
from src.infraestructure.repositories.describers.audio_describer import AudioDescriber
from src.infraestructure.repositories.transcribers.audio_transcriber import AudioTranscriber
from src.infraestructure.repositories.embeddings.audio_embedding_generator import AudioEmbedder


class AudioPipeline(Pipeline):
    """
    AudioPipeline class is responsible for processing audio files by:
    - Splitting audio into smaller clips.
    - Generating embeddings for each clip.
    - Storing embeddings along with metadata.
    - Uploading processed embeddings to Qdrant.

    Attributes:
        AUDIOS_DIR (str): Directory for storing audio files.
        CLIPS_DIR (str): Directory for storing audio clips.
        EMBEDDINGS_DIR (str): Directory for storing embeddings.
        adapter (QdrantAdapter): Adapter to interface with Qdrant.
    """

    def __init__(self, config_paths: str, llm_provider = None):
        """
        Initializes the audio processing pipeline.

        Args:
            config_paths (str): Path to the configuration file.
        """
        self.config_path = config_paths
        self.__config = ConfigLoader.load_config(config_paths)
        self.ensure_existing_dir("audio",self.__config["audio"]["audios_dir"],
                                self.__config["audio"]["clips_dir"],
                                self.__config["audio"]["embeddings_dir"])
        
        self.audio_loader = AudioLoader()
        self.audio_transcriber = AudioTranscriber()
        self.audio_splitter = AudioSplitter(self.__config["audio_splitter_config"])
        self.audio_embedder = AudioEmbedder(self.__config["embedder_config"])
        self.audio_describer = AudioDescriber(self.__config["describer_config"],llm_provider)
        self.text_pipeline = TextPipeline(self.config_path)
        #self.adapter = QdrantAdapter(config_paths)

    async def run_pipeline(self):
        """
        Runs the audio processing pipeline.
        
        Steps:
        1. Splits the audio into smaller clips.
        2. Generates embeddings for each clip.
        3. Stores embeddings along with metadata.
        4. Uploads processed embeddings to Qdrant.
        """
        audio_path = self.__config["audio"]["audio_path"]
        audio_path = self.check_file_type(audio_path)
        
        clips_output_dir = self.get_output_dir(audio_path, self.CLIPS_DIR)
        embeddings_output_dir = self.get_output_dir(audio_path, self.EMBEDDINGS_DIR)
        self._update_output_dir(self.__config["audio_splitter_config"], clips_output_dir) #TODO: replantear esto.

        clips_dict = self.split(audio_path)
        
        # Process each audio clip
        for clip_index, (clip_key, clip_info) in enumerate(clips_dict.items(), start=1):
            clip_path = clip_info["clip_path"]
            start_time = clip_info["start_time"]
            end_time = clip_info["end_time"]
            print(f"Processing clip: {clip_path} (Start: {start_time}s, End: {end_time}s)")

            # Generate embedding and transcription
            embedding = self.get_embedding(clip_path)
            transcription = self.get_transcription(clip_path)
            description = await self.get_description(clip_path)
            # CALL TEXT PIPELINE OVER DESCRIPTION      
            self.text_pipeline.run_from_text(description)
            # Construct metadata payload
            params = self.__config["audio"]["config"]["parameters"]
            payload = {
                'audio_clip_path': clip_path,
                'start_time': start_time,
                'end_time': end_time,
                'clip_index': clip_index,
                'transcription': transcription,
                'params': params
            }

            # Save embedding and payload as a pickle file
            clip_dir = os.path.join(embeddings_output_dir, f"clip_{clip_index}")
            self.generate_pkl_point(os.path.join(clip_dir, "audio.pkl"), embedding,payload ,"audio")



    def load(self, audio_path: str):
        """
        Loads an audio file.

        Args:
            audio_path (str): Path to the audio file.

        Returns:
            np.ndarray: Audio data.
        """
        return self.audio_loader.load(audio_path)
    
    def split(self, audio_path: str):
        """
        Splits an audio file into smaller clips based on the specified method.

        Args:
            audio_path (str): Path to the audio file.
            
        Returns:
            dict: Dictionary containing clip paths, start times, and end times.
        """
        audio = self.load(audio_path)
        return self.audio_splitter.split(audio)

    def get_embedding(self, audio_path: str) -> np.ndarray:
        """
        Generates an embedding for an audio file.

        Args:
            audio_path (str): Path to the audio file.

        Returns:
            np.ndarray: Embedding vector.
        """
        return self.audio_embedder.get_embeddings(audio_path)
    
    def get_transcription(self, audio_path: str) -> str:
        """
        Generates a transcription for an audio file.

        Args:
            audio_path (str): Path to the audio file.

        Returns:
            str: Transcription of the audio file.
        """
        return self.audio_transcriber.transcribe(audio_path)
    
            
    def check_file_type(self, audio_path: str) -> str:
        """
        Verifica si el archivo es un video (.mp4) y extrae su audio.

        Args:
            audio_path (str): Ruta del archivo de entrada.

        Returns:
            str: Ruta del archivo de audio procesado.
        """
        if audio_path.lower().endswith(".mp4"):
            video_audio = VideoLoader.load_audio_from_video(audio_path)

            # Guardar el audio extraído en formato MP3
            audio_output_path = audio_path.replace(".mp4", ".mp3")
            audio_output_path = os.path.join(self.MEDIA_DIR, os.path.basename(audio_output_path))
            video_audio.write_audiofile(audio_output_path)

            print(f"Audio extraído y guardado en: {audio_output_path}")
            return audio_output_path

        return audio_path
    
    async def get_description(self, audio_path: str) -> str:
        """
        Generates a description for a audio file.
        Args:
            audio_path (str): Path to the audio file.
        Returns:
            str: Description of the audio.
        """
        return await self.audio_describer.generate_description(audio_path)
    
