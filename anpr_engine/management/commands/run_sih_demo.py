"""
SIH Live Demo — automated management command.

Simulates a target vehicle driving through 5 sequential camera checkpoints
over a configurable window, writes DetectionLog rows, seeds the hotlist,
and triggers a real-time WebSocket hotlist alert on the final checkpoint.

Usage:
    python manage.py run_sih_demo [--plate PLATE] [--checkpoints N]
                                  [--window-minutes M] [--speed KMH]

Examples:
    python manage.py run_sih_demo                          # defaults below
    python manage.py run_sih_demo --plate "KDA 123A" --checkpoints 5 --window-minutes 10
    python manage.py run_sih_demo --plate "KCX 882B" --checkpoints 3 --window-minutes 6
"""
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.contrib.gis.geos import Point
from django.core.management.base import BaseCommand
from django.utils import timezone

from anpr_engine.models import BlacklistedVehicle, CameraNode, DetectionLog

# ---------------------------------------------------------------------------
# Default camera grid (matches seed_trackx.py)
# ---------------------------------------------------------------------------
CAMERA_GRID = [
    {"camera_id": "CAM-042", "location_name": "Ring Rd / ITO Junction", "lon": 77.2410, "lat": 28.6289},
    {"camera_id": "CAM-118", "location_name": "Rajghat Flyover",      "lon": 77.2498, "lat": 28.6412},
    {"camera_id": "CAM-233", "location_name": "Kashmere Gate ISBT",   "lon": 77.2295, "lat": 28.6673},
    {"camera_id": "CAM-501", "location_name": "GT Karnal Road",       "lon": 77.2011, "lat": 28.6905},
    {"camera_id": "CAM-612", "location_name": "Azadpur Mandi",        "lon": 77.1758, "lat": 28.7078},
]

HOTLIST_SEED = {
    "license_plate": "DL 3C AF 9021",
    "owner_name": "Arjun Mehta",
    "reason": "Reported stolen vehicle; involved in hit and run",
    "alert_level": "CRITICAL",
}

BLACKLIST_SEEDS = [
    {
        "license_plate": "DL 3C AF 9021",
        "owner_name": "Arjun Mehta",
        "reason": "Reported stolen vehicle; involved in hit and run",
        "alert_level": "CRITICAL",
    },
    {
        "license_plate": "HR 26 DQ 4412",
        "owner_name": "Ravi Khanna",
        "reason": "Repeat traffic violations in a restricted zone",
        "alert_level": "WARNING",
    },
]

# ---------------------------------------------------------------------------
# Command
# ---------------------------------------------------------------------------

