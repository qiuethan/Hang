from rest_framework.routers import DefaultRouter

from .views import NotificationViewSet

app_name = 'notifications'

router = DefaultRouter()
router.register(r'notifications', NotificationViewSet, basename='notifications')

urlpatterns = router.urls
