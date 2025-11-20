FROM python:3.11-slim

WORKDIR /app

# Install system deps for scipy/noisereduce
RUN apt-get update && apt-get install -y \
    gcc g++ libsndfile1-dev curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python packages
RUN pip install --no-cache-dir \
    flask flask-cors \
    deepgram-sdk==3.5.0 \
    numpy scipy noisereduce

# Copy app
COPY asr_server.py .
COPY noise_sample.npy .

# Expose port
EXPOSE 6010

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:6010/health || exit 1

CMD ["python", "asr_server.py"]
