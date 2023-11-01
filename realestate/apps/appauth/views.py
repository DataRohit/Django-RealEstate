from django.shortcuts import render, redirect
from django.contrib.auth import views as auth_views
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages

from realestate.apps.appauth.forms import LoginForm
from realestate.apps.appauth.serializers import APIUserSerializer
from realestate.apps.appauth.utils import jwt_payload_handler

from rest_framework_simplejwt.authentication import JWTAuthentication

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response


# Create your views here.
class APIUserInfoView(APIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (JWTAuthentication,)

    def get(self, request, *args, **kwargs):
        serializer = APIUserSerializer(data=request.data, context={"request": request})

        if serializer.is_valid():
            user = request.user
            response_data = jwt_payload_handler(user)

            return Response(response_data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


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
