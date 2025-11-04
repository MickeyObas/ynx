from django.contrib import admin

from .models import Integration, Connection, Automation

admin.site.register(Integration)
admin.site.register(Connection)
admin.site.register(Automation)