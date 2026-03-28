<<<<<<< HEAD
FROM python:3.11-slim

WORKDIR /app

# Ensure apt-get doesn't hang invisibly asking for keyboard input
ENV DEBIAN_FRONTEND=noninteractive

# Force Python to stream logs instantly to the Hugging Face console
ENV PYTHONUNBUFFERED=1

# Install necessary system dependencies
RUN echo "🚀 DOCKER BUILD HAS OFFICIALLY STARTED 🚀" && apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Pre-install CPU-only PyTorch to prevent downloading massive CUDA (GPU) binaries
RUN pip install -v --no-cache-dir --progress-bar off torch torchvision torchaudio \
    --index-url https://download.pytorch.org/whl/cpu

# Copy and install Python dependencies
COPY requirements.txt .
RUN pip install -v --no-cache-dir --progress-bar off -r requirements.txt

# Copy the rest of the application code
COPY . .

EXPOSE 7860

# Start the FastAPI application via uvicorn
CMD ["uvicorn", "server.server:app", "--host", "0.0.0.0", "--port", "7860"]
=======
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libxcb1 \
  && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "server.server:app", "--host", "0.0.0.0", "--port", "8000"]
>>>>>>> fe589f9 (replaced docling with llama-cloud)
