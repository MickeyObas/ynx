from rest_framework import viewsets
from rest_framework.request import Request
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from ..serializers.automations import AutomationSerializer
from ..models import Automation


class AutomationViewSet(viewsets.ModelViewSet):
    """
    CRUD for Automations + custom actions for enabling/disabling/pausing.
    """
    serializer_class = AutomationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        workspace_id = self.kwargs.get("workspace_pk")

        if self.request.user.is_superuser:
            queryset = Automation.objects.all()
        else:
            queryset = Automation.objects.filter(workspace_id=workspace_id)
            
        status_param = self.request.query_params.get("status")
        if status_param:
            queryset = queryset.filter(status=status_param)
        return queryset

    def perform_create(self, serializer):
        workspace_id = self.kwargs.get("workspace_pk")
        serializer.save(
            workspace_id=workspace_id,
            owner=self.request.user,
            status=Automation.Status.DRAFT
        )

    @action(detail=True, methods=["post"])
    def enable(self, request, workspace_pk=None, pk=None):
        automation = self.get_object()
        automation.status = Automation.Status.ENABLED
        automation.save()
        return Response({"status": "enabled"})

    @action(detail=True, methods=["post"])
    def disable(self, request, workspace_pk=None, pk=None):
        automation = self.get_object()
        automation.status = Automation.Status.DISABLED
        automation.save()
        return Response({"status": "disabled"})

    @action(detail=True, methods=["post"])
    def pause(self, request, workspace_pk=None, pk=None):
        automation = self.get_object()
        automation.status = Automation.Status.PAUSED
        automation.save()
        return Response({"status": "paused"})