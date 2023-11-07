# Django imports
from django.contrib import messages
from django.db import transaction
from django.shortcuts import redirect
from django.shortcuts import render


# App imports
from realestate.apps.appauth.models import User
from realestate.apps.core.views import BaseView
from .forms import InviteHomebuyerForm
from .models import PendingCouple
from .models import PendingHomebuyer


# View to handle the invite homebuyer page
class InviteHomebuyerView(BaseView):
    # Get the allower user types
    _USER_TYPES_ALLOWED = User._REALTOR_ONLY

    # Set the template name
    template_name = "pending/invite_homebuyer.html"

    # Set the form class
    form_class = InviteHomebuyerForm

    # Method to invite a homebuyer
    def _invite_homebuyer(self, request, pending_couple, email):
        # Create the pending homebuyer
        homebuyer = PendingHomebuyer.objects.create(
            email=email, pending_couple=pending_couple
        )

        # Send the invite email
        homebuyer.send_email_invite(request)

        # Send a success message
        messages.success(request, "Email invite sent to {email}".format(email=email))

    # method the handle the get request
    def get(self, request, *args, **kwargs):
        # Prepare the context
        context = {"form": self.form_class()}

        # Render the template
        return render(request, self.template_name, context)

    # Method to handle the post request
    def post(self, request, *args, **kwargs):
        # Populate the form with data
        form = self.form_class(request.POST)

        # If the form is valid
        if form.is_valid():
            # Get the email addresses for the couple
            first_email = form.cleaned_data.get("first_email")
            second_email = form.cleaned_data.get("second_email")

            # With a transaction
            with transaction.atomic():
                # Create a pending couple with the pending users
                pending_couple = PendingCouple.objects.create(
                    realtor=request.user.realtor
                )

                # Send the invitations to both the homebuyers
                self._invite_homebuyer(request, pending_couple, first_email)
                self._invite_homebuyer(request, pending_couple, second_email)

            # Redirect to the invite homebuyer page
            return redirect("invite-homebuyers")

        # Prepare the context
        context = {"form": form}

        # Render the template
        return render(request, self.template_name, context)
