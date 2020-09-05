from django.contrib.auth import login
from django.conf import settings

from rest_framework.authentication import TokenAuthentication
from rest_framework import exceptions

class TokenAuthenticationMiddleware(object):
    """
    This authentication function will capture token, and convert it to session model
    """
    def process_request(self, request):
        token = None
        try:
            token = request.GET['token']
        except :
            pass

        if token:
            try:
                token_auth = TokenAuthentication()
                user, t = token_auth.authenticate_credentials(token)
                """
                this is only good for single backend case. 
                """
                for backend_path in settings.AUTHENTICATION_BACKENDS:
                    user.backend = backend_path

                login(request, user)
            except (exceptions.AuthenticationFailed):
                pass
        pass

class DeviceMiddleware(object):
    """
    This device recognition function will capture token, and convert it to session model
    """
    def process_request(self, request):
        container = None
        try:
            container = request.GET['container']
        except :
            pass

        if container:
            request.session['container'] = container
        pass
