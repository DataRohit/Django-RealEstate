from django.shortcuts import render
from django.views.generic import View
from django.http import HttpResponseRedirect
from django.urls import reverse


# Create your views here.
class HomeView(View):
    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return render(request, "core/homebuyerHome.html", {})
        return HttpResponseRedirect(reverse("appauth_login"))
