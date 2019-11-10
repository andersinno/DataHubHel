from django.contrib import admin
from django.contrib.admin import ModelAdmin

from datahubhel.core.models import Datastream, Location, Thing

admin.site.register(Datastream, ModelAdmin)
admin.site.register(Location, ModelAdmin)
admin.site.register(Thing, ModelAdmin)
