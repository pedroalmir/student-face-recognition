# ──────────────────────────────────────────────────────────────
# Dockerfile – face-api (usa wheels prontos do dlib)           #
# ──────────────────────────────────────────────────────────────
FROM hdgigante/python-opencv:4.11.0-alpine

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

RUN apt-get update && apt-get install -y cmake
RUN apt-get clean && apt-get -y update && apt-get install -y build-essential cmake libopenblas-dev liblapack-dev libopenblas-dev liblapack-dev

# Copia requirements e instala (usará wheels do PyPI)
WORKDIR /app
COPY requirements.txt .

RUN pip install --upgrade pip setuptools wheel \
    && pip install -r requirements.txt

# Copia o código da API
COPY face_api ./face_api

# Porta do Flask
EXPOSE 5000

CMD ["python", "-m", "face_api.server"]