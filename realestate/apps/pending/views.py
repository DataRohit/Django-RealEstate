from django.contrib import messages
from django.db import transaction
from django.contrib.auth import authenticate, login
from django.shortcuts import redirect, render
from django.views.generic import View

from realestate.apps.appauth.models import User
from realestate.apps.core.models import Couple, Homebuyer
from realestate.apps.core.views import BaseView
from realestate.apps.pending.forms import InviteHomebuyerForm, SignupForm
from realestate.apps.pending.models import PendingCouple, PendingHomebuyer


# Create your views here.
class InviteHomebuyerView(BaseView):
    _USER_TYPES_ALLOWED = User._REALTOR_ONLY
    template_name = "pending/inviteHomebuyer.html"

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


class SignupView(View):
    template_name = "pending/signup.html"

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated():
            return redirect("home")

        token = kwargs.get("registration_token")

        pending_homebuyer_filter = PendingHomebuyer.objects.filter(
            registration_token=token
        )
        if not pending_homebuyer_filter.exists():
            messages.error(request, "Invalid Registration Link.")
            return redirect("auth_login")

        pending_homebuyer = pending_homebuyer_filter.first()
        if pending_homebuyer.registered:
            messages.info(
                request,
                (f"{pending_homebuyer.email} is already registered."),
            )
            return redirect("auth_login")

        return super(SignupView, self).dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        token = kwargs.get("registration_token")

        pending_homebuyer = PendingHomebuyer.objects.get(registration_token=token)
        realtor = pending_homebuyer.pending_couple.realtor

        context = {
            "signup_form": SignupForm(initial={"email": pending_homebuyer.email}),
            "registration_token": token,
        }

        msg = (
            f"Welcome, {pending_homebuyer.email}.<br>You have been invited by {realtor.full_name} "
            f"({realtor.email}).<br>Please fill out the form below to "
            f"register for the Real Estate App."
        )
        messages.info(request, msg)
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        token = kwargs.get("registration_token")
        pending_homebuyer = PendingHomebuyer.objects.get(registration_token=token)
        realtor = pending_homebuyer.pending_couple.realtor

        form = SignupForm(request.POST)

        if form.is_valid():
            cleaned_data = form.cleaned_data

            with transaction.atomic():
                email = pending_homebuyer.email
                password = cleaned_data["password"]

                user = User.objects.create_user(
                    username=email,
                    password=password,
                    first_name=cleaned_data["first_name"],
                    last_name=cleaned_data["last_name"],
                    phone=cleaned_data["phone"],
                )

                pending_couple = pending_homebuyer.pending_couple

                couple = pending_couple.couple

                if not couple:
                    couple = Couple.objects.create(realtor=realtor)

                Homebuyer.objects.create(user=user, couple=couple)

                if pending_couple.registered:
                    pending_couple.pendinghomebuyer_set.all().delete()
                    pending_couple.delete()

            user = authenticate(email=email, password=password)
            login(request, user)

            return redirect("home")

        context = {
            "signup_form": form,
            "registration_token": token,
        }

        return render(request, self.template_name, context)
