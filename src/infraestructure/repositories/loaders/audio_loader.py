from moviepy.editor import AudioFileClip
from src.domain.repositories.loaders.loader import Loader

class AudioLoader(Loader):

    @staticmethod
    def load(audio_path: str):
        """
        Loads an audio file and converts it to a temporary WAV file.

        Args:
            audio_path (str): Path to the original audio file.

        Returns:
            tuple: Loaded AudioSegment object and its duration.
        """
        return AudioFileClip(audio_path)
       
        
       