# ── Base ──────────────────────────────────────────────────────────────────────
FROM python:3.11-slim

# System deps for MoviePy / ffmpeg / imagemagick
RUN apt-get update && apt-get install -y \
    ffmpeg \
    imagemagick \
    fonts-dejavu-core \
    && rm -rf /var/lib/apt/lists/*

# Unlock ImageMagick policy so MoviePy TextClip works
RUN sed -i 's/rights="none" pattern="@\*"/rights="read|write" pattern="@*"/' \
    /etc/ImageMagick-6/policy.xml || true

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Default command — run the full pipeline
CMD ["python", "run_pipeline.py"]
