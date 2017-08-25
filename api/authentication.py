from django.contrib.auth import get_user_model
from rest_framework import authentication
from rest_framework import exceptions

class KongUpstreamAuthentication(authentication.BaseAuthentication):
    def authenticate(self, request):

        is_anon = request.META.get('HTTP_X_ANONYMOUS_CONSUMER', False) == 'true'
        user = AnonymousUser()
        if not is_anon:
            user_id = request.META.get('HTTP_X_AUTHENTICATED_USERID', False)
            user = get_user_model()()
            user.id = user_id
            user.username = user_id
            user.first_name = user_id
            user.last_name = user_id
            return (user, None)
        return None