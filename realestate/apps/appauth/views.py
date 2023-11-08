# Django imports
from django.conf import settings
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


# App imports
from .forms import HomebuyerSignupForm
from .forms import LoginForm
from .forms import PasswordChangeForm
from .forms import RealtorSignupForm
from realestate.apps.appauth.models import User
from realestate.apps.core.models import Couple
from realestate.apps.core.models import Homebuyer
from realestate.apps.core.models import Realtor
from realestate.apps.pending.models import PendingHomebuyer


# Class based view to handle login
class LoginView(auth_views.LoginView):
    # Set the template name
    template_name = "appauth/general_login.html"

    # Set the form class
    form_class = LoginForm

    # Method to handle the get requests
    def get(self, request, *args, **kwargs):
        # If the user is authenticated
        if request.user.is_authenticated:
            # Redirected to the homepage
            return redirect("home")

        # Render the template with the form
        return render(
            request,
            self.template_name,
            {"form": self.form_class()},
        )

    # Method to handle the post requests
    def post(self, request, *args, **kwargs):
        # Get the email and password from the request
        email = request.POST.get("username")
        password = request.POST.get("password")

        # authenticate user
        user = authenticate(request, email=email, password=password)

        # If the user is authenticated
        if user is not None:
            # If user is active
            if user.is_active:
                # Log the user in
                login(request, user)

                # Send a success message
                messages.success(request, "You're successfully logged in!")

                # Redirect to the homepage
                return redirect("home")

            # If the user is not active
            else:
                # Send a warning message
                messages.warning(
                    request,
                    "Your account is not active, please contact the site admin.",
                )

        # If invalid credentials are provided
        else:
            # Send a error message
            messages.error(
                request,
                "Your email and/or password were incorrect.",
            )

        # Create the context dictionary
        context = {"form": self.form_class()}

        # Render the template
        return render(request, self.template_name, context)


# Class based view to handle the logout
class LogoutView(auth_views.LogoutView):
    # Method to handle the get requests
    def get(self, request, *args, **kwargs):
        # Log the user out
        logout(request)

        # Send a success message
        messages.success(request, "You're successfully logged out!")

        # Redirect to the login page
        return redirect("login")


# Class based view to handle the homebuyer signup
class HomebuyerSignupView(View):
    # Set the template name
    template_name = "appauth/homebuyer_signup.html"

    # Set the form class
    form_class = HomebuyerSignupForm

    # Dispatch method
    def dispatch(self, request, *args, **kwargs):
        # If the user is authenticated
        if request.user.is_authenticated:
            # Redirect to the homepage
            return redirect("home")

        # Get the registration token from the keyword arguments
        registration_token = kwargs.get("registration_token")

        # Get the filtered pending homebuyer for the registration token
        pending_homebuyer_filter = PendingHomebuyer.objects.filter(
            registration_token=registration_token
        )

        # If the pending homebuyer does not exist
        if not pending_homebuyer_filter.exists():
            # Send a error message
            messages.error(request, "Invalid Registration Link.")

            # Redirect to the login page
            return redirect("login")

        # Get the pending homebuyer from the filtered pending homebuyer
        pending_homebuyer = pending_homebuyer_filter.first()

        # If the pending homebuyer is registered
        if pending_homebuyer.registered:
            # Send a info message
            messages.info(
                request,
                (
                    "{email} is already registered.".format(
                        email=pending_homebuyer.email
                    )
                ),
            )

            # Redirect to the login page
            return redirect("login")

        # Call the dispatch method of the parent class
        return super(HomebuyerSignupView, self).dispatch(request, *args, **kwargs)

    # Method to handle the get requests
    def get(self, request, *args, **kwargs):
        # Get the registration token from the keyword arguments
        registration_token = kwargs.get("registration_token")

        # Get pending homebuyer for the registration token
        pending_homebuyer = PendingHomebuyer.objects.get(
            registration_token=registration_token
        )

        # Get the assigned realtor for the pending homebuyer
        realtor = pending_homebuyer.pending_couple.realtor

        # Create the context dictionary
        context = {
            "form": self.form_class(initial={"email": pending_homebuyer.email}),
        }

        # Message to be sent to the user is registered
        msg = (
            f"Welcome, {pending_homebuyer.email}."
            f"You have been invited by {realtor.full_name} ({realtor.email})."
            f"Please fill out the form below to register for the Real Estate App."
        )

        # Send a info message
        messages.info(request, msg)

        # Render the template
        return render(request, self.template_name, context)

    # Method to handle the post requests
    def post(self, request, *args, **kwargs):
        # Get teh registration token from the keyword arguments
        registration_token = kwargs.get("registration_token")

        # Get the pending homebuyer for the registration token
        pending_homebuyer = PendingHomebuyer.objects.get(
            registration_token=registration_token
        )

        # Get the assigned realtor for the pending homebuyer
        realtor = pending_homebuyer.pending_couple.realtor

        # Populate the form with the post data
        form = self.form_class(request.POST)

        # If the form is valid
        if form.is_valid():
            # Get the cleaned data from the form
            cleaned_data = form.cleaned_data

            # Wrap the database operations in a transaction
            with transaction.atomic():
                # Get the email and password from the cleaned data
                email = pending_homebuyer.email
                password = cleaned_data["password1"]

                # Create a new user instance
                user = User.objects.create_user(
                    username=email,
                    email=email,
                    password=password,
                    first_name=cleaned_data["first_name"],
                    last_name=cleaned_data["last_name"],
                    phone=cleaned_data["phone"],
                )

                # Get the pending couple for the pending homebuyer
                pending_couple = pending_homebuyer.pending_couple

                # Copy the couple from the pending couple
                couple = pending_couple.couple

                # If the couple does not exist
                if not couple:
                    # Create a new couple instance
                    couple = Couple.objects.create(realtor=realtor)

                # Create a new homebuyer user
                Homebuyer.objects.create(user=user, couple=couple)

                # If the user is registered
                if pending_couple.registered:
                    # Delete pending homebuyer for the user
                    pending_couple.pendinghomebuyer_set.all().delete()

                    # Delete the pending couple
                    pending_couple.delete()

            # Authenticate the user
            user = authenticate(request, email=email, password=password)

            # Log the user in
            login(request, user)

            # Send a success message
            messages.success(request, "You're successfully registered!")

            # Redirect to the homepage
            return redirect("home")

        # Create the context dictionary
        context = {"form": form}

        # Send a error message
        messages.error(request, "Invalid form data.")

        # Render the template
        return render(request, self.template_name, context)


