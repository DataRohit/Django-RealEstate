from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.core.exceptions import PermissionDenied
from django.utils.decorators import method_decorator
from django.views.generic import View

from realestate.apps.core.models import House, Couple, Realtor
from realestate.apps.appauth.models import User


class BaseView(View):
    _USER_TYPES_ALLOWED = User._ALL_TYPES_ALLOWED

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        role_type = request.user.role_object.role_type
        if role_type in self._USER_TYPES_ALLOWED:
            return super().dispatch(request, *args, **kwargs)
        raise PermissionDenied


class HomeView(BaseView):
    def get(self, request, *args, **kwargs):
        if Realtor.objects.filter(user=request.user).exists():
            return render(request, "core/realtorHome.html")

        couple = Couple.objects.filter(homebuyer__user=request.user).first()
        house = House.objects.filter(couple=couple)
        return render(
            request, "core/homebuyerHome.html", {"couple": couple, "house": house}
        )
