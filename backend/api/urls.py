from django.urls import path, include

urlpatterns = [
    path('auth/', include('users.urls')),
    path("workspaces/", include("automations.workspace_urls"))
]