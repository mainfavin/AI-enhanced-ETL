import time

import whisper
from typing import Optional
from langchain_core.runnables import Runnable
from langchain.prompts import ChatPromptTemplate
from src.domain.config.config_loader import ConfigLoader
from src.domain.repositories.describers.describer import Describer
from src.infraestructure.ai_services.ollama_llm_provider import OLLamaLLMProvider
from src.infraestructure.repositories.transcribers.audio_transcriber import AudioTranscriber


class AudioDescriber(Describer):
    """
    AudioDescriber generates a textual description from an audio file:
    1. Transcribes the audio using Whisper.
    2. Describes the content using an LLM.
    """

    def __init__(self, config_path: str, llmprovider):
        self.__config_path = config_path
        self.__config = ConfigLoader.load_config(config_path)
        self.__audio_path = self.__config["media_path"]
        self._llm_provider = llmprovider or OLLamaLLMProvider(self.__config["llm_config"])
        self._chatmodel = self._llm_provider.get_chat_model()
        self._description_prompt = self._prepare_description_prompt()

    def _prepare_description_prompt(self) -> ChatPromptTemplate:
        """
        Creates the prompt used to generate a description from transcript.
        """
        return ChatPromptTemplate.from_messages([
            ("system", self.__config["prompt_audio"]),
            ("user", "{transcript}")
        ])

    def _transcribe_audio(self, audio_path: str) -> Optional[str]:
        """
        Transcribes the audio file using Whisper.
        """
        try:
            transcriber = AudioTranscriber()
            text = transcriber.transcribe(audio_path)
            return text
            
        except Exception as e:
            print(f"❌ Error en transcripción: {e}")
            return None

    async def _generate_description(self, transcript: str) -> str:
        """
        Uses an LLM to generate a description from the transcript.
        """
        chain: Runnable = self._description_prompt.partial(transcript=transcript) | self._chatmodel
        try:
            response = await chain.ainvoke({})
            return response.content if hasattr(response, "content") else str(response)
        except Exception as e:
            raise RuntimeError(f"❌ Error al generar la descripción: {e}")

    async def generate_description(self, audio_path = None) -> str:
        """
        Full pipeline: transcribe audio → generate description → report performance.
        """
        logs = []
        if audio_path!= None:
            self.__audio_path = audio_path
        t0 = time.perf_counter()

        # 1. Transcripción
        t1 = time.perf_counter()
        transcript = self._transcribe_audio(self.__audio_path)
        t2 = time.perf_counter()
        logs.append(f"🔊 Transcripción: {t2 - t1:.2f} s")

        if not transcript:
            return "No se pudo obtener una transcripción válida del audio."

        # 2. Descripción
        try:
            t3 = time.perf_counter()
            description = await self._generate_description(transcript)
            t4 = time.perf_counter()
            logs.append(f"🧠 Descripción generada: {t4 - t3:.2f} s")
        except Exception as e:
            return str(e)

        total_time = time.perf_counter() - t0
        logs.append(f"✅ Tiempo total: {total_time:.2f} s")

        return "\n".join(logs) + f"\n\nTranscripción:\n{transcript}\n\nDescripción:\n{description}"
