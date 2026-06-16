from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.shortcuts import get_object_or_404

from automations.models import Automation, Execution, Step, Trigger, Workspace
from automations.serializers import (
    AutomationSerializer,
    TriggerSerializer,
    ExecutionSerializer,
    StepCreateSerializer,
    StepDetailSerializer,
    StepUpdateSerializer,
    PublishAutomationSerializer
)
from automations.services.automations import publish_automation
from automations.exceptions import AutomationValidationError


class AutomationList(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        qs = Automation.objects.filter(
            workspace__members=request.user
        ).distinct()

        workspace_id = request.query_params.get("workspace_id")
        if workspace_id:
            qs = qs.filter(workspace_id=workspace_id)

        status_param = request.query_params.get("status")
        if status_param:
            qs = qs.filter(status=status_param)

        return Response(AutomationSerializer(qs, many=True).data)

    def post(self, request):
        workspace_id = request.data.get("workspace_id")
        workspace = get_object_or_404(
            Workspace.objects.filter(members=request.user),
            pk=workspace_id
        )

        serializer = AutomationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        print(serializer.errors)
        serializer.save(
            workspace=workspace,
            owner=request.user,
            status=Automation.Status.DRAFT,
        )
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class AutomationDetail(APIView):
    """GET/PATCH/DELETE /automations/<pk>/"""
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        automation = get_object_or_404(
            Automation.objects.filter(workspace__members=request.user, pk=pk)
        )
        serializer = AutomationSerializer(automation)
        return Response(serializer.data)

    def patch(self, request, pk):
        automation = get_object_or_404(
            Automation.objects.filter(workspace__members=request.user, pk=pk)
        )
        serializer = AutomationSerializer(automation, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def delete(self, request, pk):
        automation = get_object_or_404(
            Automation.objects.filter(workspace__members=request.user, pk=pk)
        )
        automation.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class AutomationEnable(APIView):
    """POST /automations/<pk>/enable/"""
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        automation = get_object_or_404(
            Automation.objects.filter(workspace__members=request.user, pk=pk)
        )
        automation.status = Automation.Status.ENABLED
        automation.save()
        return Response({"status": "enabled"})


class AutomationDisable(APIView):
    """POST /automations/<pk>/disable/"""
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        automation = get_object_or_404(
            Automation.objects.filter(workspace__members=request.user, pk=pk)
        )
        automation.status = Automation.Status.DISABLED
        automation.save()
        return Response({"status": "disabled"})


class AutomationPause(APIView):
    """POST /automations/<pk>/pause/"""
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        automation = get_object_or_404(
            Automation.objects.filter(workspace__members=request.user, pk=pk)
        )
        automation.status = Automation.Status.PAUSED
        automation.save()
        return Response({"status": "paused"})


class AutomationPublish(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        automation = get_object_or_404(
            Automation.objects.prefetch_related('steps', 'trigger'),
            id=pk,
            workspace__members=request.user
        )

        serializer = PublishAutomationSerializer(data=request.data, context={'automation': automation})
        serializer.is_valid(raise_exception=True)

        try:
            result = publish_automation(automation)
        except AutomationValidationError as e:
            return Response({'errors': e.errors}, status=status.HTTP_400_BAD_REQUEST)

        return Response(AutomationSerializer(result).data, status=status.HTTP_200_OK)


# Triggers

class TriggerList(APIView):
    """POST /automations/<pk>/triggers/"""
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        automation = get_object_or_404(
            Automation.objects.filter(workspace__members=request.user, pk=pk)
        )
        serializer = TriggerSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(automation=automation)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class TriggerDetail(APIView):
    """GET/PATCH/DELETE /automations/<pk>/triggers/<trigger_id>/"""
    permission_classes = [IsAuthenticated]

    def get(self, request, pk, trigger_id):
        automation = get_object_or_404(
            Automation.objects.filter(workspace__members=request.user, pk=pk)
        )
        trigger = get_object_or_404(
            Trigger.objects.filter(id=trigger_id, automation=automation)
        )

        serializer = TriggerSerializer(trigger)
        return Response(serializer.data)

    def patch(self, request, pk, trigger_id):
        automation = get_object_or_404(
            Automation.objects.filter(workspace__members=request.user, pk=pk)
        )
        trigger = get_object_or_404(
            Trigger.objects.filter(id=trigger_id, automation=automation)
        )

        serializer = TriggerSerializer(trigger, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def delete(self, request, pk, trigger_id):
        automation = get_object_or_404(
            Automation.objects.filter(workspace__members=request.user, pk=pk)
        )
        trigger = get_object_or_404(
            Trigger.objects.filter(id=trigger_id, automation=automation)
        )
        trigger.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# Steps

class StepList(APIView):
    """GET/POST /automations/<pk>/steps/"""
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        steps = Step.objects.filter(
            automation_id=pk,
            automation__workspace__members=request.user,
        )
        serializer = StepDetailSerializer(steps, many=True)
        return Response(serializer.data)
    
    def post(self, request, pk):
        serializer = StepCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        step = serializer.save()
        return Response(StepDetailSerializer(step).data, status=status.HTTP_201_CREATED)


class StepDetail(APIView):
    """PATCH/DELETE /automations/<pk>/steps/<step_id>/"""
    permission_classes = [IsAuthenticated]

    def get(self, request, pk, step_id):
        step = get_object_or_404(
            Step.objects.filter(id=step_id)
        )
        serializer = StepDetailSerializer(step)
        return Response(serializer.data)

    def patch(self, request, pk, step_id):
        step = get_object_or_404(
            Step.objects.filter(id=step_id)
        )
        serializer = StepUpdateSerializer(step, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        step = serializer.save()

        step.automation.status = Automation.Status.DRAFT
        step.automation.save()

        # step.automation.trigger.status = Trigger.Status.READY
        # step.automation.trigger.save()

        return Response(StepDetailSerializer(step).data)

    def delete(self, request, pk, step_id):
        step = get_object_or_404(
            Step.objects.filter(id=step_id)
        )
        step.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# Executions 

class ExecutionDetail(APIView):
    def get(self, request, pk, execution_id):
        try:
            execution = Execution.objects.get(
                automation__workspace__members=request.user,
                id=execution_id
            )
        except Execution.DoesNotExist:
            return Response({"detail": "Execution not found"}, status=404)
        
        serializer = ExecutionSerializer(execution)
        return Response(serializer.data)
            

class ExecutionList(APIView):
    """GET /automations/<pk>/executions/"""
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        try:
            automation = get_object_or_404(
                Automation.objects.filter(workspace__members=request.user),
                pk=pk
            )
        except Automation.DoesNotExist:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
        queryset = Execution.objects.filter(automation=automation).order_by("-created_at")
        serializer = ExecutionSerializer(queryset, many=True)
        return Response(serializer.data)