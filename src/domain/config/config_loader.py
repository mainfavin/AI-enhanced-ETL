import yaml

class ConfigLoader:
    @staticmethod
    def load_config(file_path: str):
        """Loads a YAML configuration file and returns it as a dictionary."""
        with open(file_path, "r") as file:
            return yaml.safe_load(file)