from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from django.http import JsonResponse
from django.db import connection

# Импортируем вьюсеты из всех приложений
from apps.mountains.views import MountainViewSet
from apps.climbers.views import ClimberViewSet, GroupViewSet, GroupMemberViewSet
from apps.ascents.views import AscentViewSet

from apps.accounts.views import home, login_page, register_page

# Функция проверки работоспособности сервиса и СУБД (Health Check по ТЗ)
def health_check(request):
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        return JsonResponse({"status": "ok", "database": "connected"}, status=200)
    except Exception as e:
        return JsonResponse({"status": "error", "database": str(e)}, status=500)

# Настраиваем общий API-роутер
router = DefaultRouter()
router.register(r'mountains', MountainViewSet)
router.register(r'climbers', ClimberViewSet)
router.register(r'groups', GroupViewSet)
router.register(r'group-members', GroupMemberViewSet)
router.register(r'ascents', AscentViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('home/', home, name="home"),
    path('login/', login_page, name='login_page'),
    path('register/', register_page, name='register'),
    
    # Служебный адрес проверки работоспособности (Health Check)
    path('health/', health_check, name='health_check'),
    
    # Подключаем эндпоинты DRF
    path('api/', include(router.urls)),
]