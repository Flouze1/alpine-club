import os
import socket
from django.http import JsonResponse


def version_view(request):
    return JsonResponse(
        {
            "service": "alpine-club",
            "version": os.getenv("APP_VERSION", "unknown"),
            "instance": socket.gethostname(),
        }
    )
