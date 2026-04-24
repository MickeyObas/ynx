from django.contrib import admin

from .models import Integration, Connection, Automation, Trigger, Step, EventRecord, Task, Execution


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


admin.site.register(Integration)
admin.site.register(Connection, ConnectionModelAdmin)
admin.site.register(Automation)
admin.site.register(Trigger, TriggerModelAdmin)
admin.site.register(Step)
admin.site.register(EventRecord, EventRecordModelAdmin)
admin.site.register(Task)
admin.site.register(Execution)