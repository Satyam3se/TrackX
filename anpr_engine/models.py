from django.contrib.gis.db import models
from django.utils import timezone


class CameraNode(models.Model):
    camera_id = models.CharField(max_length=100, unique=True)
    location_name = models.CharField(max_length=255)
    location = models.PointField(srid=4326)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f'{self.camera_id} - {self.location_name}'


class CameraVideoFeed(models.Model):
    camera = models.ForeignKey(
        CameraNode,
        on_delete=models.CASCADE,
        related_name='video_feeds',
    )
    video_file = models.FileField(upload_to='video_feeds/')
    title = models.CharField(max_length=255)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    processed = models.BooleanField(default=False)

    class Meta:
        ordering = ['-uploaded_at']

    def __str__(self):
        return f'{self.title} ({self.camera.camera_id})'


class DetectionLog(models.Model):
    camera = models.ForeignKey(
        CameraNode,
        on_delete=models.CASCADE,
        related_name='detection_logs',
        db_index=True,
    )
    video_feed = models.ForeignKey(
        CameraVideoFeed,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='detections',
    )
    license_plate = models.CharField(max_length=20)
    confidence_score = models.FloatField(default=0.0)
    captured_at = models.DateTimeField(default=timezone.now)
    frame_timestamp = models.FloatField(null=True, blank=True)
    crop_image_path = models.CharField(max_length=512, blank=True)
    speed_estimate = models.FloatField(null=True, blank=True)

    class Meta:
        ordering = ['-captured_at']
        indexes = [
            models.Index(
                fields=['license_plate', 'captured_at'],
                name='detection_plate_capture_idx',
            ),
        ]

    def __str__(self):
        return f'{self.license_plate} @ {self.captured_at:%Y-%m-%d %H:%M}'


class BlacklistedVehicle(models.Model):
    ALERT_LEVEL_CHOICES = [
        ('CRITICAL', 'Critical'),
        ('WARNING', 'Warning'),
        ('INFO', 'Info'),
    ]

    license_plate = models.CharField(max_length=20, unique=True)
    owner_name = models.CharField(max_length=255)
    reason = models.TextField()
    alert_level = models.CharField(
        max_length=20,
        choices=ALERT_LEVEL_CHOICES,
        default='INFO',
    )
    flagged_at = models.DateTimeField(default=timezone.now)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f'{self.license_plate} ({self.alert_level})'