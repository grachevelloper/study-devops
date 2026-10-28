from django.urls import path

from . import views


urlpatterns = [
    path("", views.index, name="index"),
    path("grpc", views.grpc, name="grpc"),
    path("nginx", views.nginx, name="nginx"),
]
