#from typing import List
#from langchain_core.documents import Document
#from langchain_community.document_loaders import Docx2txtLoader
#from src.domain.repositories.loaders.loader import Loader
#
#
#
#class DocxLoader(Loader):
#
#    def __init__(self, config: dict):
#        self.config = config.copy()
#
#    def load(self, document_path: str) -> List[Document]:
#        """
#    Loads a DOCX document from the specified path.
#
#    Args:
#        document_path (str): Path to the .docx file.
#
#    Returns:
#        List[Document]: A list containing the loaded document with metadata.
#        """
#        if not document_path.endswith(".docx"):
#            return []
#
#        loader = Docx2txtLoader(file_path=document_path)
#        loaded_docs = loader.load()
#
#        for doc in loaded_docs:
#            doc.metadata["extension"] = "docx"
#            doc.metadata["origin"] = "local_storage"
#
#        return loaded_docs