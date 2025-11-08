# docker/Dockerfile
FROM python:3.10-slim

ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y \
    build-essential \
    libgl1 \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    v4l-utils \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copier code
COPY app /app

# Installer dépendances
RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir -r /app/requirements.txt
# Installer eventlet séparément si pas dans requirements
RUN pip install eventlet

# Dossiers persistants
RUN mkdir -p /data /models /alerts /logs /visualizations

EXPOSE 5000

CMD ["python", "/app/main.py"]
