import os
from typing import List
from src.domain.repositories.loaders.loader import Loader


class TxtLoader(Loader):
    def __init__(self, config: dict):
        self.config = config.copy()

    def load(self, document_path: str) -> List[dict]:
        """
        Loads a plain text document from the specified path.

        Args:
            document_path (str): Path to the .txt file.

        Returns:
            List[dict]: A list with one dict containing the content and metadata.
        """
        if not document_path.endswith(".txt"):
            return []

        if not os.path.exists(document_path):
            raise FileNotFoundError(f"File not found: {document_path}")

        with open(document_path, "r", encoding="utf-8") as f:
            content = f.read()

        return [{
            "page_content": content,
            "metadata": {
                "extension": "txt",
                "origin": "local_storage",
                "source": document_path
            }
        }]