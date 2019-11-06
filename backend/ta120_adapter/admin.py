from django.contrib import admin
from django.contrib.admin import ModelAdmin
from django.contrib.gis.admin import OSMGeoAdmin

from .models import TA120Sensor

admin.site.register(TA120Sensor, ModelAdmin)
