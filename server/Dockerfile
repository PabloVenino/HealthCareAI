FROM python:3.12-slim

WORKDIR /app

# Install system dependencies if necessary (e.g. for building some python packages)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY server/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the server directory and data directory
COPY server/ ./server/
COPY data/ ./data/

# Environment variables
ENV HOST=0.0.0.0
ENV PORT=8000
ENV PYTHONPATH=/app

EXPOSE 8000

CMD ["uvicorn", "server.main:app", "--host", "0.0.0.0", "--port", "8000"]
