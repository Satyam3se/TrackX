import os

from django.core.management.base import BaseCommand, CommandError

from anpr_engine.models import CameraNode, DetectionLog
from anpr_engine.tasks import process_camera_frame


class Command(BaseCommand):
    help = 'Run the ANPR pipeline on an image and persist a DetectionLog.'

    def add_arguments(self, parser):
        parser.add_argument('camera_id', type=str, help='CameraNode.camera_id')
        parser.add_argument(
            'image_path', type=str, help='Path to the captured frame image',
        )
        parser.add_argument(
            '--speed', dest='speed', type=float, default=None,
            help='Optional speed estimate (km/h) to record',
        )

    def handle(self, *args, **options):
        camera_id = options['camera_id']
        image_path = options['image_path']
        speed = options['speed']

        if not CameraNode.objects.filter(camera_id=camera_id).exists():
            raise CommandError(f'No CameraNode found for camera_id={camera_id!r}')
        if not os.path.isfile(image_path):
            raise CommandError(f'Image file not found: {image_path}')

        self.stdout.write(f'Processing frame: {image_path}')
        self.stdout.write(f'Camera: {camera_id} | speed: {speed}')

        result = process_camera_frame.run(
            camera_id=camera_id,
            image_path=image_path,
            speed_estimate=speed,
        )

        self.stdout.write(self.style.SUCCESS('ANPR pipeline completed:'))
        self.stdout.write(f'  plate_text       : {result["plate_text"]!r}')
        self.stdout.write(f'  confidence       : {result["confidence"]:.3f}')
        self.stdout.write(f'  detected         : {result["detected"]}')
        self.stdout.write(f'  bbox             : {result["bbox"]}')
        self.stdout.write(f'  crop_image_path  : {result["crop_image_path"]}')

        if result['detection_log_id']:
            log = DetectionLog.objects.get(pk=result['detection_log_id'])
            self.stdout.write(
                self.style.SUCCESS(
                    f'DetectionLog #{log.pk} created for plate '
                    f'{log.license_plate!r} at {log.captured_at}'
                )
            )
        else:
            self.stdout.write(self.style.WARNING(
                'No DetectionLog persisted (plate not read with '
                'confidence > 0.4, or no plate box found).'
            ))