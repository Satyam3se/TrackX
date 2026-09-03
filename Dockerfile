# ============================================================================
# TrackX — Backend (Django + GeoDjango + Celery)
# ============================================================================
FROM python:3.10-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    # Compiler include paths so GDAL Python bindings compile/link cleanly
    CPLUS_INCLUDE_PATH=/usr/include/gdal \
    C_INCLUDE_PATH=/usr/include/gdal

# System deps: PostGIS/GeoDjango, GDAL, OpenCV/easyocr, video, init tooling
RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential \
        libpq-dev \
        gdal-bin \
        libgdal-dev \
        python3-gdal \
        libgl1 \
        libglib2.0-0 \
        ffmpeg \
        curl \
    && rm -rf /var/lib/apt/lists/*

# Explicit GDAL runtime lookup (matching the version installed by apt)
ENV GDAL_LIBRARY_PATH=/usr/lib/x86_64-linux-gnu/libgdal.so \
    GEOS_LIBRARY_PATH=/usr/lib/x86_64-linux-gnu/libgeos_c.so

WORKDIR /app

# Install Python dependencies first for better layer caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the project source
COPY . .

# Web entrypoint (migrate + seed + launch Daphne)
COPY docker/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Expose the ASGI/Daphne application port
EXPOSE 8000

# Default command (overridden by docker-compose per-service)
CMD ["daphne", "-b", "0.0.0.0", "-p", "8000", "trackx.asgi:application"]
