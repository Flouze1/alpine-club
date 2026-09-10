from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ClimberViewSet, GroupViewSet, GroupMemberViewSet

router = DefaultRouter()
router.register(r'climbers', ClimberViewSet)
router.register(r'groups', GroupViewSet)
router.register(r'group-members', GroupMemberViewSet)

urlpatterns = [
    path('', include(router.urls)),
]