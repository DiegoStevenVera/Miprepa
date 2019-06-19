from .base import *

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'miprepadb',
        'USER': 'postgres',
        'PASSWORD': 'postgres',
        'HOST': 'localhost'
    }
}

DEBUG = False

TEMPLATE_DEBUG = False

ALLOWED_HOSTS = ['134.209.121.248', 'miprepa.doge-labs.com']

ADMINS = (
    ('Luis Campos Rubina', 'luis@kodevian.com'),
)

# Email
EMAIL_USE_TLS = True
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_HOST_USER = 'luis@kodevian.com'
EMAIL_HOST_PASSWORD = 'kodevianluis'
