from django.shortcuts import render
from django.views.generic import View
from django.contrib.auth import authenticate, login


# Create your views here.
class HomeView(View):
    def get(self, request, *args, **kwargs):
        return render(request, "core/homebuyerHome.html", {})


class LoginView(View):
    def get(self, request, *args, **kwargs):
        state = "Please log in below..."
        username = password = ""
        return render(request, "core/auth.html", {"state": state, "username": username})

    def post(self, request, *args, **kwargs):
        username = request.POST.get("username")
        password = request.POST.get("password")

        # authenticate user
        user = authenticate(username=username, password=password)

        if user is not None:
            # If user is active, log them in
            if user.is_active:
                login(request, user)
                state = "You're successfully logged in!"

            else:
                state = "Your account is not active, please contact the site admin."

        # Invalid login details
        else:
            state = "Your username and/or password were incorrect."

        return render(request, "core/auth.html", {"state": state, "username": username})
