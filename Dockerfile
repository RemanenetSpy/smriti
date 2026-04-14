FROM python:3.11-slim

WORKDIR /app

# Install build dependencies for ChromaDB/SQLite
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Use PORT env variable (Render injects this), fallback to 7860 for HF Spaces
ENV PORT=7860
EXPOSE ${PORT}

CMD ["sh", "-c", "python -m uvicorn api.main:app --host 0.0.0.0 --port ${PORT}"]
