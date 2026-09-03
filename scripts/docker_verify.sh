#!/bin/bash
# ============================================================================
# TrackX — Docker verification
# Builds all images and confirms the 5 services reach a stable running state.
# ============================================================================
set -euo pipefail

cd "$(dirname "$0")/.."

echo "=== 1. Validate docker-compose.yml ==="
docker compose config --quiet

echo "=== 2. Build all images ==="
docker compose build

echo "=== 3. Launch all services in detached mode ==="
docker compose up -d

echo "=== 4. Wait for services to become healthy ==="
sleep 15
docker compose ps

echo
echo "=== 5. Service status (container_name -> status) ==="
docker compose ps --format "table {{.Name}}\t{{.Status}}"

echo
echo "=== 6. Quick API smoke test through nginx (frontend -> web) ==="
curl -sf http://localhost:3000/api/v1/analytics/summary/ && echo " [OK] API reachable"
curl -sf http://localhost:3000/ | grep -q "TrackX" && echo " [OK] SPA served"

echo
echo "=== 7. Backend logs (last 20 lines) ==="
docker compose logs web --tail 20 || true

echo
echo "All services are expected to be up. For continuous health:"
echo "  docker compose ps                                # watch status"
echo "  docker compose logs -f --tail=50 web celery      # follow logs"
