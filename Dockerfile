# ──────────────────────────────────────────────────────────────
# Dockerfile – face-api (usa wheels prontos do dlib)           #
# ──────────────────────────────────────────────────────────────
FROM python:3.9

# Bibliotecas compartilhadas exigidas por OpenCV-headless e dlib
RUN apt-get update && \
        apt-get install -y --no-install-recommends \
        libopenblas-dev liblapack-dev libx11-6 libgl1 \
        cmake \
        build-essential \
        libboost-all-dev \
        libboost-python-dev \
        libboost-thread-dev \
        libboost-system-dev && \
        rm -rf /var/lib/apt/lists/*

# Copia requirements e instala (usará wheels do PyPI)
WORKDIR /app
COPY requirements.txt .

RUN pip install --upgrade pip setuptools wheel
RUN pip install cmake
RUN pip install dlib==19.24.2

RUN pip install --upgrade pip setuptools wheel \
    && pip install -r requirements.txt

# Copia o código da API
COPY face_api ./face_api

# Porta do Flask
EXPOSE 5000

CMD ["python", "-m", "face_api.server"]