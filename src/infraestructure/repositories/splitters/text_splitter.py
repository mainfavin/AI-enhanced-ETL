import os
import uuid
from src.domain.repositories.splitters.splitter import Splitter

class TextSplitter(Splitter):
    def __init__(self, config_path: str):
        super().__init__(config_path)

        self.chunk_size = self._config["chunk_size"]
        self.chunk_overlap = self._config["chunk_overlap"]
        self.output_dir = self._config["output_dir"]
        os.makedirs(self.output_dir, exist_ok=True)

    def _split_text(self, text: str):
        """
        Split text into chunks of size `chunk_size` with overlap `chunk_overlap`.
        """
        step = self.chunk_size - self.chunk_overlap
        chunks = []

        for i in range(0, len(text), step):
            chunk = text[i:i + self.chunk_size]
            if not chunk.strip():
                continue
            chunks.append((chunk, i, i + len(chunk)))

        return chunks

    def split(self, full_text: str):
        chunks = self._split_text(full_text)
        saved_chunks = []

        for idx, (chunk_text, start, end) in enumerate(chunks, start=1):
            clip_filename = f"clip_{idx}_{uuid.uuid4()}.txt"
            clip_path = os.path.join(self.output_dir, clip_filename)

            with open(clip_path, "w", encoding="utf-8") as f:
                f.write(chunk_text)

            saved_chunks.append((chunk_text, start, end, clip_path))

        return saved_chunks

    def calculate_total_clips(self, full_length: int):
        effective_step = self.chunk_size - self.chunk_overlap
        return (full_length // effective_step) + (1 if full_length % effective_step > 0 else 0)
