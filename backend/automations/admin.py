from django.contrib import admin

from .models import Integration, Connection

admin.site.register(Integration)
admin.site.register(Connection)
