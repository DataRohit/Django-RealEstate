from django.contrib import messages
from django.contrib.auth import authenticate
from django.contrib.auth import login
from django.contrib.auth import logout
from django.contrib.auth import views as auth_views
from django.db import transaction
from django.shortcuts import redirect
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import View


from realestate.apps.appauth.forms import HomebuyerSignupForm
from realestate.apps.appauth.forms import LoginForm
from realestate.apps.appauth.forms import PasswordChangeForm
from realestate.apps.appauth.forms import RealtorSignupForm
from realestate.apps.appauth.models import User
from realestate.apps.core.models import Couple
from realestate.apps.core.models import Homebuyer
from realestate.apps.core.models import Realtor
from realestate.apps.pending.models import PendingHomebuyer


class LoginView(auth_views.LoginView):
    template = "appauth/general_login.html"
    form = LoginForm()

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect("home")

        return render(
            request,
            self.template,
            {"form": self.form},
        )

    def post(self, request, *args, **kwargs):
        email = request.POST.get("username")
        password = request.POST.get("password")

        # authenticate user
        user = authenticate(email=email, password=password)

        if user is not None:
            # If user is active, log them in
            if user.is_active:
                login(request, user)
                messages.success(request, "You're successfully logged in!")
                return redirect("home")

            else:
                messages.warning(
                    request,
                    "Your account is not active, please contact the site admin.",
                )

        # Invalid login details
        else:
            messages.error(
                request,
                "Your email and/or password were incorrect.",
            )

        # Create the context dictionary
        context = {"form": self.form, "email": email}

        # Render the template
        return render(request, self.template, context)


class LogoutView(auth_views.LogoutView):
    def get(self, request, *args, **kwargs):
        # Log the user out
        logout(request)

        # Redirect to the homepage
        return redirect("home")


class HomebuyerSignupView(View):
    template_name = "appauth/homebuyer_signup.html"

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
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
                (
                    "{email} is already registered.".format(
                        email=pending_homebuyer.email
                    )
                ),
            )
            return redirect("auth_login")
        return super(HomebuyerSignupView, self).dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        token = kwargs.get("registration_token")
        pending_homebuyer = PendingHomebuyer.objects.get(registration_token=token)
        realtor = pending_homebuyer.pending_couple.realtor

        context = {
            "registration_token": token,
            "signup_form": HomebuyerSignupForm(
                initial={"email": pending_homebuyer.email}
            ),
        }

        msg = (
            "Welcome, {email}.<br>You have been invited by {realtor_name} "
            "({realtor_email}).<br>Please fill out the form below to "
            "register for the Real Estate App.".format(
                email=pending_homebuyer.email,
                realtor_name=realtor.full_name,
                realtor_email=realtor.email,
            )
        )
        messages.info(request, msg)
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        token = kwargs.get("registration_token")
        pending_homebuyer = PendingHomebuyer.objects.get(registration_token=token)
        realtor = pending_homebuyer.pending_couple.realtor
        form = HomebuyerSignupForm(request.POST)

        if form.is_valid():
            cleaned_data = form.cleaned_data
            with transaction.atomic():
                email = pending_homebuyer.email
                password = cleaned_data["password"]

                user = User.objects.create_user(
                    email=email,
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
            "registration_token": token,
            "signup_form": form,
        }
        return render(request, self.template_name, context)


class RealtorSignupView(View):
    template_name = "appauth/realtor_signup.html"

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect("home")
        return super(RealtorSignupView, self).dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        context = {"signup_form": RealtorSignupForm()}
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        signup_form = RealtorSignupForm(request.POST)
        if signup_form.is_valid():
            cleaned_data = signup_form.cleaned_data
            email = cleaned_data["email"]
            password = cleaned_data["password1"]

            with transaction.atomic():
                user = User.objects.create_user(
                    username=email,
                    email=email,
                    password=password,
                    first_name=cleaned_data["first_name"],
                    last_name=cleaned_data["last_name"],
                    phone=cleaned_data["phone"],
                )

                Realtor.objects.create(user=user)

            user = authenticate(username=email, password=password)
            _login(request, user)
            return redirect("home")

        context = {"signup_form": signup_form}
        return render(request, self.template_name, context)


class PasswordChangeView(auth_views.PasswordChangeView):
    form_class = PasswordChangeForm
    template_name = "appauth/password_change.html"
    success_url = reverse_lazy("login")

    def form_valid(self, form):
        response = super().form_valid(form)
        logout(self.request)
        return response
