from django.contrib import admin
from django.contrib.gis.admin import GISModelAdmin
from django.utils.html import format_html

from .models import (
    BlacklistedVehicle,
    CameraNode,
    CameraVideoFeed,
    DetectionLog,
)


@admin.action(description='Process Selected Videos with YOLOv8 + EasyOCR')
def process_selected_videos(modeladmin, request, queryset):
    """Admin action: trigger the async Celery video-processing task."""
    from .tasks import process_video_feed_task

    queued = []
    for feed in queryset:
        if not feed.processed:
            process_video_feed_task.delay(feed.id)
            queued.append(feed.id)

    if queued:
        modeladmin.message_user(
            request,
            f'{len(queued)} video feed(s) queued for YOLOv8+EasyOCR processing.',
        )
    else:
        modeladmin.message_user(
            request,
            'No unprocessed video feeds selected.',
        )


@admin.register(CameraVideoFeed)
class CameraVideoFeedAdmin(admin.ModelAdmin):
    list_display = (
        'title', 'camera', 'uploaded_at', 'processed',
        'video_file_link',
    )
    list_filter = ('processed', 'camera', 'uploaded_at')
    search_fields = ('title', 'camera__camera_id', 'camera__location_name')
    date_hierarchy = 'uploaded_at'
    actions = [process_selected_videos]

    def video_file_link(self, obj):
        try:
            url = obj.video_file.url
        except ValueError:
            return '—'
        return format_html('<a href="{}" target="_blank">view</a>', url)

    video_file_link.short_description = 'Video File'


@admin.register(CameraNode)
class CameraNodeAdmin(GISModelAdmin):
    list_display = ('camera_id', 'location_name', 'is_active', 'created_at')
    list_filter = ('is_active',)
    search_fields = ('camera_id', 'location_name')

    class Media:
        css = {'all': ('gis/css/ol3.css',)}
        js = ('gis/js/ol.js',)


@admin.register(DetectionLog)
class DetectionLogAdmin(admin.ModelAdmin):
    list_display = ('license_plate', 'camera', 'confidence_score',
                    'speed_estimate', 'captured_at')
    list_filter = ('camera', 'confidence_score')
    search_fields = ('license_plate',)
    date_hierarchy = 'captured_at'


@admin.register(BlacklistedVehicle)
class BlacklistedVehicleAdmin(admin.ModelAdmin):
    list_display = ('license_plate', 'owner_name', 'alert_level',
                    'is_active', 'flagged_at')
    list_filter = ('alert_level', 'is_active')
    search_fields = ('license_plate', 'owner_name')
    date_hierarchy = 'flagged_at'