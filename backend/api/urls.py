from django.urls import path, include

urlpatterns = [
    path('auth/', include('users.urls')),
    path("automations/", include("automations.automation_urls")),
    path("integrations/", include("automations.integration_urls")),
    path("workspaces/", include("automations.workspace_urls"))
]