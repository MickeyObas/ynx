from django.contrib import admin

from .models import Integration, Connection, Automation, Trigger, Step, EventRecord, Task, Execution, Workspace, WorkspaceMembership

class EventRecordModelAdmin(admin.ModelAdmin):
    list_display = [
        'event_id',
        'external_id',
        'integration',
        'trigger',
        'occurred_at',
        'recorded_at',
        'processed',
        "processed_at"
    ]
    ordering = ['-occurred_at', '-recorded_at']
    search_fields = ["event_id"]


class ConnectionModelAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "integration",
        "display_name",
        "config",
        "status"
    ]


class TriggerModelAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "integration",
        "type",
        "trigger_key",
        "connection",
        "status",
        "last_run_at",
        "last_tested_at"
    ]


class StepModelAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "automation",
        "integration",
        "action_name",
        "connection",
        "order",
    ]

    list_display_links = [
        "id",
        "automation"
    ]


class AutomationModelAdmin(admin.ModelAdmin):
    list_display = [
        "name", "owner", "workspace"
    ]


admin.site.register(Integration)
admin.site.register(Connection, ConnectionModelAdmin)
admin.site.register(Automation, AutomationModelAdmin)
admin.site.register(Trigger, TriggerModelAdmin)
admin.site.register(Step, StepModelAdmin)
admin.site.register(EventRecord, EventRecordModelAdmin)
admin.site.register(Task)
admin.site.register(Execution)
admin.site.register(Workspace)
admin.site.register(WorkspaceMembership)