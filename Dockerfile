# ── Stage: runtime ─────────────────────────────────────────────────────────
FROM python:3.11-slim

LABEL maintainer="toomsey"
LABEL description="SenseHat Monitor — reads sensors, stores to SQLite, pushes to Blynk"

# System deps: gcc needed by some pip packages; sense-hat needs libc headers
RUN apt-get update && apt-get install -y --no-install-recommends \
        gcc \
        libc6-dev \
    && rm -rf /var/lib/apt/lists/*

# Working directory inside the container
WORKDIR /app

# Install Python dependencies first (layer-caching: changes to code
# won't invalidate this layer unless requirements.txt changes)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source
COPY app.py          .
COPY flask_app.py    .
COPY sensor.py       .
COPY database.py     .
COPY blynk_client.py .

# Ensure the DB directory exists inside the container.
# In production, mount a host volume here so data persists across restarts:
#   docker run -v /home/toomsey/assignement:/home/toomsey/assignement ...
RUN mkdir -p /home/toomsey/assignement

# Expose Flask API port
EXPOSE 5000

# Environment defaults — override at runtime via --env-file or -e flags
ENV DB_PATH=/home/toomsey/assignement/sense_data.db \
    POLL_INTERVAL=30 \
    TEMP_HOT=35 \
    TEMP_COLD=20 \
    TEMP_CORRECTION=-5 \
    BLYNK_SERVER=https://blynk.cloud \
    BLYNK_AUTH_TOKEN=pSbVAjTPl9HX_ObS3Pe3WzlsBaN5TK1O \
    BLYNK_TIMEOUT=5

# Run the application
CMD ["python", "app.py"]
