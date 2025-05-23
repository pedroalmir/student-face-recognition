# Imagem base com wheels prontos para dlib/numpy
FROM python:3.10-slim

ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

# Dependências nativas mínimas p/ dlib + OpenCV-headless
RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential cmake libopenblas-dev liblapack-dev \
        libx11-dev libgtk-3-dev \
    && rm -rf /var/lib/apt/lists/*

# Copia requisitos e instala
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copia código
COPY face_api ./face_api

# Porta do Flask
EXPOSE 5000

CMD ["python", "-m", "face_api.server"]
