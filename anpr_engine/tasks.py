import os

from asgiref.sync import async_to_sync
from celery import shared_task
from channels.layers import get_channel_layer
from django.utils import timezone

from .models import BlacklistedVehicle, CameraNode, CameraVideoFeed, DetectionLog
from .vision import extract_license_plate, save_crop
from .vision_video import process_video_stream

OCR_CONFIDENCE_THRESHOLD = 0.4


@shared_task(
    name='anpr_engine.process_camera_frame',
    bind=True,
    max_retries=3,
    default_retry_delay=5,
)
def process_camera_frame(self, camera_id, image_path, speed_estimate=None):
    """Run ANPR on a single camera frame, persist a DetectionLog, and broadcast
    WebSocket alerts if the plate is on the active hotlist.

    Args:
        camera_id (str): The ``CameraNode.camera_id`` the frame came from.
        image_path (str): Path (or URL) to the captured frame.
        speed_estimate (float|None): Optional vehicle speed at capture time.

    Returns a JSON-serializable summary dict.
    """
    camera = CameraNode.objects.filter(camera_id=camera_id).first()
    if camera is None:
        raise ValueError(f'No CameraNode found for camera_id={camera_id!r}')

    if not os.path.isfile(image_path):
        # Local file missing — assume the worker may be on a different host.
        self.retry(countdown=30)

    detection = extract_license_plate(image_path)

    plate_text = detection.get('plate_text', '')
    confidence = detection.get('confidence', 0.0)
    cropped_img = detection.get('cropped_img', b'')
    bbox = detection.get('bbox')

    crop_path = ''
    detection_log = None
    alert_triggered = False

    if plate_text and confidence > OCR_CONFIDENCE_THRESHOLD:
        crop_path = save_crop(camera_id, plate_text, cropped_img)
        detection_log = DetectionLog.objects.create(
            camera=camera,
            license_plate=plate_text,
            confidence_score=confidence,
            speed_estimate=speed_estimate,
            crop_image_path=crop_path,
        )

        blacklisted = BlacklistedVehicle.objects.filter(
            license_plate__iexact=plate_text,
            is_active=True,
        ).first()

        if blacklisted:
            alert_triggered = True
            channel_layer = get_channel_layer()
            if channel_layer:
                payload = {
                    'type': 'send_alert_notification',
                    'alert_level': blacklisted.alert_level,
                    'plate': plate_text,
                    'owner': blacklisted.owner_name,
                    'reason': blacklisted.reason,
                    'camera': camera.location_name,
                    'coordinates': [camera.location.x, camera.location.y],
                    'timestamp': str(detection_log.captured_at),
                }
                async_to_sync(channel_layer.group_send)(
                    'surveillance_alerts',
                    payload,
                )

    return {
        'camera_id': camera_id,
        'processed_at': timezone.now().isoformat(),
        'plate_text': plate_text,
        'confidence': confidence,
        'detected': detection_log is not None,
        'alert_triggered': alert_triggered,
        'bbox': bbox,
        'crop_image_path': crop_path,
        'detection_log_id': detection_log.id if detection_log else None,
    }


@shared_task(
    name='anpr_engine.process_video_feed_task',
    bind=True,
    max_retries=3,
    default_retry_delay=10,
    acks_late=True,
    task_track_started=False,
)
def process_video_feed_task(self, video_feed_id, sample_rate=5):
    """Asynchronously run ANPR (YOLOv8 + EasyOCR) on a video feed file.

    Args:
        video_feed_id (int): PK of the CameraVideoFeed to process.
        sample_rate (int): Process every Nth frame (default: 5).

    Returns:
        dict: Summary of processing execution, or None when retries are exhausted.
    """
    try:
        summary = process_video_stream(video_feed_id, sample_rate=sample_rate)
        return summary
    except Exception as exc:
        self.retry(exc=exc)
        return None