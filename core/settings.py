"""
Django settings for multi-tenant document management demo.

Architecture:
  SHARED_APPS  → public schema (tenants, users, auth)
  TENANT_APPS  → per-tenant schemas (documents, business logic)
"""

import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = "demo-only-not-for-production"

DEBUG = True

ALLOWED_HOSTS = ["*"]


# ── Application Definitions ─────────────────────────────────────────────

SHARED_APPS = [
    # django-tenants must come first in shared apps
    "django_tenants",
    "tenants",                     # our Tenant model
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
]

TENANT_APPS = [
    # Apps that get their own schema per tenant
    "documents",
]

INSTALLED_APPS = SHARED_APPS + [app for app in TENANT_APPS if app not in SHARED_APPS]


# ── Tenant Configuration ────────────────────────────────────────────────

TENANT_MODEL = "tenants.Client"
TENANT_DOMAIN_MODEL = "tenants.Domain"

DATABASE_ROUTERS = ["django_tenants.routers.TenantSyncRouter"]

# Middleware: django_tenants.main.TenantMainMiddleware detects the tenant
# from the request domain and sets the connection's schema search path.
MIDDLEWARE = [
    "django_tenants.middleware.main.TenantMainMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "core.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "core.wsgi.application"


# ── Database ────────────────────────────────────────────────────────────

# PostgreSQL with schema support is required for django-tenants.
# This connects to the Docker container we spun up.
DATABASES = {
    "default": {
        "ENGINE": "django_tenants.postgresql_backend",
        "NAME": "multitenant_dev",
        "USER": "postgres",
        "PASSWORD": "demo123",
        "HOST": "localhost",
        "PORT": "5432",
    }
}


# ── Auth, Static, DRF, etc. ─────────────────────────────────────────────

AUTH_PASSWORD_VALIDATORS = []

LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.SessionAuthentication",
        "rest_framework.authentication.BasicAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
}
