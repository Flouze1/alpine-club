from django.conf import settings
from django.conf.urls.static import static
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.urls import path

from apps.accounts.views import *

urlpatterns = [
    path("home/", home, name="home"),
    path("login/", login_page, name="login_page"),
    path("register/", register_page, name="register"),
    path("attestation/", attestation_view, name="attestation"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

urlpatterns += staticfiles_urlpatterns()
