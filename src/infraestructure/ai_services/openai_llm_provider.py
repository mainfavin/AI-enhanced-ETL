#import os
#from src.domain.config.config_loader import ConfigLoader
#from src.domain.services.llm_provider import LLMProvider
#from langchain.chat_models.base import BaseChatModel
#from langchain_openai import AzureChatOpenAI
#
#class OpenAILLMProvider(LLMProvider):
#        
#    def __init__(self, config_path: str, secret: str = None):
#        """
#        Inicializa el proveedor de Azure OpenAI
#        """
#        self.__secret = secret or os.environ.get("OPENAI_API_KEY")
#        self.__config = ConfigLoader.load_config(config_path)
#
#        assert str(self.__config.get("API_TYPE", "")).lower() == "azure", "El modelo seleccionado no corresponde a Azure OpenAI."
#
#        
#
#    def get_chat_model(self) -> BaseChatModel:
#        """
#        Devuelve el modelo de chat basado en Azure OpenAI
#        """
#
#        openai_llm_model = AzureChatOpenAI(
#            temperature=self.__config.get("temperature", 0),
#            deployment_name=self.__config["DEPLOYMENT_MODEL_NAME"],
#            model=self.__config["MODEL_NAME"],
#            max_tokens=self.__config.get("max_tokens", 1024),
#            openai_api_type=self.__config.get("API_TYPE"), 
#            openai_api_version=self.__config["OPENAI_API_VERSION"],
#            azure_endpoint=self.__config["OPENAI_API_BASE"],
#            openai_api_key=self.__secret,
#        )
#        
#        return openai_llm_model
#
#    async def generate_response(self, model, messages: list) -> str:
#        response = await model.ainvoke(messages)
#        return response.content
