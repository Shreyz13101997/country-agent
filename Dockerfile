# Country Information AI Agent - Dockerfile
# =============================================
# Production-ready Docker configuration
# 
# Build:   docker build -t country-agent .
# Run:    docker run -p 8501:8501 country-agent
# 
# Or use docker-compose for environment variables:
# docker-compose up --build

# -----------------------------------------------------------------------------
# Base Image - Python 3.12 (slim for smaller image)
# -----------------------------------------------------------------------------
FROM python:3.12-slim

# -----------------------------------------------------------------------------
# Labels for metadata
# -----------------------------------------------------------------------------
LABEL maintainer="Country Agent Team"
LABEL description="Country Information AI Agent - Production"
LABEL version="1.0.0"

# -----------------------------------------------------------------------------
# Environment Variables
# -----------------------------------------------------------------------------
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    STREAMLIT_SERVER_PORT=8501 \
    STREAMLIT_SERVER_HEADLESS=true

# -----------------------------------------------------------------------------
# Working Directory
# -----------------------------------------------------------------------------
WORKDIR /app

# -----------------------------------------------------------------------------
# Copy dependencies first (for caching)
# -----------------------------------------------------------------------------
COPY requirements.txt .

# -----------------------------------------------------------------------------
# Install dependencies with exact versions + wget for healthcheck
# -----------------------------------------------------------------------------
RUN pip install --no-cache-dir -r requirements.txt && \
    apt-get update && apt-get install -y --no-install-recommends wget && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# -----------------------------------------------------------------------------
# Copy application code
# -----------------------------------------------------------------------------
COPY . .

# -----------------------------------------------------------------------------
# Create non-root user for security
# -----------------------------------------------------------------------------
RUN useradd --create-home --shell /bin/bash appuser && \
    chown -R appuser:appuser /app

USER appuser

# -----------------------------------------------------------------------------
# Expose Streamlit port
# -----------------------------------------------------------------------------
EXPOSE 8501

HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8501')" || exit 1

CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]