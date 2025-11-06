from django.urls import path

from .views import oauth_callback, start_oauth, connection_test, integration_list, integration_detail

urlpatterns = [ 
    path("", integration_list),
    path("<str:integration_id>", integration_detail),
    path("oauth/<str:service_name>/callback/", oauth_callback),
    path("oauth/<str:integration_id>/start/<str:workspace_id>", start_oauth),
    path("test/<str:connection_id>", connection_test)
]