from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.db import connection

from rest_framework.routers import DefaultRouter

from apps.mountains.views import MountainViewSet
from apps.climbers.views import ClimberViewSet, GroupViewSet, GroupMemberViewSet
from apps.ascents.views import AscentViewSet
from apps.accounts.views import home, login_page, register_page


# ===== Служебные функции =====
def health_check(request):
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        return JsonResponse({"status": "ok", "database": "connected"}, status=200)
    except Exception as e:
        return JsonResponse({"status": "error", "database": str(e)}, status=500)


def root(request):
    return JsonResponse({
        'message': 'Alpine Club API',
        'endpoints': {
            'admin': '/admin/',
            'api': '/api/',
            'health': '/health/',
            'home': '/home/',
            'login': '/login/',
            'register': '/register/',
        }
    })


# ===== API роутер =====
router = DefaultRouter()
router.register(r'mountains', MountainViewSet)
router.register(r'climbers', ClimberViewSet)
router.register(r'groups', GroupViewSet)
router.register(r'group-members', GroupMemberViewSet)
router.register(r'ascents', AscentViewSet)


# ===== Маршруты =====
urlpatterns = [
    # Главная (JSON со списком эндпоинтов)
    path('', root, name='root'),

    # Админка
    path('admin/', admin.site.urls),

    # API
    path('api/', include(router.urls)),
    path('health/', health_check, name='health_check'),

    # Веб-страницы (аутентификация)
    path('home/', home, name='home'),
    path('login/', login_page, name='login_page'),
    path('register/', register_page, name='register'),
]

# Медиа в режиме разработки
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Статика
urlpatterns += staticfiles_urlpatterns()