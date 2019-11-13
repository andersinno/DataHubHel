from rest_framework import routers

from .views import (
    ServicePermissionsViewSet,
    ServiceTokenViewSet,
    ServiceViewSet,
    SubscriptionViewSet,
)

router = routers.SimpleRouter()

router.register(
    r'services', ServiceViewSet)
router.register(
    r'servicetokens', ServiceTokenViewSet,
    base_name='servicetoken')
router.register(
    r'servicepermissions', ServicePermissionsViewSet,
    base_name='servicepermission')
router.register(
    r'subscriptions', SubscriptionViewSet,
    base_name='subscription'
)

urlpatterns = router.urls
