'''
Module for generating audio embeddings using Wav2Vec2-XLSR.

This script allows extracting vector representations from audio files using
Facebook's pre-trained Wav2Vec2 model. The generated embeddings can be stored
in .pkl files for later use in search or classification tasks.

Usage:
    - Instantiate the `Wav2Vec2XLSRAudioEmbedder` class.
    - Call `get_embeddings_audio(audio_path)` to get the audio embedding.
    - Use `generate_embeddings_audio_pkl(audio_path, pkl_folder)` to save the embedding to a file.

Requirements:
    - torch
    - numpy
    - librosa
    - transformers (Hugging Face)
    - pickle
    - os

Author: Marcos Infante
Date: 2024-03-04
'''

import uuid
import torch
import os
import pickle
import librosa
import numpy as np
from transformers import Wav2Vec2Model, Wav2Vec2FeatureExtractor
from src.domain.repositories.embeddings.embedding_generator import EmbeddingGenerator


class AudioEmbedder(EmbeddingGenerator):
    """
    Class for extracting audio embeddings using Wav2Vec2-XLSR.

    Attributes:
        - model_name (str): Name of the pre-trained model to use.
        - min_length (int): Minimum length of the audio in samples (default: 16000, equivalent to 1s at 16kHz).
    """
    def __init__(self, config_path:str):
        """
        Initializes the model and feature extractor.

        Args:
            model_name (str): Name of the pre-trained Hugging Face model.
            min_length (int): Minimum number of samples required in the audio.
        """
        super().__init__(config_path)
        self.feature_extractor = Wav2Vec2FeatureExtractor.from_pretrained(self._config["audio"]['model_name'])
        self.model = Wav2Vec2Model.from_pretrained(self._config["audio"]['model_name'])
        self.min_length = self._config["audio"]["min_samples"]  # Minimum in samples (16000 = 1s at 16kHz)

    def get_embeddings(self, audio_path:str):
        """
        Gets the embedding of an audio file.

        Args:
            audio_path (str): Path to the audio file.

        Returns:
            np.ndarray: Embedding vector of the audio.
        """
        audio_input = self.load_and_process(audio_path)
        inputs = self.feature_extractor(audio_input, return_tensors="pt", sampling_rate=self._config["audio"]["min_samples"])

        with torch.no_grad():
            embeddings = self.model(**inputs).last_hidden_state

        embeddings = embeddings.cpu().numpy()

        # If the embedding has more than one dimension, average over the temporal dimension
        if embeddings.ndim > 1:
            embeddings = embeddings.mean(axis=1).flatten()

        return embeddings

    def save_embeddings(self, data:dict):
        """
        Generates and saves the embedding of an audio file in a .pkl file.

        Args:
            audio_path (str): Path to the audio file.
            pkl_folder (str): Folder where the .pkl file will be saved.

        Returns:
            np.ndarray: Embedding of the audio.
        """
     
        os.makedirs(self._config["audio"]["pkl_folder"], exist_ok=True)

        unique_id = str(uuid.uuid4())
        pkl_output = os.path.join(self._config["audio"]["pkl_folder"], f"embedding_{unique_id}.pkl")
        
        with open(pkl_output, 'wb') as f:
            pickle.dump(data, f)

       

    def load_and_process(self, audio_path:str):
        """
        Loads and preprocesses an audio file.

        - Converts to mono.
        - Adjusts the sampling rate to 16kHz.
        - Normalizes the audio signal.
        - Applies padding if the audio is shorter than the required minimum.

        Args:
            audio_path (str): Path to the audio file.

        Returns:
            np.ndarray: Array with the preprocessed audio signal.
        """
        # Load audio ensuring a sampling rate of 16kHz and conversion to mono
        sr = self._config["audio"]["min_samples"]
        audio, sample_rate = librosa.load(audio_path, sr=sr, mono=True)

        # Normalize the audio
        audio = librosa.util.normalize(audio)

        # Apply padding if necessary
        if len(audio) < self.min_length:
            pad_length = self.min_length - len(audio)
            audio = np.pad(audio, (0, pad_length), mode='constant')

        return audio