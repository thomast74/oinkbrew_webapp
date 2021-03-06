import os

#
# Application Settings
#
DEBUG = False
TEMPLATE_DEBUG = False
TIME_ZONE = 'Europe/London'

BREWPI_PORT = 7873

#
# Influx DB Settings
#
INFLUXDB_HOST = 'localhost'
INFLUXDB_PORT = 8086
INFLUXDB_USER = 'root'
INFLUXDB_PWD = 'root'
INFLUXDB_DB = 'oinkbrew'

#
# Celery Settings
#
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
BROKER_URL='sqla+mysql://oinkuser:Amara@localhost/celery'
CELERY_RESULT_BACKEND = 'db+mysql://oinkuser:Amara@localhost/celery'
CELERY_TASK_RESULT_EXPIRES = 3600

#
# Framework Settings
#
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
SECRET_KEY = '!f+8y8k8$djmc6!o9-h=^7=%uqyltzh!3@4iy)eq2h!y8nh@l='
ALLOWED_HOSTS = ['*']
ROOT_URLCONF = 'oinkbrew_webapp.urls'
WSGI_APPLICATION = 'oinkbrew_webapp.wsgi.application'
LANGUAGE_CODE = 'en-us'
USE_I18N = True
USE_L10N = True
USE_TZ = True
STATIC_URL = '/static/'


INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'djcelery',
    'api'
)


MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'api.views.errors.ProcessExceptionMiddleware'
)


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'oinkbrew',
        'USER': 'oinkuser',
        'PASSWORD': 'Amara',
        'HOST': 'localhost',
        'PORT': '',
        'OPTIONS': {
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'"
        }
    }
}

U_LOGFILE_SIZE = 10 * 1024 * 1024
U_LOGFILE_COUNT = 4

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': "[%(asctime)s] %(levelname)s [%(name)s:%(lineno)s] %(message)s",
            'datefmt': "%d/%b/%Y %H:%M:%S"
        },
        'simple': {
            'format': '%(levelname)s %(message)s'
        },
    },
    'handlers': {
        'api-file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': 'log/oinkbrew-api.log',
            'formatter': 'verbose',
            'maxBytes': U_LOGFILE_SIZE,
            'backupCount': U_LOGFILE_COUNT
        },
        'application-file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': 'log/oinkbrew-application.log',
            'formatter': 'verbose',
            'maxBytes': U_LOGFILE_SIZE,
            'backupCount': U_LOGFILE_COUNT
        },
    },
    'loggers': {
        'django': {
            'handlers': ['application-file'],
            'propagate': True,
            'level': 'INFO',
        },
        'api': {
            'handlers': ['api-file'],
            'level': 'INFO',
        },
    }
}
