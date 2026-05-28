from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from django.shortcuts import get_object_or_404
from django.db import transaction
from django.contrib.auth import get_user_model

from automations.models import Workspace, WorkspaceMembership, Automation, Connection, Integration
from automations.serializers import WorkspaceSerializer, WorkspaceMembershipSerializer, AutomationSerializer, ConnectionSerializer, ConnectionDisplaySerializer

User = get_user_model()


class WorkspaceList(APIView):
    """GET/POST /workspaces/"""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        workspaces = Workspace.objects.filter(members=request.user).distinct()
        serializer = WorkspaceSerializer(workspaces, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = WorkspaceSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class WorkspaceDetail(APIView):
    """GET/PATCH/DELETE /workspaces/<pk>/"""
    permission_classes = [IsAuthenticated]

    def get_object(self, request, pk):
        return get_object_or_404(
            Workspace.objects.filter(members=request.user).distinct(),
            pk=pk,
        )

    def get(self, request, pk):
        workspace = self.get_object(request, pk)
        serializer = WorkspaceSerializer(workspace)
        return Response(serializer.data)

    def patch(self, request, pk):
        workspace = self.get_object(request, pk)
        serializer = WorkspaceSerializer(workspace, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def delete(self, request, pk):
        workspace = self.get_object(request, pk)
        workspace.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class WorkspaceMemberList(APIView):
    """GET/POST /workspaces/<pk>/members/"""
    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def get(self, request, pk):
        workspace = get_object_or_404(
            Workspace.objects.filter(members=request.user).distinct(),
            pk=pk,
        )
        memberships = WorkspaceMembership.objects.filter(workspace=workspace)
        serializer = WorkspaceMembershipSerializer(memberships, many=True)
        return Response(serializer.data)

    @transaction.atomic
    def post(self, request, pk):
        workspace = get_object_or_404(
            Workspace.objects.filter(members=request.user).distinct(),
            pk=pk,
        )

        user_id = request.data.get("user_id")
        if not user_id:
            return Response({"error": "user_id required."}, status=status.HTTP_400_BAD_REQUEST)

        user = get_object_or_404(User, id=user_id)

        if WorkspaceMembership.objects.filter(workspace=workspace, user=user).exists():
            return Response({"error": "User is already a member."}, status=status.HTTP_400_BAD_REQUEST)

        WorkspaceMembership.objects.create(
            workspace=workspace,
            user=user,
            role=WorkspaceMembership.Role.MEMBER,
        )
        return Response({"success": "Member added."}, status=status.HTTP_201_CREATED)


class WorkspaceMemberDetail(APIView):
    """PATCH/DELETE /workspaces/<pk>/members/<user_id>/"""
    permission_classes = [IsAuthenticated]

    def get_workspace(self, request, pk):
        return get_object_or_404(
            Workspace.objects.filter(members=request.user).distinct(),
            pk=pk,
        )

    def patch(self, request, pk, user_id):
        workspace = self.get_workspace(request, pk)

        requester = WorkspaceMembership.objects.filter(
            workspace=workspace, user=request.user
        ).first()
        if not requester or requester.role != WorkspaceMembership.Role.ADMIN:
            return Response(
                {"detail": "Only admins can update roles."},
                status=status.HTTP_403_FORBIDDEN,
            )

        member = get_object_or_404(WorkspaceMembership, workspace=workspace, user_id=user_id)

        new_role = request.data.get("role")
        if new_role not in dict(WorkspaceMembership.Role.choices):
            return Response({"detail": "Invalid role."}, status=status.HTTP_400_BAD_REQUEST)

        member.role = new_role
        member.save()
        return Response(WorkspaceMembershipSerializer(member).data)

    def delete(self, request, pk, user_id):
        workspace = self.get_workspace(request, pk)

        requester = WorkspaceMembership.objects.filter(
            workspace=workspace, user=request.user
        ).first()
        if not requester:
            return Response(
                {"detail": "You're not part of this workspace."},
                status=status.HTTP_403_FORBIDDEN,
            )

        if requester.role != WorkspaceMembership.Role.ADMIN and str(request.user.id) != str(user_id):
            return Response(
                {"detail": "You can only remove yourself."},
                status=status.HTTP_403_FORBIDDEN,
            )

        member = get_object_or_404(WorkspaceMembership, workspace=workspace, user_id=user_id)
        member.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    

class WorkspaceAutomationList(APIView):
    def get(self, request, pk):
        workspace = get_object_or_404(
            Workspace.objects.filter(members=request.user),
            pk=pk
        )
        automations = Automation.objects.filter(
            workspace=workspace
        )

        serializer = AutomationSerializer(automations, many=True)

        return Response(serializer.data)
    

class WorkspaceConnectionList(APIView):
    def get(self, request, pk):
        workspace = get_object_or_404(
            Workspace.objects.filter(members=request.user),
            pk=pk
        )
        qs = Connection.objects.filter(
            workspace=workspace
        )

        integration_id = request.query_params.get("integrationId")
        if integration_id and integration_id != "null":
            try:
                integration = Integration.objects.get(id=integration_id)
                qs = qs.filter(integration=integration)
            except Integration.DoesNotExist:
                return Response(
                    {"error": f"Integration with ID {integration_id} does not exist."},
                    status=status.HTTP_404_NOT_FOUND,
                )

        serializer = ConnectionDisplaySerializer(qs, many=True)

        return Response(serializer.data)
    

class WorkspaceConnectionDetail(APIView):
    def get(self, request, pk, connection_id):
        connection = get_object_or_404(
            Connection.objects.filter(
                workspace_id=pk,
                workspace__members=request.user,
                id=connection_id
            )
        )
        serializer = ConnectionSerializer(connection)
        return Response(serializer.data)
    
    def delete(self, request, pk, connection_id):
        connection = get_object_or_404(
            Connection.objects.filter(
                workspace_id=pk,
                workspace__members=request.user,
                id=connection_id
            )
        )
        connection.delete()
        return Response(status=204)
    
    def patch(self, request, pk, connection_id):
        connection = get_object_or_404(
            Connection.objects.filter(
                workspace_id=pk,
                workspace__members=request.user,
                id=connection_id
            )
        )
        serializer = ConnectionSerializer(connection, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)
    

class WorkspaceConnectionInitiate(APIView):
    def post(self, request, pk):
        data = request.data.copy()
        data["workspace_id"] = pk

        # Return existing connection if one already exists for this integration
        existing = Connection.objects.filter(
            workspace_id=pk,
            integration_id=data.get("integration_id"),
        ).first()
        if existing:
            return Response({"connection_id": str(existing.id)})

        serializer = ConnectionSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        connection = serializer.save()

        # Uncomment when auth flow is ready:
        # service = get_integration_service(connection.integration.id, connection)
        # auth_url = service.get_auth_url(connection.id)

        return Response({
            "connection_id": str(connection.id),
            # "auth_url": auth_url,
        }, status=status.HTTP_201_CREATED)