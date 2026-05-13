"""
URL configuration for styleai_project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from django.views.static import serve
from urllib.parse import urlsplit
import re

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('styleai.urls')),
    path('masters/', include('masters.urls')),
]

# Serve media files (for development and simple deployments)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# If DEBUG is disabled but media is served from a local URL, also allow Django to serve media.
# This is useful for simple deployments or when the environment doesn't have a separate media server.
if not settings.DEBUG and settings.MEDIA_URL.startswith('/') and not urlsplit(settings.MEDIA_URL).netloc:
    urlpatterns += [
        re_path(r'^%s(?P<path>.*)$' % re.escape(settings.MEDIA_URL.lstrip('/')), serve, {'document_root': settings.MEDIA_ROOT}),
    ]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
