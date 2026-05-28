from django.urls import path, include

urlpatterns = [
    path('auth/', include('users.urls')),
    path("workspaces/", include("automations.urls.workspaces")),
    path("automations/", include("automations.urls.automations")),
    path("integrations/", include("automations.urls.integrations")),
    path("triggers/", include("triggers.urls")),
    path("workflows/", include('automations.urls.workflows'))
]