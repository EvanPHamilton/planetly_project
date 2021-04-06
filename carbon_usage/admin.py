from django.contrib import admin

from .models import UsageType, Usage

admin.site.register(UsageType)
admin.site.register(Usage)
