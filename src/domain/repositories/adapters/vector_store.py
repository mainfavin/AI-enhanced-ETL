from abc import ABC, abstractmethod

from src.domain.config.config_loader import ConfigLoader
class VectorStoreAdapter(ABC):
    """
    Abstract base class for vector database adapters.
    """
    def __init__(self, config_path: str):
        """
        Initializes the class by loading the configuration from a YAML file.
        Args:
            config_path (str): Path to the configuration file.
        """
        self._config = ConfigLoader.load_config(config_path) #Ojo que tiene una _ porque si tuviera dos, seria privada y no podria devolver la variable. Hay que poner en la clase que llame al super "self.__config = self._config"
        
    @abstractmethod
    def connect(self):
        pass

    @abstractmethod
    def upload(self, embeddings, iteration, vect_name):
        """Uploads one embedding to the vector store."""
        pass

    @abstractmethod
    def close(self):
        pass
    
    def search_similar_vectors(self, query_vector, filters: any ,vector_type="audio", top_k=5):
        """
        Searches Qdrant for the most similar vectors.

        Args:
            query_vector (torch.Tensor or np.ndarray or list): Query vector.
            vector_type (str): Type of vector to search ('audio', 'text', or 'video').
            top_k (int): Number of top results to return.

        Returns:
            list: Search results (list of ScoredPoint objects).
        """
        return
        
        
        
        
        
        
        
        
        
        

    #TODO: Add the following methods
    def update():
        pass
    def delete():
        pass
    def retrieve():
        pass
