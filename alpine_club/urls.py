from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse


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
    path('api/', include('apps.mountains.urls')),
    path('api/', include('apps.climbers.urls')),
    path('api/', include('apps.ascents.urls')),
    path('api/health/', health_check),
]