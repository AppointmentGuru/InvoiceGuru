from django.contrib.auth.models import AnonymousUser
from django.contrib.auth import get_user_model

class KongUserMiddleware(object):
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):

        not_anonomous_user = request.META.get('HTTP_X_ANONYMOUS_CONSUMER', True) == 'false'

        user = AnonymousUser()
        if not_anonomous_user:
            user_id = request.META.get('HTTP_X_AUTHENTICATED_USERID', False)
            user = get_user_model()()
            user.id = user_id
            user.username = user_id
            user.first_name = user_id
            user.last_name = user_id

        request.user = user
        response = self.get_response(request)
        return response