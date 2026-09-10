from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AscentViewSet

router = DefaultRouter()
router.register(r'ascents', AscentViewSet)

urlpatterns = [
    path('', include(router.urls)),
]