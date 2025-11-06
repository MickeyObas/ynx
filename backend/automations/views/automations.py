from rest_framework import viewsets, status
from rest_framework.request import Request
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from automations.serializers import AutomationSerializer, TriggerSerializer
from automations.models import Automation


class AutomationViewSet(viewsets.ModelViewSet):
    """
    CRUD for Automations + custom actions for enabling/disabling/pausing.
    """
    serializer_class = AutomationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        workspace_id = self.kwargs.get("workspace_pk")

        # NOTE: Change later
        if not workspace_id:
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

    # @action(detail=True, methods=["get"], url_path="triggers")
    # def list_triggers(self, request, workspace_pk=None, pk=None):
    #     """List all triggers for this automation."""
    #     automation = self.get_object()
    #     triggers = automation.triggers.all()
    #     serializer = TriggerSerializer(triggers, many=True)
    #     return Response(serializer.data)

    @action(detail=True, methods=["post"], url_path="triggers")
    def add_trigger(self, request, workspace_pk=None, pk=None):
        """Add a new trigger to this automation."""
        automation = self.get_object()
        serializer = TriggerSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(automation=automation)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["put"], url_path=r"triggers/(?P<trigger_id>[^/.]+)")
    def update_trigger(self, request, workspace_pk=None, pk=None, trigger_id=None):
        """Update an existing trigger for this automation."""
        automation = self.get_object()
        try:
            trigger = automation.triggers.get(pk=trigger_id)
        except Trigger.DoesNotExist:
            return Response({"detail": "Trigger not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = TriggerSerializer(trigger, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    @action(detail=True, methods=["delete"], url_path=r"triggers/(?P<trigger_id>[^/.]+)")
    def delete_trigger(self, request, workspace_pk=None, pk=None, trigger_id=None):
        """Delete a trigger from this automation."""
        automation = self.get_object()
        try:
            trigger = automation.triggers.get(pk=trigger_id)
        except Trigger.DoesNotExist:
            return Response({"detail": "Trigger not found."}, status=status.HTTP_404_NOT_FOUND)

        trigger.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

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