from rest_framework.routers import DefaultRouter
from rest_framework_nested.routers import NestedSimpleRouter

from .views import WorkspaceViewSet, AutomationViewSet, ConnectionViewset

router = DefaultRouter()
router.register("", WorkspaceViewSet, basename="workspace")

automations_router = NestedSimpleRouter(router, r'', lookup='workspace')
automations_router.register('automations', AutomationViewSet, basename='workspace-automations')

connections_router = NestedSimpleRouter(router, r'', lookup="workspace")
connections_router.register("connections", ConnectionViewset, basename="workspace-connections")

urlpatterns = router.urls + automations_router.urls + connections_router.urls