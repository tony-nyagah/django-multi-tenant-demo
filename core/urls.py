"""URL routing — public endpoints and tenant endpoints."""

from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from documents.views import DocumentViewSet

router = DefaultRouter()
router.register(r"documents", DocumentViewSet, basename="document")

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include(router.urls)),
]
