"""Disposable Docker QA. Does not import production settings or read .env."""
import os
from django.core.exceptions import ImproperlyConfigured
from .test_settings import *  # noqa: F403

QA_ONLY=True
qa_host=os.environ.get('LEXIREAD_QA_DB_HOST','qa-db')
if qa_host!='qa-db':
    raise ImproperlyConfigured('QA database host must be the isolated compose service qa-db.')
DATABASES={'default':{
    'ENGINE':'django.db.backends.postgresql','NAME':'lexiread_qa',
    'USER':'lexiread_qa','PASSWORD':'lexiread-qa-local-only','HOST':qa_host,'PORT':'5432',
    'CONN_MAX_AGE':0,'OPTIONS':{'connect_timeout':5},'TEST':{'NAME':'test_lexiread_qa'},
}}
DEBUG=True
EMAIL_BACKEND='django.core.mail.backends.console.EmailBackend'
