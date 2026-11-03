from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import ClimberViewSet, GroupMemberViewSet, GroupViewSet

router = DefaultRouter()
router.register(r"climbers", ClimberViewSet)
router.register(r"groups", GroupViewSet)
router.register(r"group-members", GroupMemberViewSet)

urlpatterns = [
    path("", include(router.urls)),
]
