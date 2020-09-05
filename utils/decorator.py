from signals.handler import log_signal
from functools import wraps
from django.core.handlers.wsgi import WSGIRequest
from rest_framework.request import Request

def log_decorator(signal):

    def log_opration(func):

        @wraps(func)
        def wrapper(*args, **kwargs):
            request = list(filter(lambda arg: isinstance(arg, (WSGIRequest, Request)), args))
            response = func(*args, **kwargs)

            if response.status_code in (200, 201):
                signal.send(sender=None, request=request[0], opration=flag, **kwargs)
            return response
        return wrapper
    return log_opration




