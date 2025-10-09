#from typing import List
#from langchain_core.documents import Document
#from langchain_docling import DoclingLoader
#from langchain_docling.loader import ExportType
#from src.domain.repositories.loaders.loader import Loader
#
#
#
#class MarkdownLoader(Loader):
#
#    def __init__(self, config: dict):
#        self.config = config.copy()
#
#    def load(self, document_path: str) -> List[Document]:
#        """
#    Loads a Markdown document from the specified path.
#
#    Args:
#        document_path (str): Path to the .md file.
#
#    Returns:
#        List[Document]: A list containing the loaded document with metadata.
#        """ 
#        loader = DoclingLoader(
#            file_path=document_path,
#            export_type=ExportType.MARKDOWN,
#        )
#        loaded_docs = loader.load()
#
#        for doc in loaded_docs:
#            doc.metadata["extension"] = "md"
#            doc.metadata["origin"] = "local_storage"
#
#        return loaded_docs