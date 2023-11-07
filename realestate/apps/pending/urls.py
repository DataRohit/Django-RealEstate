from django.urls import path
from .views import InviteHomebuyerView

urlpatterns = [
    path("invite-homebuyer/", InviteHomebuyerView.as_view(), name="invite-homebuyer"),
]
