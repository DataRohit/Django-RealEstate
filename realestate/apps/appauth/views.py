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

from realestate.apps.appauth.serializers import (
    APIUserSerializer,
    APIHouseSerializer,
    APIHouseParamSerializer,
    APIHouseFullParamSerializer,
)
from realestate.apps.core.models import House, Category, Couple, Grade


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


class APIHouseView(APIView):
    serializer_class = APIHouseSerializer

    def get(self, request):
        hid = self.request.query_params.get("id", None)
        user = self.request.user

        couple = Couple.objects.filter(homebuyer__user=user).first()
        serializer = APIUserSerializer(
            data=request.data, context={"request": self.request}
        )

        if not serializer.is_valid():
            return Response(
                {"code": 201, "message": serializer.errors["non_field_errors"][0]}
            )

        if hid is None:
            houses = []

            houses_queryset = House.objects.filter(couple=couple)

            for h in houses_queryset:
                content = {"id": h.pk, "nickname": h.nickname, "address": h.address}
                houses.append(content)

            query = {"house": houses}
        else:
            paramser = APIHouseParamSerializer(
                data={"id": int(hid)}, context={"request": self.request}
            )
            if paramser.is_valid():
                d = paramser.val()
                if d is not None:
                    return Response(d)
            else:
                return Response({"code": 300, "message": "Format error"})

            h = House.objects.filter(pk=hid)
            category = Category.objects.filter(couple=couple)
            categories = []
            for c in category:
                grade = Grade.objects.filter(category=c, house=h, homebuyer__user=user)
                if grade.count() > 0:
                    content = {
                        "id": c.pk,
                        "summary": c.summary,
                        "score": grade[0].score,
                    }
                    categories.append(content)
            query = {"category": categories}

        return Response(query)

    def put(self, request):
        hid = self.request.query_params.get("id", None)
        cat = self.request.query_params.get("category", None)
        score = self.request.query_params.get("score", None)

        if hid is None or cat is None or score is None:
            return Response({"code": 300, "message": "Format error"})

        paramser = APIHouseFullParamSerializer(
            data={"id": hid, "category": cat, "score": int(score)},
            context={"request": self.request},
        )

        if paramser.is_valid():
            d = paramser.val()
            if d is not None:
                return Response(d)
        else:
            return Response({"code": 300, "message": "Format error"})

        serializer = APIUserSerializer(
            data=request.data, context={"request": self.request}
        )

        if not serializer.is_valid():
            return Response(
                {"code": 201, "message": serializer.errors["non_field_errors"][0]}
            )

        return Response("Waiting for updates")

    def post(self, request):
        serializer = APIUserSerializer(
            data=request.data, context={"request": self.request}
        )

        if not serializer.is_valid():
            return Response(
                {"code": 201, "message": serializer.errors["non_field_errors"][0]}
            )

        couple = Couple.objects.filter(homebuyer__user=request.user)

        data = dict(request.data)

        for key, val in data.items():
            if len(val) == 1:
                data[key] = val[0]

        data["couple"] = couple[0].pk

        ser = APIHouseSerializer(data=data)

        if ser.is_valid(raise_exception=True):
            ser.save()
            ret = ser.validated_data
            content = {"nickname": ret["nickname"], "address": ret["address"]}
            return Response(content)
        else:
            # Will be replaced by serializer error
            return Response({"error": "Format error"})


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
