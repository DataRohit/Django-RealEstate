from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.views.generic import View
from django.urls import reverse

from realestate.apps.core.models import Couple, House


# Create your views here.
class HomeView(View):
    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            # couple = Couple.objects.filter(homebuyer__user=request.user)
            # house = House.objects.filter(couple=couple)
            # return render(
            #     request, "core/homebuyerHome.html", {"couple": couple, "house": house}
            # )
            return render(request, "core/homebuyerHome.html", {})
        return HttpResponseRedirect(reverse("appauth_login"))
