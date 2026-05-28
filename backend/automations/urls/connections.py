from django.urls import path
from automations.views.connections import (
    ConnectionInitiate,
)

urlpatterns = [
    path("initiate/", ConnectionInitiate.as_view(), name="connection-initiate"),
]