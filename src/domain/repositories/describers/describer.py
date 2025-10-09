from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from langchain_core.runnables import Runnable
from langchain.prompts import ChatPromptTemplate


class Describer(ABC):
    @abstractmethod
    def generate_description(self, data: Optional[Dict[str, str]] = None) -> str:
        """
     Abstract method to generate a description of multimedia content.
     :param data: A dictionary with relevant data, either embeddings or audio transcription.
     :return: The generated description as a string.
     """
        pass

 