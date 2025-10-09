"""
Audio Splitter implementation.
This class divides the audio into clips and stores them in a desired folder.

Requirements:
    - MoviePy
    - tqdm
    - config_loader.py

Author: Marcos Infante
Date: 2024-02-07
"""
import os
from pydub import AudioSegment
from moviepy.editor import AudioFileClip
from pydub.silence import split_on_silence
from src.domain.repositories.splitters.splitter import Splitter
from src.infraestructure.repositories.loaders.audio_loader import AudioLoader



class AudioSplitter(Splitter):
    
    def __init__(self, config_path: str):
        """
        Initializes the AudioSplitter class with configuration settings.
        
        Args:
            config_path (str): Path to the configuration file.
        """
        super().__init__(config_path) 

    def split(self, full_audio: AudioFileClip):
        """
        Splits an audio file into smaller segments based on silence or duration.
    
        Args:
            audio_clip (AudioFileClip): Audio file to be split.
    
        Returns:
            dict: Dictionary containing segment paths, start, and end times.
        """
        os.makedirs(self._config["output_dir"], exist_ok=True)
    
        temp_audio_path = self._config["temp_audio_path"]
        full_audio.write_audiofile(temp_audio_path)

        audio, duration = self.audio_segment(temp_audio_path)
        segments = self.extract_clips(audio)
    
        clips_dict = {}  
        current_time = 0
    
        for i, segment in enumerate(segments):
            segment_path = os.path.join(self._config["output_dir"], f"segment_{i+1}.wav")
            segment.export(segment_path, format="wav")
            clips_dict[f"clip_{i+1}"] = { 
                "clip_path": segment_path,
                "start_time": current_time,
                "end_time": current_time + len(segment)
            }
            current_time += len(segment)
    
        os.remove(temp_audio_path)
    
        return clips_dict 

    def extract_clips(self, audio):
        """
        Extracts audio segments based on silence or fixed duration.

        Args:
            audio (AudioSegment): The loaded audio file.

        Returns:
            list[AudioSegment]: List of extracted audio segments.
        """
        method = self._config["method"]
        if method == "silence":
            return split_on_silence(
                audio,
                min_silence_len=self._config["min_silence_len"],
                silence_thresh=self._config["silence_thresh"]
            )
        elif method == "duration":
            clip_duration = self._config["clip_duration"]
            return [audio[i:i + clip_duration] for i in range(0, len(audio), clip_duration)]
        else:
            raise ValueError("Invalid method specified in configuration.")


    def audio_segment(self, temp_audio_path: str):
        """
        Loads a temporary audio file (must be .wav) and returns the AudioSegment object.
        """
        audio = AudioSegment.from_wav(temp_audio_path)
        return audio, len(audio)
    
    def calculate_total_clips(self, full_duration: int):
        """
        Calculates the total number of clips to be extracted.

        Args:
            full_duration (int): Duration of the full audio.
        
        Returns:
            int: Total number of clips.
        """
        part_duration = self._config["clip_duration"]
        if self._config["method"] == "duration": 
            return (full_duration // part_duration) + (1 if full_duration % part_duration > 0 else 0)
        else:
            return "Cannot calculate total clips for scilence-based splitting"  