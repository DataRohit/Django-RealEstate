from django.shortcuts import render, redirect
from django.contrib.auth import views as auth_views
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.views.generic import View
from django.db import transaction
from django.urls import reverse_lazy


from realestate.apps.appauth.forms import (
    LoginForm,
    HomebuyerSignupForm,
    PasswordChangeForm,
)
from realestate.apps.core.models import Couple, Homebuyer
from realestate.apps.appauth.models import User
from realestate.apps.pending.models import PendingHomebuyer


# Create your views here.
class LoginView(auth_views.LoginView):
    # Template for the login page
    template = "registration/login.html"
    form = LoginForm()

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect("home")

        email = password = ""
        return render(
            request,
            self.template,
            {"form": self.form, "email": email},
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


class SignupView(View):
    template_name = "registration/homebuyerSignup.html"

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
                (f"{pending_homebuyer.email} is already registered."),
            )
            return redirect("auth_login")

        return super(SignupView, self).dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        token = kwargs.get("registration_token")

        pending_homebuyer = PendingHomebuyer.objects.get(registration_token=token)
        realtor = pending_homebuyer.pending_couple.realtor

        context = {
            "signup_form": HomebuyerSignupForm(
                initial={"email": pending_homebuyer.email},
            ),
            "registration_token": token,
        }

        msg = f"""Welcome, {pending_homebuyer.email}.
        You have been invited by {realtor.full_name} ({realtor.email}).
        Please fill out the form below to register for the Real Estate App.
        """
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
                password = cleaned_data["password1"]

                user = User.objects.create_user(
                    username=email,
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
            "signup_form": form,
            "registration_token": token,
        }

        return render(request, self.template_name, context)


class PasswordChangeView(auth_views.PasswordChangeView):
    form_class = PasswordChangeForm
    template_name = "registration/password_change.html"
    success_url = reverse_lazy("login")

    def form_valid(self, form):
        response = super().form_valid(form)
        logout(self.request)
        return response
