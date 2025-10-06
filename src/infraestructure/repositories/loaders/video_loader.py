'''
Implementation of an abstract class "media loader" that loads/detects files from local storage and moves them to where they are needed. 
It's a bit redundant because MoviePy already does this, but this way I have it clear.

Requirements:
    - MoviePy

Author: Marcos Infante
Date: 2024-02-07
'''

from moviepy.editor import VideoFileClip
from src.domain.repositories.loaders.loader import Loader

class VideoLoader(Loader):
    @staticmethod
    def load(file_dir: str):
        """
        Loads a video file.
        """
        return VideoFileClip(file_dir)
    def load_audio_from_video(file_dir: str):
        """
        Loads the audio from a video file.
        Note: remember to audio.write_audiofile("path/to/audio.mp3") to work with the loaded file.
        """
        return VideoFileClip(file_dir).audio