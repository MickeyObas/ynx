from django.urls import path

from .views import oauth_callback, start_oauth, connection_test

urlpatterns = [ 
    # NOTE: "service_name" is a temp variable for testing
    path("oauth/<str:service_name>/callback/", oauth_callback),
    path("oauth/<str:integration_id>/start/<str:workspace_id>", start_oauth),
    path("test/<str:connection_id>", connection_test)
]