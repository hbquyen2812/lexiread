"""Isolated fast tests only. Never imports .env or connects to the deployed database.

SQLite verifies application workflows, not PostgreSQL locking/concurrency semantics.
Production continues to require PostgreSQL via config.settings.
"""
from pathlib import Path
BASE_DIR=Path(__file__).resolve().parent.parent
SECRET_KEY='test-only-not-for-production-012345678901234567890123456789'
DEBUG=False
ALLOWED_HOSTS=['testserver','localhost','127.0.0.1']
INSTALLED_APPS=['django.contrib.admin','django.contrib.auth','django.contrib.contenttypes','django.contrib.sessions','django.contrib.messages','django.contrib.staticfiles','learning']
MIDDLEWARE=['django.middleware.security.SecurityMiddleware','django.contrib.sessions.middleware.SessionMiddleware','django.middleware.common.CommonMiddleware','django.middleware.csrf.CsrfViewMiddleware','django.contrib.auth.middleware.AuthenticationMiddleware','django.contrib.messages.middleware.MessageMiddleware']
ROOT_URLCONF='config.urls'
TEMPLATES=[{'BACKEND':'django.template.backends.django.DjangoTemplates','DIRS':[BASE_DIR/'templates'],'APP_DIRS':True,'OPTIONS':{'context_processors':['django.template.context_processors.request','django.contrib.auth.context_processors.auth','django.contrib.messages.context_processors.messages']}}]
DATABASES={'default':{'ENGINE':'django.db.backends.sqlite3','NAME':':memory:'}}
PASSWORD_HASHERS=['django.contrib.auth.hashers.MD5PasswordHasher']
STATIC_URL='/static/'
STATICFILES_DIRS=[BASE_DIR/'static']
DEFAULT_AUTO_FIELD='django.db.models.BigAutoField'
USE_TZ=True
TIME_ZONE='Asia/Ho_Chi_Minh'
LANGUAGE_CODE='vi'
LOGIN_URL='/login/'
AUTH_DAILY_LIMIT=100
PASSWORD_RESET_TIMEOUT=3600
EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend'
EMAIL_RECOVERY_ENABLED=True
PUBLIC_SITE_URL=''
DEFAULT_FROM_EMAIL='Lexivela <noreply@example.test>'
AUTH_PASSWORD_VALIDATORS=[{'NAME':'django.contrib.auth.password_validation.MinimumLengthValidator','OPTIONS':{'min_length':10}}]
LOGIN_REDIRECT_URL='/'
LOGOUT_REDIRECT_URL='/'
AI_PROVIDER='none'
OPENAI_API_KEY=''
OPENAI_MODEL='test-disabled'
AI_DAILY_LIMIT=30
TRUST_PROXY_HTTPS=False
DATA_UPLOAD_MAX_MEMORY_SIZE=10*1024*1024
