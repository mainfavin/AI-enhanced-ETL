# 🧠 Multimedia Processing Pipeline

Este repositorio contiene un sistema modular para procesar contenido multimedia (audio, vídeo, texto), generar embeddings, dividir clips, transcribir, describir y almacenar vectores en una base de datos vectorial (Qdrant). Fue diseñado para ser usado tanto de forma manual como a través de un **asistente conversacional**, facilitando que usuarios sin conocimientos técnicos puedan configurar el sistema.

---

## 🚀 ¿Qué hace este repositorio?

- Divide archivos de audio y vídeo en clips según configuraciones definidas.
- Genera descripciones automáticas de contenido (audio, imagen, vídeo) usando modelos LLM.
- Transcribe audio a texto.
- Genera embeddings para audio, vídeo y texto con modelos preentrenados.
- Almacena los vectores en Qdrant para búsquedas vectoriales.
- Permite una configuración personalizada mediante YAMLs.

---

## 🛠 ¿Cómo se usa?

### 1. Configuración
Debes definir los parámetros de ejecución en los siguientes archivos de configuración, ubicados en la carpeta `config/`.

- `pipeline.yaml`: Configuración general (entrada/salida, secciones activas, rutas a otros YAMLs).
- `embedding_generator_config.yaml`: Define modelos y parámetros para la generación de embeddings.
- `audio_splitter_config.yaml` y `video_splitter_config.yaml`: Controlan la división de clips.
- `audio_transcriber_config.yaml`: Define el modelo de transcripción.
- `describer_config.yaml`: Configura prompts y modelo para descripción automática del contenido.
