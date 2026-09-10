from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import MountainViewSet

router = DefaultRouter()
router.register(r'mountains', MountainViewSet)

urlpatterns = [
    path('', include(router.urls)),
]