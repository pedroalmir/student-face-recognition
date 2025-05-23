# ──────────────────────────────────────────────────────────────
# Dockerfile – face-api (usa wheels prontos do dlib)           #
# ──────────────────────────────────────────────────────────────
FROM python:3.11-slim

# Evita prompts do apt
ENV DEBIAN_FRONTEND=noninteractive \
    PIP_NO_CACHE_DIR=1 \
    PYTHONUNBUFFERED=1

# Bibliotecas compartilhadas exigidas por OpenCV-headless e dlib
RUN apt-get update && apt-get install -y --no-install-recommends \
      libopenblas-dev liblapack-dev libx11-6 libgl1 \
      cmake build-essential libboost-all-dev \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Copia requirements e instala (usará wheels do PyPI)
WORKDIR /app
COPY requirements.txt .

RUN pip install -U pip wheel cmake

RUN pip install --upgrade pip setuptools wheel \
    && pip install -r requirements.txt

# Copia o código da API
COPY face_api ./face_api

# Porta do Flask
EXPOSE 5000

CMD ["python", "-m", "face_api.server"]