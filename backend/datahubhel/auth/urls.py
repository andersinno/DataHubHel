from django.urls import path
from rest_framework import routers
from rest_framework.authtoken import views

from . import api

router = routers.SimpleRouter()

router.register('user-tokens', api.TokenViewSet, base_name='user-token')

urlpatterns = router.urls + [
    path('login/', views.obtain_auth_token, name='user-login'),
    path('me/', api.MeView.as_view(), name='personal-data'),
    path('me/register/', api.RegisterView.as_view(), name='register-user'),
    path('me/forget/', api.ForgetView.as_view(), name='forget-user'),
]
