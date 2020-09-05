from ng_webapp.base import *
from datetime import datetime

# JAVA_DOMAIN = 'api.lingoace.com'
# JAVA_DOMAIN = '127.0.0.1:8080'
JAVA_DOMAIN = 'us-prod-inner.api.lingoace.com'

HOST_NAME = 'man.lingoace.com'

STUDENT_USER_DOMAIN = 'student.lingoace.com'

ALLOWED_HOSTS = [HOST_NAME, JAVA_DOMAIN, 'ngwebapp', 'man.b8uybizbr5u1yeom.lingo-ace.com', '127.0.0.1', 'localhost', '*']

DEBUG = False


AGORA_VIDEO_APP_ID = '892359b8ca1948de9678a652dbe365a4'
AGORA_APP_ID = '341c6c0733234da384218cfbc4bb30db'
AGORA_APP_CERTIFICATE = '3a9e88acf8534ef9a333c9877e020305'


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
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
        'file': {
            # 'level': 'DEBUG',
            # 'class': 'logging.handlers.RotatingFileHandler',
            # 'filename': '/data/logs/ng_webapp/debug.log',
            # 'maxBytes': 1024*1024*15, # 15MB
            # 'backupCount': 10,
            # 'formatter': 'verbose',
            # 'level': 'DEBUG',
            'class': 'ng_webapp.log_handler.HxTimedRotatingFileHandler',
            'filename': '/data/logs/ng_webapp/debug.log',
            # 'maxBytes': 1024*1024*50,  # 15MB
            # 'backupCount': 10,
            'when': 'midnight',
            # 时间间隔
            'interval': 1,

            'formatter': 'verbose',
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
        },
        'pplingo.ng_webapp.scripts': {
            'handlers': ['file1'],
            'level': os.getenv('DJANGO_LOG_LEVEL', 'DEBUG'),
        },

    },
}

MEDIA_URL = "https://s3.cn-north-1.amazonaws.com.cn/media.ppchinese.com/"

# SENTRY_DSN = 'http://2c13a240bd1e46d39e13e8b058d703f7:f1f1f251e55845bf8a92cbf81c15a181@stage.api.pplingo.com/17'
#
# RAVEN_CONFIG = {
#     'dsn': SENTRY_DSN,
# }

DATABASES = {
    'default': {
        'STORAGE_ENGINE': 'MyISAM / INNODB / ETC',
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'ng_webapp',
        'USER': 'lingoace',
        'PASSWORD': 'DB4lingo.com',
        'HOST': 'DB_SERVER',
        'PORT': '3306',
        # 'ATOMIC_REQUESTS': True,
        # 'CONN_MAX_AGE': 3600,
    },
    'lingoace': {
        'STORAGE_ENGINE': 'MyISAM / INNODB / ETC',
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'lingoacedb',
        'USER': 'lingoace',
        'PASSWORD': 'DB4lingo.com',
        'HOST': 'DB_SERVER',
        'PORT': '3306',
        'CONN_MAX_AGE': 100,
        # 'CONN_MAX_AGE': 3600,
    },
    'manage': {
        'STORAGE_ENGINE': 'MyISAM / INNODB / ETC',
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'managedb',
        'USER': 'lingoace',
        'PASSWORD': 'DB4lingo.com',
        'HOST': 'DB_SERVER',
        'PORT': '3306',
    },
    'explorer_query': {
        'STORAGE_ENGINE': 'MyISAM / INNODB / ETC',
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'lingoacedb',
        'USER': 'lingoace',
        'PASSWORD': 'DB4lingo.com',
        'HOST': 'DIRECT_SQL_DB_SERVER',
        'PORT': '3306'
    }
}
