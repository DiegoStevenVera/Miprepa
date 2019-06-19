# coding=utf-8
import datetime
from django.utils.encoding import smart_text
from django.utils.timezone import now
from rest_framework.authentication import TokenAuthentication, get_authorization_header
from rest_framework import exceptions
from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from rest_framework_jwt.settings import api_settings
from django.utils.translation import ugettext as _


class ExpiringTokenAuthentication(TokenAuthentication):
    def authenticate_credentials(self, key):
        try:
            token = self.model.objects.get(key=key)
        except self.model.DoesNotExist:
            raise exceptions.AuthenticationFailed(u'Token inválido')
        if not token.user.is_active:
            raise exceptions.AuthenticationFailed('Usuario inactivo o eliminado')
        utc_now = now()
        if token.created < utc_now - datetime.timedelta(days=30):
            raise exceptions.AuthenticationFailed('Token expirado')
        return token.user, token


class OwnJSONWebTokenAuthentication(JSONWebTokenAuthentication):
    def get_jwt_value(self, request):
        token = request.query_params.get('token')
        if token:
            return token
        else:
            auth = get_authorization_header(request).split()
            auth_header_prefix = api_settings.JWT_AUTH_HEADER_PREFIX.lower()

            if not auth or smart_text(auth[0].lower()) != auth_header_prefix:
                return None

            if len(auth) == 1:
                msg = _('Invalid Authorization header. No credentials provided.')
                raise exceptions.AuthenticationFailed(msg)
            elif len(auth) > 2:
                msg = _('Invalid Authorization header. Credentials string '
                        'should not contain spaces.')
                raise exceptions.AuthenticationFailed(msg)

            return auth[1]
