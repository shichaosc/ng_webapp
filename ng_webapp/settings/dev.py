from ng_webapp.base import *


DEBUG = False

HOST_NAME = '127.0.0.1:8000'

JAVA_DOMAIN = 'dev.opsapi.pplingo.com'

STUDENT_USER_DOMAIN = 'student.api.pplingo.com'

ALLOWED_HOSTS = ['*']

AGORA_VIDEO_APP_ID = '973fa82dd6e9476ebf597ae2b8245a27'
AGORA_APP_ID = '339fbcf5e166448cab9593c741398507'
AGORA_APP_CERTIFICATE = '9bbbd62e0b344a458dbc8c73afa0f290'

MEDIA_URL = "https://s3-us-west-1.amazonaws.com/stage.media.pplingo.com/"

ROOT_URLCONF = 'ng_webapp.urls'

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s'
        },
        'simple': {
            'format': '%(levelname)s %(message)s'
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
        'file1': {
            'class': 'ng_webapp.log_handler.HxTimedRotatingFileHandler',
            'filename': '/data/logs/ng_webapp/scripts/script.log',
            'when': 'midnight',
            # 时间间隔
            'interval': 1,
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': os.getenv('DJANGO_LOG_LEVEL', 'INFO'),
        },
        'pplingo.ng_webapp.scheduler': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'formatter': 'verbose',
        },
        'pplingo.ng_webapp.tutor': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'formatter': 'verbose',
        },
        'pplingo.ng_webapp.classroom': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'formatter': 'verbose',
        },
        'pplingo.ng_webapp.course': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'formatter': 'verbose',
        },
        'pplingo.ng_webapp.activity': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'formatter': 'verbose',
        },
        'pplingo.ng_webapp.ambassador': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'formatter': 'verbose',
        },
        'pplingo.ng_webapp.common': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'formatter': 'verbose',
        },
        'pplingo.ng_webapp.student': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'formatter': 'verbose',
        },
        'pplingo.ng_webapp.finance': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'formatter': 'verbose',
        },
        'pplingo.ng_webapp.users': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'formatter': 'verbose',
        },
        'django.db.backends': {
             'handlers': ['console'],
             'propagate': True,
             'level': 'DEBUG',
         },
    },
}

CRONTAB_DJANGO_SETTINGS_MODULE = 'ng_webapp.settings.dev'


DATABASES = {
    'default': {
        'STORAGE_ENGINE': 'MyISAM / INNODB / ETC',
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'ng_webapp',
        'USER': 'lingoace',
        'PASSWORD': 'DB4lingo.com',
        'HOST': 'localhost',
        'PORT': '3306',
        # 'ATOMIC_REQUESTS': True,
        # 'CONN_MAX_AGE': 600,
    },
    'lingoace': {
        'STORAGE_ENGINE': 'MyISAM / INNODB / ETC',
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'lingoacedb',
        'USER': 'lingoace',
        'PASSWORD': 'DB4lingo.com',
        'HOST': 'localhost',
        'PORT': '3306',
        # 'CONN_MAX_AGE': 3600,
    },
    'explorer_query': {
        'STORAGE_ENGINE': 'MyISAM / INNODB / ETC',
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'lingoacedb',
        'USER': 'lingoace',
        'PASSWORD': 'DB4lingo.com',
        'HOST': 'localhost',
        'PORT': '3306'
    }
}


