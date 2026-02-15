from django.contrib import admin

from .models import Integration, Connection, Automation, Trigger, Step, EventRecord


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

admin.site.register(Integration)
admin.site.register(Connection)
admin.site.register(Automation)
admin.site.register(Trigger)
admin.site.register(Step)
admin.site.register(EventRecord, EventRecordModelAdmin)