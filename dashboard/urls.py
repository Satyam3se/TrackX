from django.urls import path

from . import views

app_name = "dashboard"

urlpatterns = [
    path("", views.index, name="index"),
    path("map/", views.map_dashboard, name="map_dashboard"),
    path("map/fire-alert/", views.fire_test_alert, name="fire_test_alert"),
]
