#from typing import List
#from langchain_core.documents import Document
#from langchain_community.document_loaders import PyPDFLoader
#from src.domain.repositories.loaders.loader import Loader
#
#
#
#class PDFLoader(Loader):
#    def __init__(self, config: dict):
#        self.config = config.copy()
#
#    def load(self, document_path: str) -> List[Document]:
#        """
#    Loads a PDF document from the specified path.
#
#    Args:
#        document_path (str): Path to the .pdf file.
#
#    Returns:
#        List[Document]: A list containing the loaded document with metadata.
#        """
#        loader = PyPDFLoader(
#            file_path=document_path,
#            extract_images=self.config.get("extract-images", False),
#            extraction_mode=self.config.get("extraction-mode", "plain")  # 'plain' or 'layout'
#        )
#        loaded_docs = loader.load()
#
#        for doc in loaded_docs:
#            doc.metadata["extension"] = "pdf"
#            doc.metadata["origin"] = "local_storage"
#
#        return loaded_docs