from django.contrib import messages
from django.db import transaction
from django.shortcuts import redirect
from django.shortcuts import render

from realestate.apps.appauth.models import User
from realestate.apps.core.views import BaseView
from realestate.apps.pending.forms import InviteHomebuyerForm
from realestate.apps.pending.models import PendingCouple
from realestate.apps.pending.models import PendingHomebuyer


# Create your views here.
class InviteHomebuyerView(BaseView):
    _USER_TYPES_ALLOWED = User._REALTOR_ONLY
    template_name = "pending/invite_homebuyer.html"

    def _invite_homebuyer(self, request, pending_couple, email):
        homebuyer = PendingHomebuyer.objects.create(
            email=email, pending_couple=pending_couple
        )
        homebuyer.send_email_invite(request)
        messages.success(request, "Email invite sent to {email}".format(email=email))

    def get(self, request, *args, **kwargs):
        context = {"invite_homebuyer_form": InviteHomebuyerForm()}
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        form = InviteHomebuyerForm(request.POST)
        if form.is_valid():
            first_email = form.cleaned_data.get("first_email")
            second_email = form.cleaned_data.get("second_email")

            with transaction.atomic():
                pending_couple = PendingCouple.objects.create(
                    realtor=request.user.realtor
                )
                self._invite_homebuyer(request, pending_couple, first_email)
                self._invite_homebuyer(request, pending_couple, second_email)
            return redirect("invite")

        context = {"invite_homebuyer_form": form}
        return render(request, self.template_name, context)
