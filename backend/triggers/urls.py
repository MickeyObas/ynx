from django.urls import path

from . import views


urlpatterns = [
    path("<str:pk>/test", views.test_trigger)
]