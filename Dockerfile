# ── Stage 1: Builder ────────────────────────────────────────
# Install dependencies into the default site-packages so pip can
# detect already-installed packages across multiple install commands.
FROM python:3.12-slim AS builder

WORKDIR /build

# Install CPU-only PyTorch FIRST (saves ~3GB by avoiding CUDA).
# Then install the rest — pip sees torch is already present and skips it.
COPY requirements.txt .
RUN pip install --no-cache-dir \
    torch torchvision --index-url https://download.pytorch.org/whl/cpu && \
    pip install --no-cache-dir -r requirements.txt

# ── Stage 2: Runtime ────────────────────────────────────────
# Start fresh from a clean slim image — no build tools, no pip cache.
FROM python:3.12-slim AS runtime

WORKDIR /app

# Copy installed packages from builder
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy application code
COPY app/ ./app/

# Create directory for ChromaDB persistence (mounted as volume in production)
RUN mkdir -p /app/chroma_data

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV CHROMA_PERSIST_DIR=/app/chroma_data

# Expose the API port
EXPOSE 8000

# Health check for container orchestrators (ECS, Docker Compose)
# start-period=120s: sentence-transformers model loading takes ~60s+
HEALTHCHECK --interval=30s --timeout=10s --start-period=120s --retries=3 \
    CMD python -c "import httpx; httpx.get('http://localhost:8000/api/v1/health').raise_for_status()"

# Run the FastAPI app with uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
