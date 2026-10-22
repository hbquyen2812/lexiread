"""Private local-first deployment. PostgreSQL is required; no SQLite fallback."""
import os
from pathlib import Path
from django.core.exceptions import ImproperlyConfigured
from dotenv import load_dotenv
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / '.env')
def env_bool(key, default=False):
    return os.getenv(key, str(default)).lower() in {'1', 'true', 'yes'}
def csv_env(key, default=''):
    return [x.strip() for x in os.getenv(key, default).split(',') if x.strip()]
SECRET_KEY = os.getenv('DJANGO_SECRET_KEY', '')
if len(SECRET_KEY) < 40:
    raise ImproperlyConfigured('Run python scripts/init_env.py or .\\setup.ps1 to generate .env first.')
DEBUG = env_bool('DJANGO_DEBUG', True)
ALLOWED_HOSTS = csv_env('DJANGO_ALLOWED_HOSTS', 'localhost,127.0.0.1,[::1]')
CSRF_TRUSTED_ORIGINS = csv_env('DJANGO_CSRF_TRUSTED_ORIGINS')
INSTALLED_APPS = [
    'django.contrib.admin','django.contrib.auth','django.contrib.contenttypes',
    'django.contrib.sessions','django.contrib.messages','django.contrib.staticfiles','learning',
]
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware','whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware','django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware','django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware','django.middleware.clickjacking.XFrameOptionsMiddleware',
]
ROOT_URLCONF = 'config.urls'
WSGI_APPLICATION = 'config.wsgi.application'
TEMPLATES = [{'BACKEND':'django.template.backends.django.DjangoTemplates',
    'DIRS':[BASE_DIR/'templates'],'APP_DIRS':True,'OPTIONS':{'context_processors':[
    'django.template.context_processors.request','django.contrib.auth.context_processors.auth',
    'django.contrib.messages.context_processors.messages']}}]
DATABASES = {'default':{'ENGINE':'django.db.backends.postgresql',
    'NAME':os.getenv('POSTGRES_DB','lexiread'), 'USER':os.getenv('POSTGRES_USER','lexiread'),
    'PASSWORD':os.getenv('POSTGRES_PASSWORD',''), 'HOST':os.getenv('POSTGRES_HOST','127.0.0.1'),
    'PORT':os.getenv('POSTGRES_PORT','5432'), 'CONN_MAX_AGE':60,
    'OPTIONS':{'connect_timeout':8}}}
AUTH_PASSWORD_VALIDATORS = [
    {'NAME':'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME':'django.contrib.auth.password_validation.MinimumLengthValidator','OPTIONS':{'min_length':10}},
    {'NAME':'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME':'django.contrib.auth.password_validation.NumericPasswordValidator'},
]
LANGUAGE_CODE = 'vi'
TIME_ZONE = 'Asia/Ho_Chi_Minh'
USE_I18N = True
USE_TZ = True
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR/'staticfiles'
STATICFILES_DIRS = [BASE_DIR/'static']
STORAGES = {'default':{'BACKEND':'django.core.files.storage.FileSystemStorage'},
            'staticfiles':{'BACKEND':'whitenoise.storage.CompressedManifestStaticFilesStorage'}}
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/login/'
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Lax'
CSRF_COOKIE_SAMESITE = 'Lax'
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'
SECURE_REFERRER_POLICY = 'same-origin'
SECURE_SSL_REDIRECT = env_bool('DJANGO_HTTPS', False)
SESSION_COOKIE_SECURE = env_bool('DJANGO_HTTPS', False)
CSRF_COOKIE_SECURE = env_bool('DJANGO_HTTPS', False)
# Enable only behind a reverse proxy that overwrites X-Forwarded-Proto.
if env_bool('TRUST_PROXY_HTTPS', False):
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO','https')
DATA_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024
FILE_UPLOAD_MAX_MEMORY_SIZE = 8 * 1024 * 1024
AI_PROVIDER = os.getenv('AI_PROVIDER','none')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY','')
OPENAI_MODEL = os.getenv('OPENAI_MODEL','gpt-4.1-mini')
AI_DAILY_LIMIT = max(1, min(int(os.getenv('AI_DAILY_LIMIT','30')), 200))
LOGGING = {'version':1,'disable_existing_loggers':False,'handlers':{'console':{'class':'logging.StreamHandler'}},
           'root':{'handlers':['console'],'level':'WARNING'}}
