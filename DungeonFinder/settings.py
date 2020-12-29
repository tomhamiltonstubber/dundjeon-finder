import os
from urllib.parse import urlparse

import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration

DJ_DIR = os.path.dirname(__file__)
BASE_DIR = os.path.dirname(DJ_DIR)

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv('SECRET_KEY', 'TEST_SECRET')

DEBUG = os.getenv('DEBUG', True)
LIVE = os.getenv('LIVE')

ALLOWED_HOSTS = []
ON_HEROKU = 'DYNO' in os.environ


def env_true(var_name, alt='FALSE'):
    return os.getenv(var_name, alt).upper() in {'1', 'TRUE'}


BASE_URL = os.getenv('BASE_URL', 'http://localhost:8000')

# Application definition

SILENCED_SYSTEM_CHECKS = ['captcha.recaptcha_test_key_error']

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'DungeonFinder.staticfiles',
    'django.contrib.staticfiles',
    'captcha',
    'django_rq',
    'DungeonFinder.games',
    'DungeonFinder.users',
    'DungeonFinder.common',
    'DungeonFinder.messaging',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'DungeonFinder.urls'

_TEMPLATE_CONTEXT_PROCESSORS = (
    'django.contrib.auth.context_processors.auth',
    'django.template.context_processors.debug',
    'django.template.context_processors.media',
    'django.template.context_processors.static',
    'django.template.context_processors.tz',
    'django.template.context_processors.request',
    'django.template.context_processors.csrf',
    'django.contrib.messages.context_processors.messages',
)

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.jinja2.Jinja2',
        'APP_DIRS': True,
        'DIRS': ['templates'],
        'OPTIONS': {
            'context_processors': _TEMPLATE_CONTEXT_PROCESSORS,
            'environment': 'DungeonFinder.jinja2.environment',
        },
    },
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {'context_processors': _TEMPLATE_CONTEXT_PROCESSORS},
    },
]

WSGI_APPLICATION = 'DungeonFinder.wsgi.application'


# =======================
#  Database
# =======================

if LIVE:
    import dj_database_url

    DATABASES = {'default': dj_database_url.config()}
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql_psycopg2',
            'NAME': 'dungeonfinder',
            'USER': os.getenv('PGUSER', 'postgres'),
            'PASSWORD': os.getenv('PGPASSWORD', 'waffle'),
            'HOST': os.getenv('PGHOST', 'localhost'),
            'PORT': os.getenv('PGPORT', '5432'),
        }
    }


# =======================
#  Authentication
# =======================

# Password validation
# https://docs.djangoproject.com/en/3.1/ref/settings/#auth-password-validators

LOGOUT_REDIRECT_URL = '/'
AUTH_USER_MODEL = 'users.User'
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]
PASSWORD_MIN_LENGTH = 8

# =======================
#  Localization
# =======================

LANGUAGE_CODE = 'en-gb'

TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = True
USE_TZ = True

# =======================
#  AWS
# =======================

AWS_ACCESS_KEY = os.getenv('AWS_ACCESS_KEY', '')
AWS_SECRET_KEY = os.getenv('AWS_SECRET_KEY', '')
AWS_STORAGE_BUCKET_NAME = os.getenv('AWS_STORAGE_BUCKET_NAME', 'dungeon-finder')
AWS_PUBLIC_BUCKET_NAME = os.getenv('AWS_STORAGE_BUCKET_NAME', 'dungeon-finder-public')
AWS_REGION = os.getenv('AWS_REGION', 'eu-west-2')


# =======================
#  Messaging
# =======================

FROM_EMAIL_ADDRESS = os.getenv('FROM_EMAIL_ADDRESS', 'tomhamiltonstubber@gmail.com')
SEND_EMAILS = True

# =======================
#  Static Files
# =======================

STATIC_ROOT = 'staticfiles'
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]
STATIC_URL = '/static/'

if sentry_dsn := os.getenv('SENTRY_DSN'):
    sentry_sdk.init(dsn=sentry_dsn, integrations=[DjangoIntegration()], send_default_pii=True)


# =======================
#   Logging
# =======================

LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'filters': {
        'require_debug_false': {'()': 'django.utils.log.RequireDebugFalse'},
        'require_debug_true': {'()': 'django.utils.log.RequireDebugTrue'},
    },
    'formatters': {
        'df': {
            'format': '%(name)16s ⬢ %(message)s' if ON_HEROKU else '[%(asctime)s] %(name)-16s %(message)s',
            'datefmt': '%d/%b/%Y %H:%M:%S',
        },
        'rq_console': {
            'format': '%(message).300s' if ON_HEROKU else '%(asctime)s %(message).300s',
            'datefmt': '%H:%M:%S',
        },
        'django.server': {'()': 'django.utils.log.ServerFormatter', 'format': '[%(server_time)s] %(message)s'},
    },
    'handlers': {
        'rq_console': {'level': 'INFO', 'formatter': 'rq_console', 'class': 'DungeonFinder.rq.RQHandler'},
        'debug_console': {'level': 'DEBUG', 'filters': ['require_debug_true'], 'class': 'logging.StreamHandler'},
        'null': {'class': 'logging.NullHandler'},
        'sentry': {'level': 'WARNING', 'class': 'sentry_sdk.integrations.logging.EventHandler'},
        'django.server': {'level': 'INFO', 'class': 'logging.StreamHandler', 'formatter': 'django.server'},
        'df': {
            'level': 'DEBUG' if DEBUG else 'INFO',
            'class': 'DungeonFinder.streamhandler.StreamHandler',
            'formatter': 'df',
        },
    },
    'loggers': {
        'django.server': {'handlers': ['django.server'], 'level': 'INFO', 'propagate': False},
        'django': {'handlers': ['debug_console'], 'level': 'INFO'},
        'df': {'handlers': ['df', 'sentry'], 'level': 'DEBUG', 'propagate': False},
        'django.security': {'handlers': ['sentry', 'debug_console'], 'level': 'ERROR', 'propagate': False},
        'django.security.DisallowedHost': {'handlers': ['null'], 'propagate': False},
        'sentry.errors': {'level': 'WARNING', 'handlers': ['debug_console'], 'propagate': False},
        'rq.worker': {'handlers': ['rq_console'], 'level': 'INFO'},
    },
}

# =======================
#  ReCaptcha
# =======================

# test keys from https://developers.google.com/recaptcha/docs/faq, need to be changed in production!
RECAPTCHA_PUBLIC_KEY = os.getenv('RECAPTCHA_PUBLIC_KEY', '6LeIxAcTAAAAAJcZVRqyHh71UMIEGNQ_MXjiZKhI')
RECAPTCHA_PRIVATE_KEY = os.getenv('RECAPTCHA_PRIVATE_KEY', '6LeIxAcTAAAAAGG-vFI1TnRWxMZNFuojJ4WifJWe')

# =======================
#   Redis and RQ
# =======================

redis_url = urlparse(os.getenv('REDIS_URL', 'redis://localhost:6379'))
redis_db = os.getenv('REDIS_DB', '0')
redis_connections = int(os.getenv('REDIS_CONNECTIONS', '50'))
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': f'redis://{redis_url.hostname}:{redis_url.port}/{redis_db}',
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            'PASSWORD': redis_url.password,
            'CONNECTION_POOL_KWARGS': {'max_connections': redis_connections},
        },
    }
}
ASYNC_RQ = env_true('ASYNC_RQ', 'TRUE')

RQ_QUEUES = {'default': {'USE_REDIS_CACHE': 'default', 'ASYNC': ASYNC_RQ}}

try:
    from localsettings import *  # noqa
except ImportError:
    pass
