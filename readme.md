# 🎬 Multimedia Processing Pipeline

A modular AI-powered system for processing multimedia content — including **audio, video, and text** — designed to automate embedding generation, transcription, and vector storage using **Qdrant**.  
The system can be used manually or via a **conversational assistant**, making it accessible to both technical and non-technical users.

---

## 🧩 Overview

This repository provides a complete multimedia ETL (Extract–Transform–Load) pipeline:

- 🎧 **Audio & Video Splitting** — Automatically segments media into clips based on custom configurations.  
- 🗣️ **Transcription** — Converts speech to text using models like Whisper.  
- 🧠 **Description Generation** — Uses LLMs to describe media content (audio, image, or video).  
- 🪄 **Embedding Generation** — Creates semantic embeddings for audio, video, and text.  
- 🧱 **Vector Storage** — Saves embeddings into **Qdrant** for similarity search and retrieval.  
- ⚙️ **Custom Configuration** — Fully configurable through YAML files.

---

## ⚙️ Configuration

Execution parameters are defined in YAML files under the `config/` folder:

| File | Purpose |
|------|----------|
| `pipeline.yaml` | General pipeline control: input/output paths, active modules, YAML references. |
| `embedding_generator_config.yaml` | Defines models and parameters for embedding generation. |
| `audio_splitter_config.yaml` / `video_splitter_config.yaml` | Control how clips are segmented. |
| `audio_transcriber_config.yaml` | Configures transcription models (e.g., Whisper). |

---

## 🚀 Run with Docker

### **Option 1 — Pull prebuilt image**

If you only want to run the project without rebuilding:

```bash
docker pull papimarkiss/ai-enhanced-etl:stable
docker compose up -d
```

---

### **Option 2 — Build locally**

If you want to rebuild the image (Python 3.13 + dependencies):

```bash
docker compose build
docker compose up -d
```

This will automatically start:

- **etl_app** — main ETL pipeline  
- **ollama_etl** — local LLM inference service  
- **qdrant** — vector database  

---

## 📂 Folder Structure

```
├── config/
│   ├── pipeline.yaml
│   ├── embedding_generator_config.yaml
│   ├── audio_splitter_config.yaml
│   ├── video_splitter_config.yaml
│   └── audio_transcriber_config.yaml
├── src/
│   ├── application/
│   ├── infrastructure/
│   └── domain/
├── media/
├── data/
├── requirements_docker.txt
├── docker-compose.yml
└── Dockerfile
```

---

## 🧠 Example Workflow

1. Place your multimedia files in `media/`.  
2. Configure desired parameters in `config/pipeline.yaml`.  
3. Run the system:

   ```bash
   docker compose up -d
   ```

The pipeline will:

- Extract and split media.  
- Transcribe and describe content.  
- Generate embeddings.  
- Store them in **Qdrant**.  

---

## 🐋 Docker Hub

You can pull the latest stable image directly from Docker Hub:

👉 [papimarkiss/ai-enhanced-etl](https://hub.docker.com/r/papimarkiss/ai-enhanced-etl)

---

## 📜 License

Licensed under the terms specified in the repository’s `LICENSE` file.
