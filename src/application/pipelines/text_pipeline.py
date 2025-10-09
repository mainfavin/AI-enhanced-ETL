import os
import uuid
import asyncio
from src.domain.config.config_loader import ConfigLoader
from src.domain.entities.pipelines.pipeline import Pipeline
from src.infraestructure.repositories.splitters.text_splitter import TextSplitter
from src.infraestructure.repositories.embeddings.text_embedding_generator import TextEmbedder
#from src.application.resources.document_loader_factory import DocumentLoaderFactory


class TextPipeline(Pipeline):
    """
    TextPipeline class for processing plain text documents:
    - Splits the document into smaller chunks.
    - Generates embeddings for each chunk.
    - Stores embeddings and metadata in .pkl format.
    
    Author: Marcos Infante
    Date: 2024-04-14
    """

    def __init__(self, config_path: str):
        """
        Initializes the text processing pipeline with configuration settings.

        Args:
            config_path (str): Path to the YAML configuration file.
        """
        self.__config = ConfigLoader.load_config(config_path)

        self.ensure_existing_dir(
            media_type="text",
            media_path=self.__config["text"]["texts_dir"],
            clips_path=self.__config["text"]["clips_dir"],
            embeddings_path=self.__config["text"]["embeddings_dir"]
        )
        self.text_splitter = TextSplitter(self.__config["text_splitter_config"])
        self.text_embedder = TextEmbedder(self.__config["embedder_config"])

    #async def run_pipeline(self):
    #    """
    #    Runs the complete text processing pipeline:
    #    1. Loads and splits the text document into chunks.
    #    2. Generates an embedding for each chunk.
    #    3. Saves each embedding and its metadata as a .pkl file.
    #    """
    #    text_path = self.__config["text"]["text_path"]
    #    file_name = os.path.splitext(os.path.basename(text_path))[0]
#
    #    clips_output_dir = self.get_output_dir(text_path, self.CLIPS_DIR)
    #    self._update_output_dir(self.__config["text_splitter_config"], clips_output_dir) #TODO: replantear esto.
    #    embeddings_output_dir = self.get_output_dir(text_path, self.EMBEDDINGS_DIR)
#
    #    print(f"📄 Processing text file: {file_name}")
#
    #    # We use the appropiate loader
    #    loader = DocumentLoaderFactory.get_loader(text_path, self.__config["text"]["config"]["text_loader_config"])
    #    documents = loader.load(text_path)
#
    #    clip_index_global = 1
    #    char_offset = 0
#
    #    # Split text into clips
    #    for doc in documents:   
    #        clips = self.split(doc.page_content)
    #        for clip_index, (clip_text, start_idx, end_idx, clip_path) in enumerate(clips, start=1):
#
    #            await self.run_from_text(
    #                text=clip_text,
    #                source_name=file_name,
    #                clip_index=clip_index_global,
    #                start_index=start_idx,
    #                end_index=end_idx,
    #                save_path=os.path.join(embeddings_output_dir, f"clip_{clip_index_global}")
    #            )

    async def run_from_text(self, 
        text: str, 
        source_name: str = "raw_text", 
        clip_index: int = None, 
        start_index: int = None, 
        end_index: int = None, 
        save_path: str = None):
        """
        Runs the pipeline from a raw text string (e.g., transcriptions, descriptions).
        
        Args:
            text (str): Raw input text.
            source_name (str): A unique identifier for this source (e.g. clip name or uuid).
        """
        print(f"🧾 Processing raw text source: {source_name}")
    
        
        #if asyncio.iscoroutine(text):
        #    text = await text
    
        embeddings_output_dir = self.get_output_dir(source_name, self.EMBEDDINGS_DIR)
    
        if not save_path:
            save_path = os.path.join(embeddings_output_dir, f"clip_{uuid.uuid4()}")
        os.makedirs(save_path, exist_ok=True)

        embedding = self.get_embedding(text)
        payload = {
            "text_source": source_name,
            "text_clip": text,
            "params": self.__config["text"]["config"]["parameters"],
            "clip_index": clip_index,
            "start_index": start_index,
            "end_index": end_index
        }

        self.generate_pkl_point(os.path.join(save_path, "text.pkl"), embedding, payload, "text")
            

    def split(self, text: str):
        """
        Splits the text file into chunks using the configured TextSplitter.

        Args:
            text (str): The text file content.

        Returns:
            list: List of (chunk_text, start_idx, end_idx)
        """
        
        return self.text_splitter.split(text)

    def get_embedding(self, text_fragment: str):
        """
        Generates an embedding from a text fragment.

        Args:
            text_fragment (str): Text chunk to embed.

        Returns:
            np.ndarray: The embedding vector.
        """
        
        return self.text_embedder.model.encode(text_fragment)