# Class based view to handle the realtor signup
class RealtorSignupView(View):
    # Set the template name
    template_name = "appauth/realtor_signup.html"

    # Set the form class
    form_class = RealtorSignupForm

    # Dispatch method
    def dispatch(self, request, *args, **kwargs):
        # If the user is authenticated
        if request.user.is_authenticated:
            # Redirect to the homepage
            return redirect("home")

        # Call the dispatch method of the parent class
        return super(RealtorSignupView, self).dispatch(request, *args, **kwargs)

    # Method to handle the get requests
    def get(self, request, *args, **kwargs):
        # Create the context dictionary
        context = {"form": self.form_class()}

        # Render the template
        return render(request, self.template_name, context)

    # Method to handle the post requests
    def post(self, request, *args, **kwargs):
        # Populate the form data with the post data
        form = self.form_class(request.POST)

        # If the form is valid
        if form.is_valid():
            # Get the cleaned data from the form
            cleaned_data = form.cleaned_data

            # Get the email and password from the cleaned data
            email = cleaned_data["email"]
            password = cleaned_data["password1"]

            # Wrap the database operations in a transaction
            with transaction.atomic():
                # Create a new user instance
                user = User.objects.create_user(
                    username=email,
                    email=email,
                    password=password,
                    first_name=cleaned_data["first_name"],
                    last_name=cleaned_data["last_name"],
                    phone=cleaned_data["phone"],
                )

                # Create a new realtor user
                Realtor.objects.create(user=user)

            # Authenticate the user
            user = authenticate(request, username=email, password=password)

            # Log the user in
            login(request, user)

            # Send a success message
            messages.success(request, "You're successfully registered!")

            # Redirect to the homepage
            return redirect("home")

        # Create the context dictionary
        context = {"form": form}

        # Render the template
        return render(request, self.template_name, context)


# Class based view to handle the password change
class PasswordChangeView(auth_views.PasswordChangeView):
    # Set the template name
    template_name = "appauth/password_change.html"

    # Set the form class
    form_class = PasswordChangeForm

    # Set the success url
    success_url = reverse_lazy("login")

    # Method to handle the password change
    def form_valid(self, form):
        # Get the response from the parent class
        response = super().form_valid(form)

        # logout the user
        logout(self.request)

        # Send a success message
        messages.success(self.request, "Your password has been changed successfully!")

        # Return the response
        return response
