from datetime import timedelta

from django.contrib.gis.geos import Point
from django.core.management.base import BaseCommand
from django.utils import timezone

from anpr_engine.models import BlacklistedVehicle, CameraNode, DetectionLog

CAMERA_SEEDS = [
    {'camera_id': 'CAM-042', 'location_name': 'Ring Rd / ITO Junction', 'lon': 77.2410, 'lat': 28.6289},
    {'camera_id': 'CAM-118', 'location_name': 'Rajghat Flyover', 'lon': 77.2498, 'lat': 28.6412},
    {'camera_id': 'CAM-233', 'location_name': 'Kashmere Gate ISBT', 'lon': 77.2295, 'lat': 28.6673},
    {'camera_id': 'CAM-501', 'location_name': 'GT Karnal Road', 'lon': 77.2011, 'lat': 28.6905},
    {'camera_id': 'CAM-612', 'location_name': 'Azadpur Mandi', 'lon': 77.1758, 'lat': 28.7078},
    {'camera_id': 'CAM-144', 'location_name': 'Rajouri Garden', 'lon': 77.2500, 'lat': 28.6820},
    {'camera_id': 'CAM-091', 'location_name': 'Connaught Place', 'lon': 77.2250, 'lat': 28.6150},
]

PLATES = [
    'DL 3C AF 9021', 'DL 1C J 7788', 'DL 8C X 4412', 'DL 5C B 1234', 'HR 26 DQ 9940',
    'UP 14 AB 5678', 'DL 3E AW 1122', 'HR 55 AL 3344', 'UP 16 CD 5566', 'DL 9C K 7788',
    'DL 2C M 9900', 'HR 12 BR 2233', 'UP 32 EF 4455', 'DL 6C N 6677', 'DL 4C P 8899',
]

BLACKLIST_SEEDS = [
    {
        'license_plate': 'DL 3C AF 9021',
        'owner_name': 'Arjun Mehta',
        'reason': 'Reported stolen vehicle; involved in hit and run',
        'alert_level': 'CRITICAL',
    },
    {
        'license_plate': 'HR 26 DQ 4412',
        'owner_name': 'Ravi Khanna',
        'reason': 'Repeat traffic violations in a restricted zone',
        'alert_level': 'WARNING',
    },
]


class Command(BaseCommand):
    help = 'Seed trackx_db with CameraNodes, DetectionLogs, and BlacklistedVehicles.'

    def handle(self, *args, **options):
        now = timezone.now()

        cameras = []
        for seed in CAMERA_SEEDS:
            camera, _ = CameraNode.objects.update_or_create(
                camera_id=seed['camera_id'],
                defaults={
                    'location_name': seed['location_name'],
                    'location': Point(seed['lon'], seed['lat'], srid=4326),
                    'is_active': True,
                },
            )
            cameras.append(camera)
        self.stdout.write(self.style.SUCCESS(f'Seeded {len(cameras)} CameraNodes'))

        created_logs = 0

        # Hotlist plates get multi-checkpoint trajectories so the map route renders.
        HOTLIST_TRAJECTORIES = [
            ('DL 3C AF 9021', [0, 1, 2, 3, 4]),   # CAM-042 -> ... -> CAM-612
            ('HR 26 DQ 4412', [1, 2, 3, 4, 5]),
        ]
        for plate, cams in HOTLIST_TRAJECTORIES:
            for j, idx in enumerate(cams):
                camera = cameras[idx % len(cameras)]
                captured_at = now - timedelta(minutes=(len(HOTLIST_TRAJECTORIES) + j) * 6)
                DetectionLog.objects.create(
                    camera=camera,
                    license_plate=plate,
                    captured_at=captured_at,
                    confidence_score=round(0.9 + 0.02 * j, 2),
                    crop_image_path=(
                        f'crops/{camera.camera_id}/{plate}'
                        f'_{captured_at:%Y%m%d%H%M%S}.jpg'
                    ),
                    speed_estimate=round(30 + j * 8, 1),
                )
                created_logs += 1

        for i, plate in enumerate(PLATES):
            camera = cameras[i % len(cameras)]
            captured_at = now - timedelta(minutes=i * 9)
            DetectionLog.objects.create(
                camera=camera,
                license_plate=plate,
                captured_at=captured_at,
                confidence_score=round(0.65 + (i * 37 % 30) / 100, 2),
                crop_image_path=(
                    f'crops/{camera.camera_id}/{plate}'
                    f'_{captured_at:%Y%m%d%H%M%S}.jpg'
                ),
                speed_estimate=round(40 + (i * 17 % 90), 1),
            )
            created_logs += 1
        self.stdout.write(
            self.style.SUCCESS(f'Seeded {created_logs} DetectionLogs (incl. hotlist trajectories)')
        )

        blacklists = []
        for seed in BLACKLIST_SEEDS:
            vehicle, _ = BlacklistedVehicle.objects.update_or_create(
                license_plate=seed['license_plate'],
                defaults={
                    'owner_name': seed['owner_name'],
                    'reason': seed['reason'],
                    'alert_level': seed['alert_level'],
                    'is_active': True,
                },
            )
            blacklists.append(vehicle)
        self.stdout.write(
            self.style.SUCCESS(f'Seeded {len(blacklists)} BlacklistedVehicles')
        )