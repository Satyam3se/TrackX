from datetime import datetime
from re import sub

from django.db.models import Avg
from django.utils import timezone
from rest_framework import decorators, status, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import (
    BlacklistedVehicle,
    CameraNode,
    CameraVideoFeed,
    DetectionLog,
)
from .serializers import (
    BlacklistedVehicleSerializer,
    CameraNodeSerializer,
    CameraVideoFeedSerializer,
    DetectionLogSerializer,
    VehicleTrajectorySerializer,
)
from .tasks import process_video_feed_task


def _parse_datetime_param(value):
    """Parse an ISO-8601 string, defaulting to the current timezone if naive.

    Tolerates clients that send a positive UTC offset unencoded in a query
    string (where ``+00:00`` is decoded to `` 00:00``).
    """
    if not value:
        return None
    value = value.strip().replace('Z', '+00:00').replace('z', '+00:00')
    value = sub(
        r'(\d{2}:\d{2}:\d{2}(?:\.\d+)?)\s+([+-]?\d{2}:\d{2})$',
        r'\1+\2',
        value,
    )
    try:
        dt = datetime.fromisoformat(value)
    except ValueError:
        raise ValueError(f'Invalid datetime format: {value!r}')
    if dt.tzinfo is None:
        dt = timezone.make_aware(dt, timezone.get_current_timezone())
    return dt


from django.http import JsonResponse
from django.contrib.gis.geos import Point
from rest_framework.permissions import AllowAny

class TrafficHeatmapAPIView(APIView):
    """GET /api/v1/analytics/detections-geojson/
    
    Returns all detection logs as a GeoJSON FeatureCollection for heatmap rendering.
    """
    permission_classes = [AllowAny]

    def get(self, request):
        logs = DetectionLog.objects.select_related('camera').all()
        
        features = []
        for log in logs:
            # Use the camera's location point for the heatmap
            location = log.camera.location
            features.append({
                'type': 'Feature',
                'geometry': {
                    'type': 'Point',
                    'coordinates': [location.x, location.y],
                },
                'properties': {
                    'plate': log.license_plate,
                    'timestamp': log.captured_at.isoformat(),
                    'weight': 1.0 # Each detection counts as 1 unit of heat
                }
            })

        return JsonResponse({
            'type': 'FeatureCollection',
            'features': features,
        })

class VehicleTrajectoryAPIView(APIView):
    """GET /api/v1/trajectory/<str:license_plate>/

    Optional query params: ``start_date``, ``end_date`` (ISO-8601).
    Returns a GeoJSON FeatureCollection for Mapbox polyline rendering.
    """

    def get(self, request, license_plate):
        try:
            start_date = _parse_datetime_param(request.query_params.get('start_date'))
            end_date = _parse_datetime_param(request.query_params.get('end_date'))
        except ValueError as exc:
            return Response({'detail': str(exc)}, status=status.HTTP_400_BAD_REQUEST)

        queryset = DetectionLog.objects.select_related('camera').filter(
            license_plate__iexact=license_plate,
        )
        if start_date:
            queryset = queryset.filter(captured_at__gte=start_date)
        if end_date:
            queryset = queryset.filter(captured_at__lte=end_date)
        queryset = queryset.order_by('captured_at')

        if not queryset.exists():
            return Response(
                {
                    'type': 'FeatureCollection',
                    'license_plate': license_plate,
                    'total_hits': 0,
                    'time_span': None,
                    'features': [],
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = VehicleTrajectorySerializer(instance=queryset)
        return Response(serializer.data)


class CameraNodeViewSet(viewsets.ModelViewSet):
    """Full CRUD for CameraNode, serialized as GeoJSON features."""

    queryset = CameraNode.objects.all()
    serializer_class = CameraNodeSerializer


class BlacklistedVehicleViewSet(viewsets.ModelViewSet):
    """Full CRUD for BlacklistedVehicle."""

    queryset = BlacklistedVehicle.objects.all()
    serializer_class = BlacklistedVehicleSerializer


class CameraVideoFeedViewSet(viewsets.ModelViewSet):
    """Full CRUD for CameraVideoFeed, plus async video processing via Celery."""

    queryset = CameraVideoFeed.objects.select_related('camera').all()
    serializer_class = CameraVideoFeedSerializer

    @decorators.action(detail=True, methods=['post'])
    def process_video(self, request, pk=None):
        """POST /api/v1/video-feeds/<id>/process_video/

        Trigger the async Celery task ``process_video_feed_task`` for this feed.
        """
        video_feed = self.get_object()
        sample_rate = request.data.get('sample_rate', 5)

        task = process_video_feed_task.delay(video_feed.id, sample_rate)

        return Response(
            {
                'video_feed_id': video_feed.id,
                'sample_rate': sample_rate,
                'task_id': task.id,
                'status': 'queued',
            },
            status=status.HTTP_202_ACCEPTED,
        )

    @decorators.action(detail=True, methods=['get'])
    def detections(self, request, pk=None):
        """GET /api/v1/video-feeds/<id>/detections/

        Return the DetectionLogs produced from this video feed, most recent first.
        """
        video_feed = self.get_object()
        logs = DetectionLog.objects.filter(video_feed=video_feed).select_related(
            'camera',
        )[:100]
        serializer = DetectionLogSerializer(logs, many=True)
        return Response(serializer.data)


class TrafficAnalyticsSummaryAPIView(APIView):
    """GET /api/v1/analytics/summary/

    Returns fleet health + activity summary stats.
    """

    def get(self, request):
        today = timezone.localdate()
        total_cameras = CameraNode.objects.count()
        active_cameras = CameraNode.objects.filter(is_active=True).count()
        detections_today = DetectionLog.objects.filter(
            captured_at__date=today,
        ).count()
        active_blacklisted_count = BlacklistedVehicle.objects.filter(
            is_active=True,
        ).count()

        avg_speed_kmh = (
            DetectionLog.objects
            .filter(speed_estimate__isnull=False)
            .aggregate(avg=Avg('speed_estimate'))['avg']
        ) or 0.0

        return Response({
            'total_cameras': total_cameras,
            'active_cameras': active_cameras,
            'detections_today': detections_today,
            'active_blacklisted_count': active_blacklisted_count,
            'avg_speed_kmh': round(avg_speed_kmh, 1),
        })