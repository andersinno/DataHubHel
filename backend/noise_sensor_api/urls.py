from  django.urls import path

from noise_sensor_api.views import (
    ObservationListView, ObservationRetrieveView)

urlpatterns = [
    path(r'observations/',
         ObservationListView().as_view(),
         name='observations-list'),
    path(r'observations/<connect_topic>/<connect_partition>/<connect_offset>/',
         ObservationRetrieveView().as_view(),
         name='observations-detail'),
]
