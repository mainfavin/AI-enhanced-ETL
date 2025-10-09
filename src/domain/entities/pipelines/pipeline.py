
import os
import pickle
import numpy as np
import yaml


class Pipeline:
    def __init__(self, config: dict):
        pass
    def run_pipeline(self):
        pass

    def get_output_dir(self, media_path: str, base_path: str) -> str:
        """
        Retrieves the output directory for storing .

        Args:
            media_path (str): Path to the media file.

        Returns:
            str: New output directory for storing .
        """
        media_name = os.path.splitext(os.path.basename(media_path))[0]
        return os.path.join(base_path, media_name)

    def load(self, media_path: str):
        """
        Loads a media file.

        Args:
            media_path (str): Path to the media file.

        Returns:
            np.ndarray: Media data.
        """
        pass      
    def split(self, file_path: str): #TODO change to media already loaded. media: any
        """
        Splits the content into different clips
        Args:
            media_path (str): Path to the media file.
        Returns:
            dict: Dictionary containing clip paths, start times, and end times
        """
        pass

    def get_embedding(self, path: str) -> np.ndarray:
        """
        Generates an embedding for a media file.
        Args:
            media_path (str): Path to the media file.

        Returns:
            np.ndarray: Embedding vector.
        """
        pass
    
    def generate_pkl_point(self, pkl_output: str, embedding: np.ndarray, payload: dict, type: str = 'embedding') -> str:
        """
        Saves an embedding and its metadata as a pickle file.

        Args:
            pkl_output (str): Path to save the pickle file.
            embedding (np.ndarray): Embedding vector.
            payload (dict): Metadata associated with the embedding.
            type (str, optional): Type of embedding. Defaults to 'embedding'
        Returns:
            str: Path to the saved pickle file.
        """
        os.makedirs(os.path.dirname(pkl_output), exist_ok=True)
        with open(pkl_output, "wb") as f:
            pickle.dump({
                type: embedding,
                'payload': payload
            }, f)
        return pkl_output
    
    def upload_point(self, point_path: str, vect_name: str):
        """
        Uploads an embedding point to Qdrant.

        Args:
            point_path (str): Path to the pickle file containing the embedding and metadata.
            vect_name (str): Name of the vector collection in Qdrant.

        Raises:
            FileNotFoundError: If the pickle file does not exist.
            RuntimeError: If an error occurs while loading the pickle file.
        """
        if not os.path.exists(point_path):
            raise FileNotFoundError(f"Pickle file does not exist: {point_path}")

        print(f"Loading pickle file from: {point_path}")  # Debugging

        self.adapter.connect()

        # Load the pickle file
        try:
            with open(point_path, "rb") as f:
                data = pickle.load(f)
        except Exception as e:
            raise RuntimeError(f"Error loading pickle file: {e}")
        
        self.adapter.upload_to_vectorstore(data, vect_name)
          
    def ensure_existing_dir(self,media_type :str ,media_path: str, clips_path: str, embeddings_path: str):
        """
        Ensures that a directory exists.

        Args:
        media_type (str): Type of media (e.g., 'audio', 'video').
        media_path (str): Path to the media file.
        clips_path (str): Path to the clips directory.
        embeddings_path (str): Path to the embeddings directory.
        """
        # Define directories for storing audio files, clips, and embeddings
        self.MEDIA_DIR =       media_path
        self.CLIPS_DIR =         clips_path
        self.EMBEDDINGS_DIR =    embeddings_path

        # Create directories if they do not exist
        for folder in [self.MEDIA_DIR, self.CLIPS_DIR, self.EMBEDDINGS_DIR]:
            os.makedirs(folder, exist_ok=True)
        
    def validate_dimensions(self, named_vectors: dict, config: dict):
        """
        Validates that each vector in named_vectors matches its expected dimension.

        Args:
            named_vectors (dict): Dictionary of vector name to vector values.
            config (dict): Global config to extract expected sizes.

        Raises:
            ValueError: If any vector dimension doesn't match the expected size.
        """
        for name, vector in named_vectors.items():
            expected = config["embeddings"]["vector_types"].get(name, {}).get("size")
            if expected and vector.shape[0] != expected:
                raise ValueError(f"❌ Invalid dimension for {name}: expected {expected}, got {vector.shape[0]}")
            
    def _update_output_dir(self, config_path: str, new_output_dir: str):
        """
        Updates the 'output_dir' field in a YAML configuration file.

        Args:
            config_path (str): Path to the configuration YAML file.
            new_output_dir (str): New directory path for output files.
        """
        with open(config_path, 'r') as file:
            config = yaml.safe_load(file)

        config['output_dir'] = new_output_dir

        with open(config_path, 'w') as file:
            yaml.safe_dump(config, file)