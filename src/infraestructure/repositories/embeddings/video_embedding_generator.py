'''
Video Embedding Generator with Clip4Clip

This script extracts frames from a video, processes them, and generates embeddings using the Clip4Clip model.  
Additionally, it allows generating and saving the embeddings in a `.pkl` file for later use.  
It also includes the option to generate text embeddings using a CLIP model.

What does this script do?
- Extracts frames from a video at a configurable rate.
- Preprocesses the frames to adapt them to the model.
- Generates visual embeddings with Clip4Clip and normalizes them.
- Saves the embeddings in a file for future queries.
- Allows generating text embeddings with CLIP.

Requirements:
- `torchvision` and `transformers` for image processing and embedding generation.
- `PIL` and `numpy` for image manipulation and calculations.
- `pickle` to save the generated embeddings.

Author: Marcos Infante  
Date: 2025-02-25  
'''

import os
import uuid
import torch
import pickle
import numpy as np
from PIL import Image
from src.infraestructure.repositories.loaders.video_loader import VideoLoader
from transformers import CLIPVisionModelWithProjection, CLIPProcessor, CLIPModel
from src.domain.repositories.embeddings.embedding_generator import EmbeddingGenerator
from torchvision.transforms import Compose, Resize, CenterCrop, ToTensor, Normalize, InterpolationMode

class VideoEmbedder(EmbeddingGenerator):
    """
    Class to generate video and text embeddings using Clip4Clip and CLIP.
    """

    def __init__(self,config_path:str):

        super().__init__(config_path)

        self.model = CLIPVisionModelWithProjection.from_pretrained(self._config["video"]['model_name'])
        self.processor = CLIPProcessor.from_pretrained(self._config["video"]['processor_name'] )

        self.model_text = CLIPModel.from_pretrained(self._config["video"]['processor_name'] )
        self.processor_text = CLIPProcessor.from_pretrained(self._config["video"]['processor_name'])

    
    def _preprocess(size, image):
        """
        Applies transformations to an image to make it compatible with the model.

        Steps:
        - Resizes the image to the specified size.
        - Crops the image to the center.
        - Converts the image to RGB.
        - Normalizes the pixel values.

        Args:
            size (int): Size to resize the image to.
            image (PIL.Image): Image to process.

        Returns:
            torch.Tensor: Transformed image ready for the model.

        Note:
        Values of mean and std are sourced from,      
        https://github.com/openai/CLIP/blob/main/clip/clip.py line 85, 
        they are the values used by openAI on Clip which is the model where Clip4Clip is based ,also this paper was mentioned https://arxiv.org/pdf/2103.00020

        """
        transform = Compose([
            Resize(size, interpolation=InterpolationMode.BICUBIC),
            CenterCrop(size),
            lambda img: img.convert("RGB"), # Admits RGB and HSV
            ToTensor(),
            Normalize((0.48145466, 0.4578275, 0.40821073), (0.26862954, 0.26130258, 0.27577711)),
        ])
        return transform(image)

 
    def load_and_process(self, video_path:str):
        """
        Extracts frames from a video and processes them to generate embeddings.

        Args:
            video_path (str): Path to the video file.
            frame_rate (float): How many frames per second to extract.
            size (int): Size of the frames for the model.

        Returns:
            torch.Tensor: Tensor with the processed frames.
        """
        clip = VideoLoader.load(video_path)
        frame_rate = self._config["video"]["frame_rate"]
        size = self._config["video"]["size"]
        duration = clip.duration  # Total duration in seconds
        interval = 1.0 / frame_rate  # Interval between frames

        # Calculates the times at which frames will be extracted
        timestamps = np.arange(0, duration, interval)

        images = []
        for t in timestamps:
            frame = clip.get_frame(t)  
            pil_image = Image.fromarray(frame)
            processed_image = VideoEmbedder._preprocess(size, pil_image)
            images.append(processed_image)

        clip.close()

        video_frames = torch.stack(images)
        return video_frames

   
    def get_embeddings(self, video_path:str):
        """
        Generates embeddings for a sequence of frames using Clip4Clip.

        Args:
            video_frames (torch.Tensor): Tensor of processed images.

        Returns:
            np.ndarray: Normalized video embedding as a NumPy array.
        """
        
        model = self.model
        model.eval()

        video_frames = VideoEmbedder.load_and_process(self,video_path) 

      
        with torch.no_grad():
            visual_output = model(video_frames)
            visual_output = visual_output["image_embeds"]

            # Normalization of the embeddings
            visual_output = visual_output / visual_output.norm(dim=-1, keepdim=True) 
            visual_output = torch.mean(visual_output, dim=0)
            visual_output = visual_output / visual_output.norm(dim=-1, keepdim=True)

        return visual_output.cpu().numpy()

    
    def save_embeddings(self, data: dict):
        """
        Generates and saves video embeddings in a `.pkl` file.

        Args:
            data (dict): Dictionary with the embedding ("embedding") and the payload ("paload")
            
        Returns:
            None
        """
        os.makedirs(self._config["video"]["pkl_folder"], exist_ok=True)

        unique_id = str(uuid.uuid4())
        pkl_output = os.path.join(self._config["video"]["pkl_folder"], f"embedding_{unique_id}.pkl")
        with open(pkl_output, 'wb') as f:
            pickle.dump(data, f)

        #print(f"✅ Embeddings successfully saved in '{pkl_output}'.")


   
    def generate_text_embedding(self, text):
        """
        Generates an embedding for a text string using CLIP.
        Args:
            text (str): Text to convert into an embedding.
        Returns:
            np.ndarray: Embedding generated from the text.
        """
        self.load_model()
        inputs = self.processor(text=text, return_tensors="pt")
        with torch.no_grad():
            text_features = self.model.get_text_features(**inputs)
        return text_features.squeeze().numpy()
    

