from abc import ABC, abstractmethod
from langchain.chat_models.base import BaseChatModel

class LLMProvider(ABC):
    """
    Abstract class to define a language model provider.
    """

    @abstractmethod
    def __init__(self, config: dict, secret: str):
        """
        Initializes the provider with the necessary configuration and credentials.

        :param config: Dictionary with the provider's specific configuration.
        :param secret: Secret key or token to authenticate the provider.
        """
        self.config = config
        self.secret = secret

    @abstractmethod
    def get_chat_model(self) -> BaseChatModel:
        """
        Method to obtain the provider's chat model.

        :return: Instance of the chat model.
        """
        pass
    @abstractmethod
    def generate_response(self, messages: list) -> str:
        """
        Generates a response from a list of messages.
        """
        pass
