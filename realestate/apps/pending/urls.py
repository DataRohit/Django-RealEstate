# Django imports
from django.urls import path


# Import the views
from .views import InviteHomebuyerView


# Add the urls patters for the user
urlpatterns = [
    path("invite-homebuyers/", InviteHomebuyerView.as_view(), name="invite-homebuyers"),
]
