from rest_framework import viewsets, status
from rest_framework.request import Request
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from automations.serializers import AutomationSerializer, TriggerSerializer, ExecutionSerializer
from automations.models import Automation, Execution


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

    @action(detail=True, methods=["post"], url_path="triggers")
    def add_trigger(self, request, workspace_pk=None, pk=None):
        """Add a new trigger to this automation."""
        automation = self.get_object()
        serializer = TriggerSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(automation=automation)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(
        detail=True,
        methods=["patch", "delete"],
        url_path=r"triggers/(?P<trigger_id>[^/.]+)"
    )
    def manage_trigger(self, request, workspace_pk=None, pk=None, trigger_id=None):
        automation = self.get_object()

        try:
            trigger = automation.triggers.get(pk=trigger_id)
        except Trigger.DoesNotExist:
            return Response({"detail": "Trigger not found."}, status=404)

        if request.method == "PATCH":
            serializer = TriggerSerializer(trigger, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)

        if request.method == "DELETE":
            trigger.delete()
            return Response(status=204)


    @action(detail=True, methods=["get"], url_path="executions")
    def executions(self, request, workspace_pk=None, pk=None):
        """
        Get execution history for this automation.
        """
        automation = self.get_object()

        queryset = (
            Execution.objects
            .filter(automation=automation)
            .order_by("-created_at")
        )

        serializer = ExecutionSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


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