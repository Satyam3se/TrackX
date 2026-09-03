# TrackX — User Guide

## What is TrackX?

TrackX is an AI-powered vehicle surveillance system built with Django + React. It uses **YOLOv8** for vehicle detection and **EasyOCR** for license plate recognition, with a real-time OpenStreetMap dashboard and WebSocket alerting.

---

## Architecture Overview (5 Docker containers)

| Container | Role | Port |
|-----------|------|------|
| `trackx-db` | PostgreSQL + PostGIS (spatial DB) | 5432 |
| `trackx-redis` | Redis (Celery broker + WebSocket channel layer) | 6379 |
| `trackx-web` | Django ASGI (Daphne) — REST + WS API | 8000 |
| `trackx-celery` | Celery worker (ANPR pipeline) | — |
| `trackx-frontend` | React SPA via Nginx | 3000 |

---

## 1. Prerequisites

- Docker Desktop (or Docker Engine + Docker Compose v2)
- Git
- Node.js (for local frontend dev)

---

## 2. Quick Start — Docker (Recommended)

```bash
# Clone / navigate to project
cd track-x

# Copy environment template
cp .env.example .env
# Edit .env to set DJANGO_SECRET_KEY

# Generate a secret key (run in project root):
# python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"

# Build and launch everything
docker compose up --build -d
```

### Or use the verify script:
```bash
bash scripts/docker_verify.sh
```

### Access the app:
- **Dashboard**: `http://localhost:3000`
- **REST API docs**: `http://localhost:3000/api/v1/`
- **Django Admin**: `http://localhost:3000/admin/`

---

## 3. API Endpoints

All API routes are under `/api/v1/`.

### Cameras
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/cameras/` | List all camera nodes (GeoJSON) |
| POST | `/api/v1/cameras/` | Create a camera node |
| GET | `/api/v1/cameras/{id}/` | Retrieve camera |
| PUT | `/api/v1/cameras/{id}/` | Update camera |
| DELETE | `/api/v1/cameras/{id}/` | Delete camera |

### Blacklisted Vehicles
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/blacklisted-vehicles/` | List hotlist |
| POST | `/api/v1/blacklisted-vehicles/` | Add to hotlist |
| GET | `/api/v1/blacklisted-vehicles/{id}/` | Retrieve |
| PUT | `/api/v1/blacklisted-vehicles/{id}/` | Update |
| DELETE | `/api/v1/blacklisted-vehicles/{id}/` | Remove |

### Analytics & Trajectory
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/analytics/summary/` | Fleet health stats |
| GET | `/api/v1/trajectory/{plate}/?start_date=&end_date=` | GeoJSON trajectory for a plate |

### WebSocket
Connect to `ws://localhost:3000/ws/alerts/` to receive real-time alerts when a detected plate matches the hotlist.

---

## 4. Using the Dashboard (`http://localhost:3000`)

The dashboard has three columns:

### Left Sidebar
- **Search bar**: Enter a license plate (e.g., `KDA 123A`) → SEARCH to view the vehicle's trajectory on the map + timeline
- **Target Trajectory**: Shows hit count, distance, and a chronological timeline of camera detections with OCR confidence and inter-node speed
- **Hotlist & Anomaly Feed**: Live WebSocket alerts — CRITICAL (dispatch), WARNING (review), INFO (analytics). Click **PIN TO MAP** to fly the map to the alert location

### Center Map (OpenStreetMap via MapLibre)
- Green markers = active camera nodes
- Cyan line = target vehicle trajectory
- Heatmap overlay = traffic congestion
- Click camera markers for popup details

### Right Sidebar
- **City Traffic Analytics**: Avg speed, cameras online, blacklisted count, detections today
- **Pinned Alert**: Coordinates of a pinned alert

---

## 5. ANPR Pipeline (How it Works)

```
Camera Frame → Celery Task (process_camera_frame)
                → YOLOv8 detects vehicle & crops plate
                → EasyOCR reads license text
                → DetectionLog saved to PostGIS
                → If plate matches BlacklistedVehicle → WebSocket alert broadcast
```

Key files:
- `anpr_engine/vision.py` — YOLOv8 + EasyOCR model loading and inference
- `anpr_engine/tasks.py` — Celery task orchestration
- `anpr_engine/consumers.py` — WebSocket alert consumer
- `yolov8n.pt` — Pre-trained YOLOv8 nano weights (in repo root)

---

## 6. Django Management Commands

```bash
# Run locally (requires Python + dependencies installed)
pip install -r requirements.txt

# Database migrations
python manage.py migrate

# Createsuperuser
python manage.py createsuperuser

# Run dev server
python manage.py runserver

# Run Celery worker (separate terminal)
celery -A trackx worker -l info --concurrency=2
```

---

## 7. Frontend Development (Local)

```bash
cd frontend
npm install

npm run dev       # Dev server on :5173
npm run build     # Production build
```

---

## 8. Key Models

| Model | Fields | Purpose |
|-------|--------|---------|
| `CameraNode` | camera_id, location (Point), location_name, is_active | CCTV camera registration |
| `DetectionLog` | camera, license_plate, confidence_score, captured_at, crop_image_path, speed_estimate | Historical detection records |
| `BlacklistedVehicle` | license_plate, owner_name, reason, alert_level (CRITICAL/WARNING/INFO), is_active | Hotlist for alerts |

---

## 9. Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `DJANGO_SECRET_KEY` | — | **Required** — set a strong value |
| `DJANGO_DEBUG` | `0` | Set `1` for local debug mode |
| `POSTGRES_DB` | `trackx_db` | Database name |
| `POSTGRES_USER` | `postgres` | Database user |
| `POSTGRES_PASSWORD` | `trackx_pass` | Database password |
| `REDIS_URL` | `redis://localhost:6379/0` | Redis connection URL |
| `YOLO_WEIGHTS` | `yolov8n.pt` | Path to custom YOLO weights |

---

## 10. Troubleshooting

| Problem | Fix |
|---------|-----|
| Container fails to start | Check `.env` has `DJANGO_SECRET_KEY` set |
| GDAL/GEOS import errors | Ensure `libgdal-dev` and `libgeos-dev` are installed (Linux) |
| Celery task fails with missing image | Verify `ANPR_CROP_ROOT` env var or `MEDIA_ROOT` exists |
| WebSocket not connecting | Check `VITE_WS_URL` matches `/ws/alerts/` and Daphne is running |
| Map tiles not loading | Check your internet connection (tiles load from OpenStreetMap) |
| Docker build fails | Run `docker compose build` with `--no-cache` |
