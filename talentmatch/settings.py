import os
from pathlib import Path
import dj_database_url

BASE_DIR = Path(__file__).resolve().parent.parent

# -------------------------------------------
# 🔐 SEGURANÇA
# -------------------------------------------

SECRET_KEY = os.environ.get('SESSION_SECRET', os.environ.get('SECRET_KEY', 'django-insecure-dev-key-change-in-production'))

DEBUG = os.environ.get('DEBUG', 'False').lower() in ('true', '1', 'yes')

ALLOWED_HOSTS = [
    '*',  # Railway precisa disso
]

CSRF_TRUSTED_ORIGINS = [
    'https://*.railway.app',
    'https://*.up.railway.app',
    'http://localhost:5000',
    'http://127.0.0.1:5000',
    'http://localhost:8000',
    'http://127.0.0.1:8000',
]

# Railway usa proxy HTTPS — obrigatório
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

if not DEBUG:
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True

# -------------------------------------------
# 📦 APPS
# -------------------------------------------

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Terceiros
    'rest_framework',
    'django_filters',

    # Seus apps
    'accounts',
    'jobs',
    'match',
    'courses',
    'chatbot',
    'dashboard',
    'messaging',
    'feed',
    'api',
]

# -------------------------------------------
# ⚙️ MIDDLEWARE
# -------------------------------------------

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',

    # WhiteNoise deve vir logo após SecurityMiddleware
    'whitenoise.middleware.WhiteNoiseMiddleware',

    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',

    # Seus middlewares
    'accounts.middleware.EmailVerificationMiddleware',
    'accounts.middleware.ProfileRedirectMiddleware',
    'accounts.middleware.MaintenanceModeMiddleware',
]

# -------------------------------------------
# 🔗 URLs & WSGI
# -------------------------------------------

ROOT_URLCONF = 'talentmatch.urls'
WSGI_APPLICATION = 'talentmatch.wsgi.application'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'accounts.context_processors.notifications',
            ],
        },
    },
]

# -------------------------------------------
# 🗄️ BANCO DE DADOS
# -------------------------------------------

if os.environ.get('DATABASE_URL'):
    DATABASES = {
        'default': dj_database_url.config(
            default=os.environ.get('DATABASE_URL'),
            conn_max_age=600,
            conn_health_checks=True
        )
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

# -------------------------------------------
# 🔑 AUTENTICAÇÃO
# -------------------------------------------

AUTH_USER_MODEL = 'accounts.User'

LOGIN_URL = 'accounts:login'
LOGIN_REDIRECT_URL = 'dashboard:index'
LOGOUT_REDIRECT_URL = 'core:home'

# -------------------------------------------
# 🌎 INTERNACIONALIZAÇÃO
# -------------------------------------------

LANGUAGE_CODE = 'pt-br'
TIME_ZONE = 'America/Sao_Paulo'
USE_I18N = True
USE_TZ = True

# -------------------------------------------
# 📁 ESTÁTICOS E MÍDIA
# -------------------------------------------

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

STORAGES = {
    'default': {'BACKEND': 'django.core.files.storage.FileSystemStorage'},
    'staticfiles': {'BACKEND': 'whitenoise.storage.CompressedManifestStaticFilesStorage'},
}

# Armazenamento externo opcional (S3 ou compatível: R2, B2, MinIO...) para mídia.
# O filesystem do Railway é efêmero: sem isso, uploads (fotos, currículos, logos)
# são perdidos a cada deploy. Ativa quando AWS_STORAGE_BUCKET_NAME estiver definido.
if os.environ.get('AWS_STORAGE_BUCKET_NAME'):
    STORAGES['default'] = {'BACKEND': 'storages.backends.s3boto3.S3Boto3Storage'}
    AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')
    AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')
    AWS_STORAGE_BUCKET_NAME = os.environ.get('AWS_STORAGE_BUCKET_NAME')
    AWS_S3_REGION_NAME = os.environ.get('AWS_S3_REGION_NAME', 'us-east-1')
    AWS_S3_ENDPOINT_URL = os.environ.get('AWS_S3_ENDPOINT_URL') or None
    AWS_DEFAULT_ACL = None
    AWS_QUERYSTRING_AUTH = False
    AWS_S3_FILE_OVERWRITE = False

# -------------------------------------------
# 📬 EMAIL
# -------------------------------------------

# SMTP (Brevo) ativado quando EMAIL_HOST_PASSWORD estiver definido no ambiente;
# sem a senha, os emails são exibidos no console (desenvolvimento).
EMAIL_HOST = os.environ.get('EMAIL_HOST', 'smtp-relay.brevo.com')
EMAIL_PORT = int(os.environ.get('EMAIL_PORT', '587'))
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER', 'b0cb28001@smtp-brevo.com')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD', '')
EMAIL_USE_TLS = os.environ.get('EMAIL_USE_TLS', 'true').lower() in ('true', '1', 'yes')

if EMAIL_HOST_PASSWORD:
    EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
else:
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

DEFAULT_FROM_EMAIL = os.environ.get('DEFAULT_FROM_EMAIL', 'noreply@talentmatch.com')

# -------------------------------------------
# 🔎 DJANGO REST FRAMEWORK
# -------------------------------------------

REST_FRAMEWORK = {
    'DEFAULT_FILTER_BACKENDS': ['django_filters.rest_framework.DjangoFilterBackend'],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 10,
}

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
