"""
WSGI config for pplingo project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.9/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application
# from raven.contrib.django.raven_compat.middleware.wsgi import Sentry
import pymysql

pymysql.install_as_MySQLdb()

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ng_webapp.settings.prod")

# application = Sentry(get_wsgi_application())

application = get_wsgi_application()
