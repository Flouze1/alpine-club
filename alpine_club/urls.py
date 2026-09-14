from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.staticfiles.urls import staticfiles_urlpatterns



def health_check(request):
    return JsonResponse({'status': 'ok', 'service': 'Alpine Club API', 'version': '0.1.0'})


def root(request):
    return JsonResponse({
        'message': 'Alpine Club API',
        'endpoints': {
            'admin': '/admin/',
            'api': '/api/',
            'health': '/api/health/',
        }
    })


urlpatterns = [
    path('', root),
    path('admin/', admin.site.urls),

    # API
    path('api/', include('apps.mountains.urls')),
    path('api/', include('apps.climbers.urls')),
    path('api/', include('apps.ascents.urls')),
    path('api/health/', health_check),

    # Веб-страницы (аутентификация)
    path('', include('apps.accounts.urls')),
]

# Медиа в режиме разработки
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Статика
urlpatterns += staticfiles_urlpatterns()