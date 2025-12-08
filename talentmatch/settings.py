import os
import dj_database_url # ADICIONE ISSO
# ... outros imports
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

# --- Configurações de Segurança CRÍTICAS para Produção ---

# 1. Chave Secreta: Use uma variável de ambiente, garantindo que o valor padrão seja apenas para desenvolvimento local.
SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-dev-key-change-in-production')

# 2. DEBUG: Nunca deve ser True em produção. Se a variável de ambiente não estiver definida, defina como False por padrão.
# Você está usando 'SESSION_SECRET' no seu código original, mudei para 'SECRET_KEY'
DEBUG = os.environ.get('DEBUG', 'False').lower() in ('true', '1', 'yes')

# 3. ALLOWED_HOSTS: É perigoso usar ['*'] em produção, mas se o Railway exigir, mantenha, ou mude para o domínio específico.
# Para maior segurança, o ideal seria: ALLOWED_HOSTS = ['talentmatch-ai-production-cbfe.up.railway.app']
ALLOWED_HOSTS = ['*']

# 4. CSRF_TRUSTED_ORIGINS: Adicionado o protocolo HTTPS e removido o domínio de desenvolvimento 'http' para o Railway.
CSRF_TRUSTED_ORIGINS = [
    'https://*.replit.dev',
    'https://*.repl.co',
    'https://talentmatch-ai-production-cbfe.up.railway.app',
    'http://localhost:5000',
    'http://127.0.0.1:5000',
    'http://localhost:8000',
    'http://127.0.0.1:8000',
]

# 5. Configuração Específica para Railway (Proxy SSL Header) - ADICIONADO
# Isso informa ao Django que ele está por trás de um proxy reverso (como o Railway) e que a conexão é HTTPS.
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# 6. Redirecionamento HTTPS (Recomendado em Produção) - ADICIONADO
# Quando DEBUG=False, força o uso de HTTPS.
if not DEBUG:
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    
# --- Fim das Configurações de Segurança ---


INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'django_filters',
    'accounts',
    'jobs',
    'match',
    'courses',
    'chatbot',
    'dashboard',
    'messaging',
    'api',
    'core',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    # WhiteNoise deve vir logo abaixo de SecurityMiddleware
    'whitenoise.middleware.WhiteNoiseMiddleware', 
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'accounts.middleware.ProfileRedirectMiddleware',
    'accounts.middleware.MaintenanceModeMiddleware',
]

ROOT_URLCONF = 'talentmatch.urls'

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
            ],
        },
    },
]

WSGI_APPLICATION = 'talentmatch.wsgi.application'

if 'DATABASE_URL' in os.environ:
    DATABASES = {
        'default': dj_database_url.config(
            default=os.environ.get('DATABASE_URL'),
            conn_max_age=600,
            conn_health_checks=True,
        )
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'pt-br'
TIME_ZONE = 'America/Sao_Paulo'
USE_I18N = True
USE_TZ = True

# STATICFILES (Configuração de Whitenoise já correta)
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

AUTH_USER_MODEL = 'accounts.User'

LOGIN_URL = 'accounts:login'
LOGIN_REDIRECT_URL = 'dashboard:index'
LOGOUT_REDIRECT_URL = 'core:home'

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
DEFAULT_FROM_EMAIL = 'noreply@talentmatch.com'

REST_FRAMEWORK = {
    'DEFAULT_FILTER_BACKENDS': ['django_filters.rest_framework.DjangoFilterBackend'],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 10,
}