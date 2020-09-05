from ng_webapp.base import *
from datetime import datetime

HOST_NAME = 'test.member.lingo-ace.com'

JAVA_DOMAIN = '127.0.0.1:8090'

STUDENT_USER_DOMAIN = 'student.api.pplingo.com'

ALLOWED_HOSTS = [HOST_NAME, JAVA_DOMAIN, 'ngwebapp', '*']

DEBUG = False

PAYPAL_TEST = True

AGORA_VIDEO_APP_ID = '973fa82dd6e9476ebf597ae2b8245a27'
AGORA_APP_ID = '339fbcf5e166448cab9593c741398507'
AGORA_APP_CERTIFICATE = '9bbbd62e0b344a458dbc8c73afa0f290'

STATIC_ROOT = "/data/static_file/static/"

MEDIA_ROOT = "/data/static_file/media/"

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
            # 'level': 'DEBUG',
            'class': 'ng_webapp.log_handler.HxTimedRotatingFileHandler',
            'filename': '/data/logs/ng_webapp/debug.log',
            'when': 'midnight',
            # 时间间隔
            'interval': 1,

            'formatter': 'verbose',
        },
        'file': {
            'class': 'ng_webapp.log_handler.HxTimedRotatingFileHandler',
            'filename': '/data/logs/ng_webapp/debug.log',
            'when': 'midnight',
            # 时间间隔
            'interval': 1,

            'formatter': 'verbose',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'level': os.getenv('DJANGO_LOG_LEVEL', 'DEBUG'),
        },
        'pplingo.ng_webapp.scheduler': {
            'handlers': ['file'],
            'level': os.getenv('DJANGO_LOG_LEVEL', 'DEBUG'),
        },
        'pplingo.ng_webapp.tutor': {
            'handlers': ['file'],
            'level': os.getenv('DJANGO_LOG_LEVEL', 'DEBUG'),
        },
        'pplingo.ng_webapp.classroom': {
            'handlers': ['file'],
            'level': os.getenv('DJANGO_LOG_LEVEL', 'DEBUG'),
        },
        'pplingo.ng_webapp.course': {
            'handlers': ['file'],
            'level': os.getenv('DJANGO_LOG_LEVEL', 'DEBUG'),
        },
        'pplingo.ng_webapp.activity': {
            'handlers': ['file'],
            'level': os.getenv('DJANGO_LOG_LEVEL', 'DEBUG'),
        },
        'pplingo.ng_webapp.ambassador': {
            'handlers': ['file'],
            'level': os.getenv('DJANGO_LOG_LEVEL', 'DEBUG'),
        },
        'pplingo.ng_webapp.student': {
            'handlers': ['file'],
            'level': os.getenv('DJANGO_LOG_LEVEL', 'DEBUG'),
        },
        'pplingo.ng_webapp.users': {
            'handlers': ['file'],
            'level': os.getenv('DJANGO_LOG_LEVEL', 'DEBUG'),
        },
        'pplingo.ng_webapp.finance': {
            'handlers': ['file'],
            'level': os.getenv('DJANGO_LOG_LEVEL', 'DEBUG'),
        }
    },
}

ROOT_URLCONF = 'ng_webapp.urls'

CRONTAB_DJANGO_SETTINGS_MODULE = 'ng_webapp.settings.test'


DATABASES = {
    'default': {
        'STORAGE_ENGINE': 'MyISAM / INNODB / ETC',
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'pplingo_new',
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
        'CONN_MAX_AGE': 100,
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
