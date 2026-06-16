from django.urls import path
from automations.views.automations import (
    AutomationList,
    AutomationDetail,
    AutomationEnable,
    AutomationDisable,
    AutomationPause,
    AutomationPublish,
    TriggerList,
    TriggerDetail,
    StepList,
    StepDetail,
    ExecutionDetail,
    ExecutionList,
)

urlpatterns = [
    # Automations
    path("", AutomationList.as_view(), name="automation-list"),
    path("<str:pk>/", AutomationDetail.as_view(), name="automation-detail"),

    # Status transitions
    path("<str:pk>/publish/", AutomationPublish.as_view(), name="automation-publish"),
    path("<str:pk>/enable/", AutomationEnable.as_view(), name="automation-enable"),
    path("<str:pk>/disable/", AutomationDisable.as_view(), name="automation-disable"),
    path("<str:pk>/pause/", AutomationPause.as_view(), name="automation-pause"),

    # Triggers
    path("<str:pk>/triggers/", TriggerList.as_view(), name="automation-trigger-list"),
    path("<str:pk>/triggers/<str:trigger_id>/", TriggerDetail.as_view(), name="automation-trigger-detail"),

    # Steps
    path("<str:pk>/steps/", StepList.as_view(), name="automation-step-list"),
    path("<str:pk>/steps/<str:step_id>/", StepDetail.as_view(), name="automation-step-detail"),

    # Executions
    path("<str:pk>/executions/<str:execution_id>/", ExecutionDetail.as_view(), name="automation-execution-detail"),
    path("<str:pk>/executions/", ExecutionList.as_view(), name="automation-execution-list"),
]