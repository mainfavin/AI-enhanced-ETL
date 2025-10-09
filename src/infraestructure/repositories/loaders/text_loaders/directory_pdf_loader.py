#from typing import List
#from langchain_core.documents import Document
#from langchain_community.document_loaders import PyPDFDirectoryLoader
#from src.domain.repositories.loaders.loader import Loader
#
#
#
#class DirectoryPDFLoader(Loader):
#    def __init__(self, config: dict):
#        self.config = config.copy()
#
#    def load(self, document_path: str) -> List[Document]:
#        """
#    Loads all PDF documents from the specified directory path.
#
#    Args:
#        document_path (str): Path to the directory containing PDF files.
#
#    Returns:
#        List[Document]: A list of loaded documents with metadata.
#        """
#        loader = PyPDFDirectoryLoader(
#            path=document_path,
#            recursive=self.config.get("recursive", False),
#            extract_images=self.config.get("extract-images", False)
#        )
#        loaded_docs = loader.load()
#
#        for doc in loaded_docs:
#            doc.metadata["extension"] = "pdf"
#            doc.metadata["origin"] = "local_storage"
#
#        return loaded_docs