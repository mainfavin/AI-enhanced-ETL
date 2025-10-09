import os
import uuid
import pickle
import torch
from transformers import AutoTokenizer, AutoModel
from src.domain.repositories.embeddings.embedding_generator import EmbeddingGenerator
from src.infraestructure.repositories.loaders.text_loaders.txt_loader import TxtLoader


class TextEmbedder(EmbeddingGenerator):
    """
    Class for generating text embeddings using HuggingFace Transformers.
    """

    def __init__(self, config_path: str):
        super().__init__(config_path)

        model_name = self._config["text"]["model_name"]
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModel.from_pretrained(model_name)
        self.model.eval()

    def get_embeddings(self, text_path: str):
        """
        Generates the embedding for the given text file.

        Args:
            text_path (str): Path to the text file.

        Returns:
            np.ndarray: Embedding vector.
        """
        text = self.load_and_process(text_path)
        inputs = self.tokenizer(text, return_tensors="pt", truncation=True, padding=True)
        with torch.no_grad():
            outputs = self.model(**inputs)
            embeddings = outputs.last_hidden_state.mean(dim=1).squeeze()

        return embeddings.numpy()

    def save_embeddings(self, data: dict):
        """
        Saves embeddings in a `.pkl` file.

        Args:
            data (dict): Dictionary containing "embedding" and "payload".
        """
        pkl_dir = self._config["text"]["pkl_folder"]
        os.makedirs(pkl_dir, exist_ok=True)
        pkl_output = os.path.join(pkl_dir, f"embedding_{uuid.uuid4()}.pkl")
        with open(pkl_output, 'wb') as f:
            pickle.dump(data, f)

    def load_and_process(self, text_path: str):
        """
        Loads and processes a .txt file using TxtLoader.

        Args:
            text_path (str): Path to the text file.

        Returns:
            str: Loaded text content.
        """
        try:
            loader = TxtLoader(self._config)
            docs = loader.load(text_path)
            return docs[0].page_content if docs else ""
        except Exception as e:
            print(f"Error loading text: {e}")
            return ""
