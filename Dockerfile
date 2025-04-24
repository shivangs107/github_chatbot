# Stage 1: Builder (for Python dependencies)
FROM python:3.12-slim AS builder
#Creates a temporary build environment

WORKDIR /app
ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    TRANSFORMERS_CACHE=/app/cache
#PYTHONUNBUFFERED=1 -> Ensures Python output is sent directly to logs
#PIP_NO_CACHE_DIR=1 -> Disables pip cache to reduce image size
#TRANSFORMERS_CACHE=/app/cache -> Centralizes model storage

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    cmake \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# First install torch separately with --no-cache-dir
RUN pip install --user --no-cache-dir torch==2.6.0 --index-url https://download.pytorch.org/whl/cpu

# Then install other requirements
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt && \
    pip install --user --no-cache-dir sentencepiece

# Stage 2: Runtime
FROM python:3.12-slim
WORKDIR /app
ENV PATH="/root/.local/bin:${PATH}" \
    PYTHONPATH="/app" \
    TRANSFORMERS_CACHE="/app/cache"

# Copy Python dependencies from builder
COPY --from=builder /root/.local /root/.local

# Copy pre-downloaded models
COPY app/data/models /app/cache

# Copy the rest of the app
COPY . .

RUN chmod +x entrypoint.sh
ENTRYPOINT ["./entrypoint.sh"]