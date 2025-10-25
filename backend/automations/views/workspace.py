from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import action, api_view, permission_classes

from django.shortcuts import get_object_or_404
from django.db import transaction
from django.contrib.auth import get_user_model

from ..serializers import (
    WorkspaceSerializer,
    WorkspaceMembershipSerializer,
)

from ..models import Workspace, WorkspaceMembership

User = get_user_model()

class WorkspaceViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing Workspaces.
    Includes endpoints for listing, creating, retrieving,
    and managing members.
    """
    serializer_class = WorkspaceSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        A user can see:
        - workspaces they own
        - workspaces where they’re a member
        """
        user = self.request.user
        return Workspace.objects.filter(members=user).distinct()

    # -----------------------------
    # Custom actions for members
    # -----------------------------

    @action(detail=True, methods=["get", "post"], url_path="members")
    @transaction.atomic
    def members(self, request, pk=None):
        """
        GET|POST /workspaces/<pk>/members/
        Body: {"user_id": <str>}
        """
        workspace = self.get_object()

        if request.method == "GET":
            memberships = WorkspaceMembership.objects.filter(workspace=workspace)
            serializer = WorkspaceMembershipSerializer(memberships, many=True)
            return Response(serializer.data)

        elif request.method == "POST":
            user_id = request.data.get("user_id")
            if not user_id:
                return Response({"error": "user_id required"}, status=400)

            user = get_object_or_404(User, id=user_id)
            if WorkspaceMembership.objects.filter(workspace=workspace, user=user).exists():
                return Response({"error": "User already a member"}, status=400)

            WorkspaceMembership.objects.create(
                workspace=workspace,
                user=user,
                role=WorkspaceMembership.Role.MEMBER
            )
            return Response({"success": "Member added"}, status=201)


    @action(detail=True, methods=["patch", "delete"], url_path="members/(?P<user_id>[^/.]+)")
    def member(self, request, pk=None, user_id=None):
        """
        PATCH|DELETE /workspaces/<id>/members/<user_id>/
        Body: { "role": "admin" }
        """
        workspace = self.get_object()

        if request.method == "PATCH":
            requester = WorkspaceMembership.objects.filter(workspace=workspace, user=request.user).first()
            if not requester or requester.role != WorkspaceMembership.Role.ADMIN:
                return Response({"detail": "Only admins can update roles."}, status=403)

            member = get_object_or_404(WorkspaceMembership, workspace=workspace, user_id=user_id)
            new_role = request.data.get("role")
            if new_role not in dict(WorkspaceMembership.Role.choices):
                return Response({"detail": "Invalid role."}, status=400)

            member.role = new_role
            member.save()
            return Response(WorkspaceMembershipSerializer(member).data)
        
        elif request.method == "DELETE":
            requester = WorkspaceMembership.objects.filter(workspace=workspace, user=request.user).first()
            if not requester:
                return Response({"detail": "You’re not part of this workspace."}, status=403)

            if requester.role != WorkspaceMembership.Role.ADMIN and str(request.user.id) != user_id:
                return Response({"detail": "You can only remove yourself."}, status=403)

            member = get_object_or_404(WorkspaceMembership, workspace=workspace, user_id=user_id)
            member.delete()
            return Response(status=204)
        
