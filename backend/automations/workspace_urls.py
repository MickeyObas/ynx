from rest_framework.routers import DefaultRouter
from rest_framework_nested.routers import NestedSimpleRouter

from .views import WorkspaceViewSet, AutomationViewSet

router = DefaultRouter()
router.register("", WorkspaceViewSet, basename="workspace")

automations_router = NestedSimpleRouter(router, r'', lookup='workspace')
automations_router.register('automations', AutomationViewSet, basename='workspace-automations')

urlpatterns = router.urls + automations_router.urls