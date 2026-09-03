from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone

from anpr_engine.models import BlacklistedVehicle, CameraNode


class Command(BaseCommand):
    help = 'Simulate a blacklisted vehicle detection and fire a test WebSocket alert.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--plate', dest='plate', type=str, default='KDA 123A',
            help='License plate to trigger alert for (default: "KDA 123A")',
        )
        parser.add_argument(
            '--camera', dest='camera_id', type=str, default='CAM-001',
            help='Camera ID to simulate capture on (default: "CAM-001")',
        )

    def handle(self, *args, **options):
        plate = options['plate']
        camera_id = options['camera_id']

        camera = CameraNode.objects.filter(camera_id=camera_id).first()
        if not camera:
            raise CommandError(f'CameraNode with camera_id={camera_id!r} does not exist.')

        vehicle = BlacklistedVehicle.objects.filter(license_plate__iexact=plate).first()
        if not vehicle:
            self.stdout.write(self.style.WARNING(
                f'No BlacklistedVehicle record found for plate={plate!r}. Using fallback test details.'
            ))
            owner = 'Simulated Owner'
            reason = 'Simulated hotlist alert trigger'
            alert_level = 'CRITICAL'
        else:
            owner = vehicle.owner_name
            reason = vehicle.reason
            alert_level = vehicle.alert_level

        channel_layer = get_channel_layer()
        if not channel_layer:
            raise CommandError('Channel layer is not configured.')

        payload = {
            'type': 'send_alert_notification',
            'alert_level': alert_level,
            'plate': plate,
            'owner': owner,
            'reason': reason,
            'camera': camera.location_name,
            'coordinates': [camera.location.x, camera.location.y],
            'timestamp': str(timezone.now()),
        }

        self.stdout.write(f'Broadcasting alert to group "surveillance_alerts": {payload}')
        try:
            async_to_sync(channel_layer.group_send)('surveillance_alerts', payload)
        except Exception as exc:
            self.stderr.write(self.style.ERROR(
                f'Failed to reach the channel layer (is Redis running?): {exc}'
            ))
            raise CommandError(
                'Could not fire test alert. Ensure Redis is running on :6379 '
                '(or REDIS_URL is set) before retrying.'
            )
        self.stdout.write(self.style.SUCCESS('Successfully fired test alert to channel layer.'))