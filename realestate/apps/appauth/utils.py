from datetime import datetime
from django.conf import settings


def jwt_payload_handler(user):
    return {
        "user_id": user.pk,
        "email": user.email,
        "firstname": user.first_name,
        "lastname": user.last_name,
        "exp": datetime.now() + settings.SIMPLE_JWT["ACCESS_TOKEN_LIFETIME"],
    }


def jwt_response_payload_handler(token, user=None, request=None):
    return {
        "token": token,
        "exp-time": datetime.now() + settings.SIMPLE_JWT["ACCESS_TOKEN_LIFETIME"],
    }
