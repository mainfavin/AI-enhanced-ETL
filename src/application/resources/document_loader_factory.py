#import os
#from src.infraestructure.repositories.loaders.text_loaders.pdf_loader import PDFLoader
#from src.infraestructure.repositories.loaders.text_loaders.docx_loader import DocxLoader
#from src.infraestructure.repositories.loaders.text_loaders.md_loader import MarkdownLoader
#from src.infraestructure.repositories.loaders.text_loaders.directory_pdf_loader import DirectoryPDFLoader
#
#
#class DocumentLoaderFactory:
#    """
#    Factory class to provide the appropriate loader based on file extension or context.
#    """
#
#    @staticmethod
#    def get_loader(document_path: str, config: dict):
#        """
#        Returns the appropriate loader class based on the document path.
#
#        Args:
#            document_path (str): Path to the document.
#            config (dict): Loader-specific configuration.
#
#        Returns:
#            A loader instance.
#        """
#        _, ext = os.path.splitext(document_path.lower())
#
#        if ext == ".pdf" and os.path.isdir(document_path):
#            return DirectoryPDFLoader(config)
#        elif ext == ".pdf":
#            return PDFLoader(config)
#        elif ext == ".docx":
#            return DocxLoader(config)
#        elif ext in [".md", ".markdown"]:
#            return MarkdownLoader(config)
#        else:
#            raise ValueError(f"❌ Unsupported document type: {ext}")
