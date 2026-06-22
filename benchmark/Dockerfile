FROM python:3.11-slim

WORKDIR /app

# Install dependencies
RUN pip install --no-cache-dir \
    fastapi==0.115.12 \
    uvicorn==0.34.3 \
    chromadb==0.6.3 \
    sentence-transformers==3.4.1 \
    pydantic==2.11.5

# Copy service
COPY smriti_service.py .

# Pre-download the embedding model at build time (avoids cold start on first request)
RUN python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2')"

EXPOSE 8080

CMD ["python", "smriti_service.py"]
