import cv2
import base64
import time
from typing import Any, Dict, List
from langchain_core.runnables import Runnable
from langchain.prompts import ChatPromptTemplate
from src.domain.config.config_loader import ConfigLoader
from src.domain.repositories.describers.describer import Describer
from src.infraestructure.ai_services.ollama_llm_provider import OLLamaLLMProvider


class VideoDescriber(Describer):
    """
    VideoDescriber is responsible for analyzing a video and producing a human-readable summary.
    """
    def __init__(self, config_path: str,llm_provider = None):
        """
        Initializes the VideoDescriber with the provided configuration.
        """
        self.__config_path = config_path
        self.__config = ConfigLoader.load_config(config_path)
        self.__video_path = self.__config["media_path"]
        self._llm_provider = llm_provider or OLLamaLLMProvider(self.__config["llm_config"])
        self._chatmodel = self._llm_provider.get_chat_model()
        self._description_prompt = self._prepare_frame_description_prompt()
        self._summary_prompt = self._prepare_summary_prompt()

    def _prepare_frame_description_prompt(self) -> ChatPromptTemplate:
        """
        Prepares the prompt template for describing individual frames.
        """
        return ChatPromptTemplate.from_messages([
            ("system", self.__config["prompt_imagen"]),
            ("user", [
                {
                    "type": "image_url",
                    "image_url": {"url": "data:image/jpeg;base64,{base64_image}"},
                }
            ]),
        ])

    def _prepare_summary_prompt(self) -> ChatPromptTemplate:
        """
        Prepares the prompt template for summarizing the frame descriptions.
        """
        return ChatPromptTemplate.from_messages([
            ("system", self.__config["prompt_resumen_1"]),
            ("user", f"{self.__config['prompt_resumen_2']} :\n\n{{frame_descriptions}}"),
        ])

    def _extract_frames(self, ) -> List[str]:
        """
        Extracts evenly spaced frames from the video and encodes them in base64.
        """
        video_path = self.__video_path
        num_frames = self.__config.get("num_frames", 4)
        frames = []
        try:
            cap = cv2.VideoCapture(video_path)
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            if total_frames == 0:
                print(f"Error: No se pudieron leer frames del video en {video_path}")
                return frames

            indices = [int(i * total_frames / (num_frames + 1)) for i in range(1, num_frames + 1)]
            for index in sorted(indices):
                cap.set(cv2.CAP_PROP_POS_FRAMES, index)
                ret, frame = cap.read()
                if ret:
                    _, buffer = cv2.imencode(".jpg", frame)
                    base64_frame = base64.b64encode(buffer).decode("utf-8")
                    frames.append(base64_frame)
                else:
                    print(f"Advertencia: No se pudo leer el frame en el índice {index}")
            cap.release()
        except Exception as e:
            print(f"Error al procesar el video {video_path}: {e}")
        return frames

    async def _describe_frames(self, base64_frames: List[str]) -> List[str]:
        """
        Generates descriptions for a batch of base64-encoded images using the LLM.
        """

        chain: Runnable = self._description_prompt | self._chatmodel
        batch_inputs = [{"base64_image": img} for img in base64_frames]

        return await self._get_response(chain, batch_inputs)
    
    async def _generate_summary(self, descriptions: List[str]) -> str:
        """
        Generates a summary from a list of frame descriptions.
        """
        combined_text = "\n".join(descriptions)
        chain: Runnable = self._summary_prompt.partial(frame_descriptions=combined_text) | self._chatmodel
        try:
            response = await chain.ainvoke({})
            return response.content if hasattr(response, "content") else str(response)
        except Exception as e:
            return f"Error al generar el resumen: {e}"    
        
    async def _describe_video_one_call(self, base64_frames: List[str]) -> str:
        """
        Sends a single LLM call with all frames to get a full video description.
        This method is more efficient but may depend on model capabilities.
        """

        prompt_template = ChatPromptTemplate.from_messages([
            ("system", self.__config["prompt_video"]),
            ("user", [
                {
                    "type": "image_url",
                    "image_url": {"url": f"data:image/jpeg;base64,{img}"}
                } for img in base64_frames
            ])
        ])
        chain: Runnable = prompt_template | self._chatmodel

        return await self._get_response(chain, {})

    async def _get_response(self, chain: Runnable, input_data: Any) -> Any:
        """
        Executes an async call to the given chain with the provided input data.
        Handles both single (`ainvoke`) and batch (`abatch`) cases based on the input type.
    
        Args:
            chain (Runnable): The LangChain chain to execute.
            input_data (Any): Input for the chain. A list triggers abatch; dict triggers ainvoke.
    
        Returns:
            The response(s) content, or an error message if something goes wrong.
        """
        try:
            if isinstance(input_data, list):
                responses = await chain.abatch(input_data) #Describe each image independently
                return [r.content if hasattr(r, "content") else str(r) for r in responses]
            else:
                response = await chain.ainvoke(input_data) #One description for all frames
                return response.content if hasattr(response, "content") else str(response)
        except Exception as e:
            return f"❌ Error while generating response: {e}"
    
    async def generate_description(self, video_path = None ,method: str = "fast") -> str:
        """
        Executes the video description pipeline.
        Method 'detailed' = frame-by-frame descriptions + summary.
        Method 'fast' = single LLM call with all frames.
        """
        logs = []
        if video_path != None:
            self.__video_path = video_path
        t0 = time.perf_counter()

        base64_frames = self._extract_frames()
        if not base64_frames:
            return "❌ No frames could be extracted from the video."

        if method == "fast":
            # Fast one-call method
            t1 = time.perf_counter()
            result = await self._describe_video_one_call(base64_frames)
            t2 = time.perf_counter()
            logs.append(f"⚡ One-call method: {t2 - t1:.2f} s")
            total_time = t2 - t0
            logs.append(f"✅ Total time: {total_time:.2f} s")
            return "\n".join(logs) + "\n\n Video Description:\n" + result

        else:
            # Default: Detailed method
            t1 = time.perf_counter()
            descriptions = await self._describe_frames(base64_frames)
            t2 = time.perf_counter()
            logs.append(f"🧠 Frame-by-frame descriptions: {t2 - t1:.2f} s")

            labeled = [f"Frame {i+1}: {desc}" for i, desc in enumerate(descriptions)]

            t3 = time.perf_counter()
            summary = await self._generate_summary(labeled)
            t4 = time.perf_counter()
            logs.append(f"📝 Summary generation: {t4 - t3:.2f} s")

            total_time = t4 - t0
            logs.append(f"✅ Total time: {total_time:.2f} s")

            return "\n".join(logs) + "\n\n" + "\n".join(labeled) + "\n\n Summary:\n" + summary