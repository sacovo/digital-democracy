"""
Django settings for backend project.

Generated by 'django-admin startproject' using Django 3.0.4.

For more information on this file, see
https://docs.djangoproject.com/en/3.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.0/ref/settings/
"""

import os

from django.utils.translation import gettext_lazy as _

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get("SECRET_KEY", "change-me")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = int(os.environ.get("DEBUG", "0"))

ALLOWED_HOSTS = ["*"]

# Application definition

INSTALLED_APPS = [
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django_celery_results",
    "ckeditor",
    "papers",
    "django.contrib.admin",
    "django.contrib.auth",
    "bootstrap4",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "backend.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "backend.context_processors.disable_comments",
            ]
        },
    }
]

WSGI_APPLICATION = "backend.wsgi.application"

# Database
# https://docs.djangoproject.com/en/3.0/ref/settings/#databases
DATABASES = {
    "default": {
        "ENGINE": os.environ.get("SQL_ENGINE", "django.db.backends.sqlite3"),
        "NAME": os.environ.get("POSTGRES_DB", os.path.join(BASE_DIR, "db.sqlite3")),
        "USER": os.environ.get("POSTGRES_USER", "user"),
        "PASSWORD": os.environ.get("POSTGRES_PASSWORD", "password"),
        "HOST": os.environ.get("SQL_HOST", "localhost"),
        "PORT": os.environ.get("SQL_PORT", "5432"),
    }
}

DEFAULT_AUTO_FIELD = "django.db.models.AutoField"

# Password validation
# https://docs.djangoproject.com/en/3.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"
    },
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# Internationalization
# https://docs.djangoproject.com/en/3.0/topics/i18n/

LANGUAGE_CODE = "de"

LANGUAGES = [("de", _("German")), ("fr", _("French")), ("it", _("Italian"))]

TIME_ZONE = "UTC"

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.0/howto/static-files/

STATIC_URL = "/static/"
STATIC_ROOT = "/home/app/web/static/"

DEFAULT_FROM_EMAIL = os.environ.get("DEFAULT_FROM_EMAIL", "webmaster@localhost")
SERVER_EMAIL = os.environ.get("SERVER_EMAIL", "root@localhost")

EMAIL_HOST = os.environ.get("SMTP_HOST", "smtp")
EMAIL_PORT = int(os.environ.get("SMTP_PORT", "25"))

EMAIL_USE_TLS = int(os.environ.get("SMTP_TLS", "0"))
EMAIL_USE_SSL = int(os.environ.get("SMTP_SSL", "0"))

EMAIL_HOST_USER = os.environ.get("SMTP_USER", "user")
EMAIL_HOST_PASSWORD = os.environ.get("SMTP_PASSWORD", "pw")

DEFAULT_FROM_EMAIL = os.environ.get("DEFAULT_FROM_EMAIL", "webmaster@localhost")
SERVER_EMAIL = os.environ.get("SERVER_EMAIL", "root@localhost")

CELERY_BROKER_URL = "redis://redis:6379"

CELERY_RESULT_BACKEND = "django-db"
CELERY_CACHE_BACKEND = "django-cache"

CUSTOM_TOOLBAR = [
    ["Format"],
    ["Bold", "Italic", "Underline", "Subscript", "Superscript"],
    ["NumberedList", "BulletedList", "-", "Outdent", "Indent", "-", "Blockquote"],
    ["Link", "Unlink"],
    ["RemoveFormat", "Source"],
    ["Paste", "Cut", "Copy"],
    ["Redo", "Undo"],
]

CKEDITOR_CONFIGS = {
    "default": {"width": "100%", "toolbar": "Custom", "toolbar_Custom": CUSTOM_TOOLBAR},
    "basic": {"toolbar": "Custom", "width": "100%", "toolbar_Custom": CUSTOM_TOOLBAR},
    "track-changes": {
        "extraPlugins": ",".join(["lite"]),
        "width": "100%",
        "toolbar": "Custom",
        "toolbar_Custom": CUSTOM_TOOLBAR,
    },
}

BLEACH_ALLOWED_TAGS = [
    "a",
    "abbr",
    "b",
    "blockquote",
    "em",
    "i",
    "li",
    "ol",
    "ul",
    "span",
    "h1",
    "h2",
    "h3",
    "h4",
    "h5",
    "h6",
    "p",
    "del",
    "ins",
    "strong",
    "pre",
    "address",
    "div",
    "u",
    "sub",
    "sup",
]

BLEACH_ALLOWED_ATTRIBUTES = {"a": ["href", "title", "name", "id"]}


LOGIN_URL = "/members/login"
LOGIN_REDIRECT_URL = "/members/profile"
LOGOUT_REDIRECT_URL = "/members/login"

NEW_USER_MAIL = """Hallo {user.first_name}

In diesem Mail erhälst du deinen Zugang zu https://dd.vote.spschweiz.ch/

Benutzername: {user.username}
Password: {password}

*****

Bonjour {user.first_name}

Dans ce mail, tu recevras ton accès à https://dd.vote.spschweiz.ch/

Nom d'utilisateur : {user.username}
Mot de passe : {password}
"""

PDF_TITLE_FONT = os.environ.get("PDF_TITLE_FONT", "Nimbus")
PDF_BODY_FONT = os.environ.get("PDF_BODY_FONT", "Nimbus")

DISABLE_COMMENTS = os.environ.get("DISABLE_COMMENTS", False)

if DEBUG:
    EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
USE_X_FORWARDED_HOST = True
USE_X_FORWARDED_PORT = True
