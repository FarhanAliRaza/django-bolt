from django.urls import path, include
from django.conf import settings
from django.contrib import admin

urlpatterns = []

if "django.contrib.admin" in settings.INSTALLED_APPS:
    urlpatterns.append(path("admin/", admin.site.urls))



