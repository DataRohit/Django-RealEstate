from django.shortcuts import render, redirect
from django.contrib.auth import views as auth_views
from django.contrib.auth import authenticate, login, logout
from django.urls import reverse
from realestate.apps.appauth.forms import LoginForm


# Create your views here.
class LoginView(auth_views.LoginView):
    # Template for the login page
    template = "registration/login.html"
    form = LoginForm()

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect(reverse("home"))

        state = (False, "")
        username = password = ""
        return render(
            request,
            self.template,
            {"form": self.form, "state": state, "username": username},
        )

    def post(self, request, *args, **kwargs):
        username = request.POST.get("username")
        password = request.POST.get("password")

        # authenticate user
        user = authenticate(username=username, password=password)

        if user is not None:
            # If user is active, log them in
            if user.is_active:
                login(request, user)
                state = (True, "You're successfully logged in!")
                return redirect(reverse("home"))

            else:
                state = (
                    False,
                    "Your account is not active, please contact the site admin.",
                )

        # Invalid login details
        else:
            state = (False, "Your username and/or password were incorrect.")

        # Create the context dictionary
        context = {"form": self.form, "state": state, "username": username}

        # Render the template
        return render(request, self.template, context)


class LogoutView(auth_views.LogoutView):
    def get(self, request, *args, **kwargs):
        # Log the user out
        logout(request)

        # Redirect to the homepage
        return redirect(reverse("home"))
