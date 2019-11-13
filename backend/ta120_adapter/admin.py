from django.contrib import admin
from django.contrib.admin import ModelAdmin

from .models import TA120Sensor

admin.site.register(TA120Sensor, ModelAdmin)
