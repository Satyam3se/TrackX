"""Video stream processing pipeline for ANPR.

Processes video feeds frame-by-frame using YOLOv8 for plate localization
and EasyOCR for character recognition. Deduplicates hits within a time window
and broadcasts real-time WebSocket alerts for hotlisted plates.
"""

import os
from datetime import timedelta

import cv2
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.utils import timezone

from .models import BlacklistedVehicle, CameraVideoFeed, DetectionLog
from .vision import (
    _clean_plate_text,
    _detect_plate_boxes,
    _encode_png,
    _preprocess_plate_crop,
    get_easyocr_reader,
    get_yolo_model,
    save_crop,
)

CONFIDENCE_MIN_THRESHOLD = 0.45
DEDUPLICATION_WINDOW_SECONDS = 3.0


def process_video_stream(video_feed_id: int, sample_rate: int = 5) -> dict:
    """Process a video feed file using YOLOv8 + EasyOCR.

    Args:
        video_feed_id (int): ID of the CameraVideoFeed instance.
        sample_rate (int): Process every Nth frame (default: 5).

    Returns:
        dict: Summary of processing execution.
    """
    video_feed = CameraVideoFeed.objects.filter(id=video_feed_id).first()
    if not video_feed:
        raise ValueError(f"CameraVideoFeed with id={video_feed_id} does not exist.")

    video_path = video_feed.video_file.path
    if not os.path.exists(video_path):
        raise FileNotFoundError(f"Video file not found at: {video_path}")

    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise ValueError(f"Could not open video file: {video_path}")

    fps = cap.get(cv2.CAP_PROP_FPS)
    if not fps or fps <= 0:
        fps = 25.0

    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    model = get_yolo_model()
    reader = get_easyocr_reader()

    camera = video_feed.camera
    channel_layer = get_channel_layer()

    # Track last detection frame timestamp per license plate for deduplication
    last_seen_ts = {}
    detections_created = 0
    alerts_triggered = 0
    processed_count = 0

    frame_idx = 0

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        if frame_idx % sample_rate != 0:
            frame_idx += 1
            continue

        processed_count += 1
        frame_timestamp = round(frame_idx / fps, 2)

        # --- Progress Update ---
        if total_frames > 0:
            progress_pct = int((frame_idx / total_frames) * 100)
            if progress_pct % 10 == 0: # Send update every 10%
                if channel_layer:
                    payload = {
                        'type': 'send_progress_update',
                        'video_feed_id': video_feed.id,
                        'progress': progress_pct,
                    }
                    try:
                        async_to_sync(channel_layer.group_send)(
                            'surveillance_alerts',
                            payload,
                        )
                    except Exception:
                        pass
        # -----------------------

        box = _detect_plate_boxes(model, frame)
        if box is not None:
            x1, y1, x2, y2 = box
            h, w = frame.shape[:2]
            x1, y1 = max(0, x1), max(0, y1)
            x2, y2 = min(w, x2), min(h, y2)

            if x2 > x1 and y2 > y1:
                plate_crop = frame[y1:y2, x1:x2]
                processed_crop = _preprocess_plate_crop(plate_crop)

                ocr_results = reader.readtext(processed_crop)
                if ocr_results:
                    _, raw_text, conf = max(ocr_results, key=lambda r: r[2])
                    plate_text = _clean_plate_text(raw_text)
                    conf = float(conf)

                    # Filter noise: confidence >= 0.45 and alphanumeric length between 6-12 chars
                    if conf >= CONFIDENCE_MIN_THRESHOLD and 6 <= len(plate_text) <= 12:
                        last_ts = last_seen_ts.get(plate_text)
                        if last_ts is None or (frame_timestamp - last_ts) >= DEDUPLICATION_WINDOW_SECONDS:
                            last_seen_ts[plate_text] = frame_timestamp

                            crop_bytes = _encode_png(processed_crop)
                            crop_path = save_crop(camera.camera_id, plate_text, crop_bytes)

                            base_time = video_feed.uploaded_at or timezone.now()
                            captured_at = base_time + timedelta(seconds=frame_timestamp)

                            log = DetectionLog.objects.create(
                                camera=camera,
                                video_feed=video_feed,
                                license_plate=plate_text,
                                confidence_score=conf,
                                frame_timestamp=frame_timestamp,
                                captured_at=captured_at,
                                crop_image_path=crop_path,
                            )
                            detections_created += 1

                            blacklisted = BlacklistedVehicle.objects.filter(
                                license_plate__iexact=plate_text,
                                is_active=True,
                            ).first()

                            if blacklisted:
                                alerts_triggered += 1
                                if channel_layer:
                                    payload = {
                                        'type': 'send_alert_notification',
                                        'alert_level': blacklisted.alert_level,
                                        'plate': plate_text,
                                        'owner': blacklisted.owner_name,
                                        'reason': blacklisted.reason,
                                        'camera': camera.location_name,
                                        'coordinates': [camera.location.x, camera.location.y],
                                        'timestamp': str(log.captured_at),
                                        'frame_timestamp': frame_timestamp,
                                        'video_feed_id': video_feed.id,
                                    }
                                    try:
                                        async_to_sync(channel_layer.group_send)(
                                            'surveillance_alerts',
                                            payload,
                                        )
                                    except Exception:
                                        pass

        frame_idx += 1

    cap.release()

    video_feed.processed = True
    video_feed.save(update_fields=['processed'])

    return {
        'video_feed_id': video_feed_id,
        'camera_id': camera.camera_id,
        'total_frames': total_frames,
        'processed_frames': processed_count,
        'detections_created': detections_created,
        'alerts_triggered': alerts_triggered,
    }