class Command(BaseCommand):
    help = (
        "Full SIH live-demo sequence: seed cameras + hotlist, simulate a target "
        "vehicle through N checkpoints over M minutes, and fire a real-time "
        "WebSocket hotlist alert on the last checkpoint."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--plate", default=HOTLIST_SEED["license_plate"],
            help="Target license plate (must match a BlacklistedVehicle for the alert).",
        )
        parser.add_argument(
            "--checkpoints", type=int, default=5,
            help="Number of sequential camera checkpoints (1–5).",
        )
        parser.add_argument(
            "--window-minutes", type=int, default=10,
            help="Total simulation window in minutes.",
        )
        parser.add_argument(
            "--speed", type=float, default=30.0,
            help="Simulated inter-checkpoint speed in km/h (default: 30.0).",
        )

    # ------------------------------------------------------------------
    # Pipeline
    # ------------------------------------------------------------------

    def handle(self, *args, **options):
        plate = options["plate"]
        checkpoints = max(1, min(options["checkpoints"], len(CAMERA_GRID)))
        window = max(1, options["window_minutes"])
        speed = options["speed"]
        now = timezone.now()

        self.stdout.write(self.style.NOTICE("=" * 64))
        self.stdout.write(self.style.NOTICE("  TRACKX — SIH LIVE DEMO SEQUENCE"))
        self.stdout.write(self.style.NOTICE("=" * 64))
        self.stdout.write(f"  Plate           : {plate}")
        self.stdout.write(f"  Checkpoints     : {checkpoints}")
        self.stdout.write(f"  Window          : {window} min")
        self.stdout.write(f"  Inter-node speed: {speed} km/h")
        self.stdout.write(self.style.NOTICE("=" * 64))

        # ---- Step 1 : Seed cameras + hotlist ----
        cameras = self._seed_cameras()
        vehicle = self._seed_hotlist(plate)
        self.stdout.write(self.style.SUCCESS(f"[1/4] Seeded {len(cameras)} CameraNodes + BlacklistedVehicle '{plate}' ({vehicle.alert_level})"))

        # ---- Step 2 : Wipe old detection logs for this plate ----
        cleared, _ = DetectionLog.objects.filter(license_plate=plate).delete()
        self.stdout.write(self.style.SUCCESS(f"[2/4] Cleared {cleared} old DetectionLog(s) for '{plate}'"))

        # ---- Step 3 : Simulate checkpoint drive ----
        interval_sec = (window * 60) / max(checkpoints, 1)
        hit_logs = []

        for idx in range(checkpoints):
            camera = cameras[idx]
            captured_at = now + timezone.timedelta(seconds=idx * interval_sec)
            confidence = round(0.85 + (idx * 0.02), 2)          # rising confidence as vehicle approaches
            crop_path = f"crops/{camera.camera_id}/{plate}_{captured_at:%Y%m%d%H%M%S}.jpg"

            log = DetectionLog.objects.create(
                camera=camera,
                license_plate=plate,
                confidence_score=confidence,
                captured_at=captured_at,
                crop_image_path=crop_path,
                speed_estimate=speed,
            )
            hit_logs.append((idx + 1, camera, log))
            self.stdout.write(
                self.style.NOTICE(
                    f"  [{idx+1}/{checkpoints}] {camera.camera_id} — "
                    f"{camera.location_name}  ({captured_at.strftime('%H:%M:%S')})  "
                    f"OCR {int(confidence*100)}%"
                )
            )
        self.stdout.write(self.style.SUCCESS(f"[3/4] Created {len(hit_logs)} DetectionLog rows"))

        # ---- Step 4 : Fire hotlist alert on the LAST checkpoint ----
        last_idx, last_camera, last_log = hit_logs[-1]
        alert_payload = self._fire_hotlist_alert(plate, vehicle, last_camera, last_log)

        self.stdout.write(self.style.SUCCESS(
            f"[4/4] Alert fired on checkpoint {last_idx}/{checkpoints} "
            f"({last_camera.location_name})"
        ))
        self.stdout.write(self.style.SUCCESS(
            "  Payload -> channel_layer.group_send('surveillance_alerts', ...)"
        ))

        # ---- Summary ----
        self.stdout.write(self.style.NOTICE("=" * 64))
        self.stdout.write(self.style.SUCCESS(
            "  DEMO COMPLETE -- Open http://localhost:3000 to view the live alert."
        ))
        self.stdout.write(self.style.SUCCESS(
            f"  Alert payload: {alert_payload}"
        ))
        self.stdout.write(self.style.NOTICE("=" * 64))

    # ------------------------------------------------------------------
    # Steps
    # ------------------------------------------------------------------

    def _seed_cameras(self):
        cameras = []
        for seed in CAMERA_GRID:
            camera, _ = CameraNode.objects.update_or_create(
                camera_id=seed["camera_id"],
                defaults={
                    "location_name": seed["location_name"],
                    "location": Point(seed["lon"], seed["lat"], srid=4326),
                    "is_active": True,
                },
            )
            cameras.append(camera)
        return cameras

    def _seed_hotlist(self, plate):
        """Seed the full default hotlist, then ensure *plate* is on it."""
        for seed in BLACKLIST_SEEDS:
            BlacklistedVehicle.objects.update_or_create(
                license_plate=seed["license_plate"],
                defaults={
                    "owner_name": seed["owner_name"],
                    "reason": seed["reason"],
                    "alert_level": seed["alert_level"],
                    "is_active": True,
                },
            )
        vehicle, _ = BlacklistedVehicle.objects.update_or_create(
            license_plate=plate,
            defaults={
                "owner_name": HOTLIST_SEED["owner_name"],
                "reason": HOTLIST_SEED["reason"],
                "alert_level": HOTLIST_SEED["alert_level"],
                "is_active": True,
            },
        )
        return vehicle

    def _fire_hotlist_alert(self, plate, vehicle, camera, log):
        """Query the active hotlist and broadcast via Redis Channels if matched."""
        matched = BlacklistedVehicle.objects.filter(
            license_plate__iexact=plate,
            is_active=True,
        ).first()

        if not matched:
            self.stdout.write(self.style.WARNING(
                "  [!] No active BlacklistedVehicle matched -- no alert broadcast."
            ))
            return None

        alert_payload = {
            "type": "send_alert_notification",
            "alert_level": matched.alert_level,
            "plate": plate,
            "owner": matched.owner_name,
            "reason": matched.reason,
            "camera": camera.location_name,
            "coordinates": [camera.location.x, camera.location.y],
            "timestamp": str(log.captured_at),
        }

        try:
            channel_layer = get_channel_layer()
            if channel_layer is None:
                raise RuntimeError("No channel layer configured.")
            async_to_sync(channel_layer.group_send)(
                "surveillance_alerts",
                alert_payload,
            )
            self.stdout.write(self.style.SUCCESS(
                f"  [OK] {matched.alert_level} alert broadcast -> 'surveillance_alerts'"
            ))
        except Exception as exc:
            # Redis is not running locally -- show what *would* be sent.
            self.stdout.write(self.style.WARNING(
                f"  [!] WebSocket broadcast skipped (Redis unavailable: {exc}). "
                f"Payload prepared and displayed above for the live demo."
            ))
            self.stdout.write(self.style.NOTICE(
                f"  Prepared payload: {alert_payload}"
            ))

        return alert_payload
