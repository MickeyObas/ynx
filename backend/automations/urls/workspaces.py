from django.urls import path
from automations.views.workspace import (
    WorkspaceList,
    WorkspaceDetail,
    WorkspaceMemberList,
    WorkspaceMemberDetail,
    WorkspaceAutomationList,
    WorkspaceConnectionList,
    WorkspaceConnectionDetail,
    WorkspaceConnectionInitiate,
    SetActiveWorkspace
)

urlpatterns = [
    path("", WorkspaceList.as_view(), name="workspace-list"),
    path("set-active/", SetActiveWorkspace.as_view()),

    path("<str:pk>/", WorkspaceDetail.as_view(), name="workspace-detail"),

    # Automations
    path("<str:pk>/automations/", WorkspaceAutomationList.as_view(), name="workspace-automation-list"),

    # Connections
    path("<str:pk>/connections/", WorkspaceConnectionList.as_view(), name="workspace-connection-list"),
    path("<str:pk>/connections/connect/", WorkspaceConnectionInitiate.as_view(), name="workspace-connection-initiate"),
    path("<str:pk>/connections/<str:connection_id>/", WorkspaceConnectionDetail.as_view(), name="workspace-connection-list"),

    # Members
    path("<str:pk>/members/", WorkspaceMemberList.as_view(), name="workspace-member-list"),
    path("<str:pk>/members/<int:user_id>/", WorkspaceMemberDetail.as_view(), name="workspace-member-detail"),
]