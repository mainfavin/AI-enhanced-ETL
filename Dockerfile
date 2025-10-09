# ===== Stage 1: Build =====
FROM python:3.13-slim AS builder
WORKDIR /app

COPY requirements_docker.txt .

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc g++ ffmpeg libsndfile1 git \
    libgl1 libglib2.0-0 libsm6 libxext6 libxrender1 \
 && pip install --upgrade pip \
 && pip install --no-cache-dir -r requirements_docker.txt \
 && apt-get remove -y gcc g++ \
 && apt-get autoremove -y && rm -rf /var/lib/apt/lists/*

# ===== Stage 2: Runtime =====
FROM python:3.13-slim
WORKDIR /app

COPY --from=builder /usr/local /usr/local
COPY . .

ENV HF_HOME=/root/.cache/huggingface \
    PYTHONUNBUFFERED=1


RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg libsndfile1 git \
    libgl1 libglib2.0-0 libsm6 libxext6 libxrender1 \
 && rm -rf /var/lib/apt/lists/*
CMD ["python", "__main__.py"]
