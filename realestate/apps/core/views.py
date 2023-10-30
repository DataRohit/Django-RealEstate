from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.views.generic import View

from realestate.apps.core.models import House, Couple


class BaseView(View):
    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(BaseView, self).dispatch(request, *args, **kwargs)


class HomeView(BaseView):
    def get(self, request, *args, **kwargs):
        # couple = Couple.objects.filter(homebuyer__user=request.user)
        # house = House.objects.filter(couple=couple)
        # return render(
        #     request, "core/homebuyerHome.html", {"couple": couple, "house": house}
        # )

        return render(request, "core/homebuyerHome.html", {})
