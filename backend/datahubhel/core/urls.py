from django.urls import path

from .views import SensorListView

app_label = 'datahubhel.core'

urlpatterns = [
    path(r'sensors/', SensorListView.as_view(), name='sensors-list'),
]
