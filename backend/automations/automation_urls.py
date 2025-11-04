from rest_framework import viewsets
from rest_framework.routers import DefaultRouter

from .views import AutomationViewSet

router = DefaultRouter()
router.register("", AutomationViewSet, basename="automation")

urlpatterns = router.urls




