from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import AscentViewSet

router = DefaultRouter()
router.register(r"ascents", AscentViewSet)

urlpatterns = [
    path("", include(router.urls)),
]
