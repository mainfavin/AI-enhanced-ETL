# Multimedia Processing Pipeline

This repository contains a modular system for processing multimedia content (audio, video, text), generating embeddings, splitting clips, transcribing, describing, and storing vectors in a vector database (Qdrant). It was designed to be used both manually and through a **conversational assistant**, allowing non-technical users to configure the system easily.

---

## What does this repository do?

- Splits audio and video files into clips based on defined configurations.
- Automatically generates content descriptions (audio, image, video) using LLM models.
- Transcribes audio to text.
- Generates embeddings for audio, video, and text using pre-trained models.
- Stores vectors in Qdrant for vector search.
- Allows custom configuration via YAML files.

---

## How to use it

### 1. Configuration

You must define execution parameters in the configuration files located in the `config/` folder.

- `pipeline.yaml`: General configuration (input/output, active sections, paths to other YAMLs).
- `embedding_generator_config.yaml`: Defines models and parameters for embedding generation.
- `audio_splitter_config.yaml` and `video_splitter_config.yaml`: Control how clips are split.
- `audio_transcriber_config.yaml`: Defines the transcription model.
