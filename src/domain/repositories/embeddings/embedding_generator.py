'''
Interface for generating embeddings from a video (expandable to other types of unstructured data).

Usage:

Requirements:
    
Author: Marcos Infante
Date: 2024-02-07
'''
from abc import ABC
from src.domain.config.config_loader import ConfigLoader


class EmbeddingGenerator(ABC):
    """
    Interface for generating embeddings from different types of data.
    """

    def __init__(self, config_path: str):
        """
        Initializes the class by loading the configuration from a YAML file.

        Args:
            config_path (str): Path to the configuration file.
        """
        self._config = ConfigLoader.load_config(config_path)
        
    def get_embeddings(self, data):
        """
        Returns the embeddings of the provided data.

        Args:
            data: Data to be processed.

        Returns:
            np.ndarray: Embedding of the data.
        """
        pass

    def save_embeddings(self, data):
        """
        Generates and saves the embeddings of the data in a .pkl file.

        Args:
            data: Data to be processed (dictionary with embedding and payload).
            pkl_folder (str): Folder where the .pkl file will be saved.

        Returns:
            None
        """
        pass

    def load_and_process(self, path: str):
        """
        Loads and preprocesses the data for processing.

        Args:
            path: Location of the data to be processed.

        Returns:
            np.ndarray: Preprocessed data.
        """
        pass