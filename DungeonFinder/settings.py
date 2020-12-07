import os
import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration

DJ_DIR = os.path.dirname(__file__)
BASE_DIR = os.path.dirname(DJ_DIR)

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv('_me*v)q1427h=^8bc1i6jn%i@51=!h2zv#f8scnr%u_-(jqbik')

DEBUG = os.getenv('DEBUG', True)
LIVE = os.getenv('LIVE')

ALLOWED_HOSTS = []
ON_HEROKU = 'DYNO' in os.environ


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'DungeonFinder.games',
    'DungeonFinder.users',
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
        'OPTIONS': {'match_extension': '.jinja', 'context_processors': _TEMPLATE_CONTEXT_PROCESSORS},
    },
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {'context_processors': _TEMPLATE_CONTEXT_PROCESSORS},
    },
]

WSGI_APPLICATION = 'DungeonFinder.wsgi.application'


# Database
# https://docs.djangoproject.com/en/3.1/ref/settings/#databases

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


# Password validation
# https://docs.djangoproject.com/en/3.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


LANGUAGE_CODE = 'en-gb'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = True
USE_TZ = True


STATIC_URL = '/static/'

if sentry_dsn := os.getenv('SENTRY_DSN'):
    sentry_sdk.init(
        dsn=sentry_dsn,
        integrations=[DjangoIntegration()],
        send_default_pii=True
    )


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
        'django.server': {'()': 'django.utils.log.ServerFormatter', 'format': '[%(server_time)s] %(message)s'},
        'sentry': {'level': 'WARNING', 'class': 'raven.contrib.django.handlers.SentryHandler'},
    },
    'handlers': {
        'debug_console': {'level': 'DEBUG', 'filters': ['require_debug_true'], 'class': 'logging.StreamHandler'},
        'null': {'class': 'logging.NullHandler'},
        'sentry': {'level': 'WARNING', 'class': 'raven.contrib.django.handlers.SentryHandler'},
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
    },
}


try:
    from localsettings import *  # noqa
except ImportError:
    pass
