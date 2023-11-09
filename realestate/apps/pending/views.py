# Django imports
from django.contrib import messages
from django.db import transaction
from django.shortcuts import redirect
from django.shortcuts import render


# App imports
from .forms import InviteHomebuyerForm
from .models import PendingCouple
from .models import PendingHomebuyer
from realestate.apps.appauth.models import User
from realestate.apps.core.views import BaseView


# View to handle the invite homebuyer page
class InviteHomebuyerView(BaseView):
    # Get the allower user types
    _USER_TYPES_ALLOWED = User._REALTOR_ONLY

    # Set the template name
    template_name = "pending/invite_homebuyer.html"

    # Set the form class
    form_class = InviteHomebuyerForm

    # Method to invite a homebuyer
    def _invite_homebuyer(self, request, pending_couple, email, first_name, last_name):
        # Create the pending homebuyer
        homebuyer = PendingHomebuyer.objects.create(
            email=email,
            first_name=first_name,
            last_name=last_name,
            pending_couple=pending_couple,
        )

        # Send the invite email
        homebuyer.send_email_invite(request)

        # Send a success message
        messages.success(request, "Email invite sent to {email}".format(email=email))

    # method the handle the get request
    def get(self, request, *args, **kwargs):
        # Prepare the context
        context = {"form_1": self.form_class(), "form_2": self.form_class()}

        # Render the template
        return render(request, self.template_name, context)

    # Method to handle the post request
    def post(self, request, *args, **kwargs):
        # Get the data from request
        emails = request.POST.getlist("email")
        first_names = request.POST.getlist("first_name")
        last_names = request.POST.getlist("last_name")

        # Populate the form with data
        form_1 = self.form_class(
            data={
                "email": emails[0],
                "first_name": first_names[0],
                "last_name": last_names[0],
            }
        )
        form_2 = self.form_class(
            data={
                "email": emails[1],
                "first_name": first_names[1],
                "last_name": last_names[1],
            }
        )

        # If the form is valid
        if form_1.is_valid() and form_2.is_valid():
            # Check if the emails are not the same
            if emails[0] == emails[1]:
                # Send an error message
                messages.error(request, "Please enter two different email addresses.")

                # Redirect to the invite homebuyer page
                return redirect("invite-homebuyers")

            # With a transaction
            with transaction.atomic():
                # Create a pending couple with the pending users
                pending_couple = PendingCouple.objects.create(
                    realtor=request.user.realtor,
                )

                # Send the invitations to both the homebuyers
                self._invite_homebuyer(
                    request, pending_couple, emails[0], first_names[0], last_names[0]
                )
                self._invite_homebuyer(
                    request, pending_couple, emails[1], first_names[1], last_names[1]
                )

            # Redirect to the invite homebuyer page
            return redirect("invite-homebuyers")

        # Prepare the context
        context = {"form_1": self.form_class(), "form_2": self.form_class()}

        # Render the template
        return render(request, self.template_name, context)
