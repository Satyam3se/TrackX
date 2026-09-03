import math

from rest_framework import serializers
from rest_framework_gis import serializers as gis_serializers

from .models import (
    BlacklistedVehicle,
    CameraNode,
    CameraVideoFeed,
    DetectionLog,
)


class CameraVideoFeedSerializer(serializers.ModelSerializer):
    """Serializer for CameraVideoFeed including camera metadata."""

    camera_id = serializers.CharField(source='camera.camera_id', read_only=True)
    location_name = serializers.CharField(
        source='camera.location_name', read_only=True,
    )
    video_file = serializers.FileField(max_length=512)
    video_url = serializers.SerializerMethodField()

    class Meta:
        model = CameraVideoFeed
        fields = (
            'id', 'camera', 'camera_id', 'location_name', 'title',
            'video_file', 'video_url', 'uploaded_at', 'processed',
        )
        read_only_fields = ('uploaded_at', 'processed')

    def get_video_url(self, obj):
        try:
            return obj.video_file.url
        except ValueError:
            return None


class CameraNodeSerializer(gis_serializers.GeoFeatureModelSerializer):
    """GeoJSON Feature serializer for CameraNode (Point geometry)."""

    location = gis_serializers.GeometryField()

    class Meta:
        model = CameraNode
        geo_field = 'location'
        fields = ('id', 'camera_id', 'location_name', 'is_active', 'created_at')


class BlacklistedVehicleSerializer(serializers.ModelSerializer):
    class Meta:
        model = BlacklistedVehicle
        fields = ('id', 'license_plate', 'owner_name', 'reason',
                  'alert_level', 'flagged_at', 'is_active')
        read_only_fields = ('flagged_at',)


class DetectionLogSerializer(serializers.ModelSerializer):
    camera_id = serializers.CharField(source='camera.camera_id', read_only=True)
    location_name = serializers.CharField(
        source='camera.location_name', read_only=True,
    )
    location = serializers.SerializerMethodField()

    class Meta:
        model = DetectionLog
        fields = (
            'id', 'license_plate', 'confidence_score', 'captured_at',
            'crop_image_path', 'speed_estimate', 'camera_id',
            'location_name', 'location',
        )

    def get_location(self, obj):
        point = obj.camera.location
        return {'type': 'Point', 'coordinates': [point.x, point.y]}


def _haversine_km(lon1, lat1, lon2, lat2):
    """Great-circle distance between two lon/lat pairs in kilometres."""
    radius_km = 6371.0
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    d_phi = math.radians(lat2 - lat1)
    d_lambda = math.radians(lon2 - lon1)
    a = (
        math.sin(d_phi / 2) ** 2
        + math.cos(phi1) * math.cos(phi2) * math.sin(d_lambda / 2) ** 2
    )
    return 2 * radius_km * math.asin(math.sqrt(a))


class VehicleTrajectorySerializer(serializers.Serializer):
    """Builds a GeoJSON FeatureCollection from a chronologically ordered
    queryset of DetectionLogs for a single license plate.

    The payload contains a single LineString feature (for Mapbox polyline
    rendering) plus one Point waypoint feature per detection carrying
    timestamp, camera details, and inter-node speed estimates.
    """
    PHYSICAL_SPEED_LIMIT_KMH = 180.0

    def to_representation(self, detections):
        detections = list(detections)

        line_coords = []
        waypoint_features = []
        previous = None

        for detection in detections:
            point = detection.camera.location
            lon, lat = point.x, point.y
            
            # --- Spatio-Temporal Validation ---
            is_anomaly = False
            inter_speed = None
            if previous is not None:
                prev_point = previous.camera.location
                d_km = _haversine_km(
                    prev_point.x, prev_point.y, lon, lat,
                )
                dt_hours = (
                    detection.captured_at - previous.captured_at
                ).total_seconds() / 3600.0
                if dt_hours > 0:
                    inter_speed = round(d_km / dt_hours, 2)
                    if inter_speed > self.PHYSICAL_SPEED_LIMIT_KMH:
                        is_anomaly = True
            # ----------------------------------

            # Only add to trajectory if not a physical anomaly
            if is_anomaly:
                continue

            line_coords.append([lon, lat])

            waypoint_features.append({
                'type': 'Feature',
                'geometry': {
                    'type': 'Point',
                    'coordinates': [lon, lat],
                },
                'properties': {
                    'id': detection.id,
                    'timestamp': detection.captured_at.isoformat(),
                    'camera_id': detection.camera.camera_id,
                    'location_name': detection.camera.location_name,
                    'license_plate': detection.license_plate,
                    'confidence_score': detection.confidence_score,
                    'speed_estimate': detection.speed_estimate,
                    'segment_speed_kmh': inter_speed,
                },
            })
            previous = detection

        if not detections:
            return {
                'type': 'FeatureCollection',
                'features': [],
            }

        first = detections[0]
        last = detections[-1]
        total_km = _haversine_km(
            first.camera.location.x,
            first.camera.location.y,
            last.camera.location.x,
            last.camera.location.y,
        )
        total_hours = (last.captured_at - first.captured_at).total_seconds() / 3600.0
        avg_speed = round(total_km / total_hours, 2) if total_hours > 0 else None

        return {
            'type': 'FeatureCollection',
            'license_plate': last.license_plate,
            'total_hits': len(detections),
            'time_span': {
                'start': first.captured_at.isoformat(),
                'end': last.captured_at.isoformat(),
            },
            'summary': {
                'distance_km': round(total_km, 3),
                'avg_speed_kmh': avg_speed,
            },
            'features': [
                {
                    'type': 'Feature',
                    'geometry': {
                        'type': 'LineString',
                        'coordinates': line_coords,
                    },
                    'properties': {
                        'source': 'trackx-anpr',
                        'total_hits': len(detections),
                    },
                },
                *waypoint_features,
            ],
        }