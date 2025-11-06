from django.contrib import admin

from .models import Integration, Connection, Automation, Trigger

admin.site.register(Integration)
admin.site.register(Connection)
admin.site.register(Automation)
admin.site.register(Trigger)