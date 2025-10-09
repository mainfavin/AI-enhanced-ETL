'''
Module for audio transcription using Whisper.

This script allows converting audio into text using OpenAI's Whisper model.
It can be used to automatically generate transcriptions of audio files.

Usage:
    - Instantiate the `AudioTranscriber` class.
    - Call `transcribe(audio_path)` to get the transcription of an audio file.

Requirements:
    - whisper (OpenAI package)
    - audio in a compatible format

Author: Marcos Infante  
Date: 2025-02-25  
'''

import whisper

class AudioTranscriber:
    """
    Class for audio transcription using Whisper.

    Attributes:
        - model_name (str): Name of the Whisper model to use.
    """
    def __init__(self, model_name='base'):
        """
        Initializes the Whisper model.

        Args:
            model_name (str): Name of the pre-trained Whisper model.
        """
        self.model = whisper.load_model(model_name)

    def transcribe(self, audio_path:str) -> str:
        """
        Transcribes the audio into text.

        Args:
            audio_path (str): Path to the audio file.

        Returns:
            str: Transcribed text from the audio.
        """
        result = self.model.transcribe(audio_path)
        return result['text']