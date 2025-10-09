"""
This module contains the abstract class Splitter, which is the base class for all splitters.

Requirements:
    - MoviePy
    - tqdm
    - config_loader.py

Author: Marcos Infante
Date: 2024-02-07
"""

from abc import ABC
from src.domain.config.config_loader import ConfigLoader



class Splitter(ABC):

    def __init__(self, config_path: str):
        """
        Initializes the class by loading the configuration from a YAML file.

        Args:
            config_path (str): Path to the configuration file.
        """
        self._config = ConfigLoader.load_config(config_path)

    
    def split(self, full_file: any): 
        """
        Splits the content into different clips and displays a progress bar.

        Args:
            full_file (any): Full media file.
        """
        pass

   
    def extract_clip(self, media: any, start_pos: int, end_pos: int, clip_index: int):
        """
        Extracts and saves a media clip.

        Args:
            media: The media object.
            start_pos (int): Start position of the clip.
            end_pos (int): End position of the clip.
            clip_index (int): Index of the clip.
        
        Returns:
            str: Path to the saved clip.
        """
        pass
    
    def calculate_total_clips(self, full_duration: int):
        """
        Calculates the total number of clips to be extracted.

        Args:
            full_duration (int): Duration of the full media.
        
        Returns:
            int: Total number of clips.
        """
        pass

    
