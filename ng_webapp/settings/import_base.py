from ng_webapp.settings.prod import *


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

    },
}


DATABASES = {
    'default': {
        'STORAGE_ENGINE': 'MyISAM / INNODB / ETC',
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'pplingodb',
        'USER': 'appuser',
        'PASSWORD': 'DB4lingo.com',
        'HOST': 'localhost',
        'PORT': '3306',
        # 'CONN_MAX_AGE': 3600,
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
    'pplingodb': {
        'STORAGE_ENGINE': 'MyISAM / INNODB / ETC',
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'pplingodb',
        'USER': 'appuser',
        'PASSWORD': 'DB4lingo.com',
        'HOST': 'localhost',
        'PORT': '3306',
        # 'CONN_MAX_AGE': 3600,
    },
    'manage': {
        'STORAGE_ENGINE': 'MyISAM / INNODB / ETC',
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'managedb',
        'USER': 'manage',
        'PASSWORD': 'DB4manage.com',
        'HOST': 'localhost',
        'PORT': '3306',
    }
}
