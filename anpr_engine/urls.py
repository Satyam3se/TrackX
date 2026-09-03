from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    BlacklistedVehicleViewSet,
    CameraNodeViewSet,
    CameraVideoFeedViewSet,
    TrafficAnalyticsSummaryAPIView,
    VehicleTrajectoryAPIView,
    TrafficHeatmapAPIView,
)

router = DefaultRouter()
router.register('cameras', CameraNodeViewSet, basename='camera')
router.register(
    'blacklisted-vehicles', BlacklistedVehicleViewSet,
    basename='blacklistedvehicle',
)
router.register(
    'video-feeds', CameraVideoFeedViewSet,
    basename='videofeed',
)

urlpatterns = [
    path(
        'trajectory/<str:license_plate>/',
        VehicleTrajectoryAPIView.as_view(),
        name='vehicle-trajectory',
    ),
    path(
        'analytics/summary/',
        TrafficAnalyticsSummaryAPIView.as_view(),
        name='traffic-analytics-summary',
    ),
    path(
        'analytics/detections-geojson/',
        TrafficHeatmapAPIView.as_view(),
        name='traffic-heatmap',
    ),
    path('', include(router.urls)),
]