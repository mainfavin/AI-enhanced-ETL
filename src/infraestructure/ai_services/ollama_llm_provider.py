import os
from langchain_ollama import ChatOllama
from langchain.chat_models.base import BaseChatModel
from src.domain.config.config_loader import ConfigLoader
from src.domain.services.llm_provider import LLMProvider


class OLLamaLLMProvider(LLMProvider):
    def __init__(self, config_path: str, secret: str = None):
        
        self.__secret = secret if secret else os.environ.get("LLM_API_KEY")        
        self.__config = ConfigLoader.load_config(config_path)
        assert str(self.__config.get("API_TYPE", "")).lower() == "ollama", "El modelo seleccionado no " \
                                                                        "pertenece a Ollama"

    def get_chat_model(self) -> BaseChatModel:
        """
        Provides an Ollama chat LLM model instance.

        Configuration file should look like this:
          API_TYPE: str
          MODEL: str
          max_tokens: int
          temperature: int
          timeout: int
          max_retries: int

        Returns
        -------
        BaseChatModel:
            LangChain Large Language Model
        """
        
        # In order to use this model you will need to:
        #   1. Download Ollama: https://ollama.com/
        #   2. Open Ollama terminal and run 'ollama run <MODEL>'
        #   3. Execute your code
        # As an alternative option to steps 1 and 2, you can download Ollama's docker image an setup the model from there:
        #   Tutorial:   https://ollama.com/blog/ollama-is-now-available-as-an-official-docker-image
        #   Docker command for CPU-only image: docker run -d -v ollama:/root/.ollama -p 11434:11434 --name ollama ollama/ollama
        # Some other useful links: https://medium.com/@garysvenson09/how-to-list-all-models-in-ollama-for-langchain-tutorial-786cb14298a8

        llm = ChatOllama(
            model=self.__config["MODEL_NAME"],
            temperature=self.__config["temperature"],
            max_tokens=self.__config["max_tokens"],
            timeout=self.__config["timeout"],
            max_retries=self.__config["max_retries"],
           
        )
        return llm

  
    async def generate_response(self, model, messages: list) -> str:
        response = await model.ainvoke(messages)
        return response.content