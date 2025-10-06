"""
Video Splitter implementation.
This class divides the video into clips and stores them in a desired folder.

Requirements:
    - MoviePy
    - tqdm
    - config_loader.py

Author: Marcos Infante
Date: 2024-02-07
"""

import os
from tqdm import tqdm
from moviepy.editor import VideoFileClip
from src.domain.config.config_loader import ConfigLoader
from src.domain.repositories.splitters.splitter import Splitter
from src.infraestructure.repositories.loaders.video_loader import VideoLoader




class VideoSplitter(Splitter):

    def __init__(self, config_path: str):
        """
        Initializes the class by loading the configuration from a YAML file.

        Args:
            config_path (str): Path to the configuration file.
        """
        super().__init__(config_path) # self._config = ConfigLoader.load_config("config/video_config.yaml")

    
    def split(self, full_video: VideoFileClip):
        """
        Splits the video into different clips and displays a progress bar.

        Args:
            full_video (VideoFileClip): Full video file.
        """
        
        os.makedirs(self._config["output_dir"], exist_ok=True)

        
        full_duration = full_video.duration
        total_clips = self.calculate_total_clips(full_duration)

        start_pos = 0
        clip_index = 1

        clips_dict = {}

        with tqdm(total=total_clips, desc="Splitting video", unit="clip") as pbar:
            while start_pos < full_duration:
                end_pos = min(start_pos + self._config["part_duration"], full_duration)
                
                # Extract and save clip
                clip_path = self.extract_clip(full_video, start_pos, end_pos, clip_index)

                pbar.update(1)
                pbar.set_postfix(clip=f"part_{clip_index}.mp4")

                # Update for the next clip
            
                clips_dict[f"clip_{clip_index}"] = {
                    "clip_path": clip_path,
                    "start_time": start_pos,
                    "end_time": end_pos
                }

                clip_index += 1
                start_pos = end_pos
        return clips_dict
   
    def extract_clip(self, video, start_pos: int, end_pos: int, clip_index: int):
        """
        Extracts and saves a video clip.

        Args:
            video (VideoFileClip): The video object.
            start_pos (int): Start position of the clip.
            end_pos (int): End position of the clip.
            clip_index (int): Index of the clip.
        
        Returns:
            str: Path to the saved clip.
        """
        part_name = os.path.join(self._config["output_dir"], f"part_{clip_index}.mp4")
        clip = video.subclip(start_pos, end_pos)
        clip.write_videofile(
            part_name, 
            codec=self._config["codec"], 
            temp_audiofile=self._config["temp_audiofile"], 
            remove_temp=self._config["remove_temp"], 
            audio_codec=self._config["audio_codec"],
            verbose=self._config["verbose"], 
            logger=None
        )
        return part_name
    
    def calculate_total_clips(self, full_duration: int):
        """
        Calculates the total number of clips to be extracted.

        Args:
            full_duration (int): Duration of the full video.
        
        Returns:
            int: Total number of clips.
        """
        part_duration = self._config["part_duration"]
        return (full_duration // part_duration) + (1 if full_duration % part_duration > 0 else 0)

    
