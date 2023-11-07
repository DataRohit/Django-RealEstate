from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404
from django.core.exceptions import PermissionDenied
from django.utils.decorators import method_decorator
from django.views.generic import View
from realestate.apps.appauth.models import User
from realestate.apps.house.models import House
from .models import Couple, Realtor


class BaseView(View):
    _USER_TYPES_ALLOWED = User._ALL_TYPES_ALLOWED

    def _permission_check(self, request, role, *args, **kwargs):
        return True

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        role = request.user.role_object
        if role.role_type in self._USER_TYPES_ALLOWED:
            if self._permission_check(request, role, *args, **kwargs):
                return super(BaseView, self).dispatch(request, *args, **kwargs)
        raise PermissionDenied


class HomeView(BaseView):
    def get(self, request, *args, **kwargs):
        if Realtor.objects.filter(user=request.user).exists():
            return render(request, "core/realtor_home.html")

        couple = Couple.objects.filter(homebuyer__user=request.user).first()
        house = House.objects.filter(couple=couple)
        return render(
            request, "core/homebuyer_home.html", {"couple": couple, "house": house}
        )


class ReportView(BaseView):
    template_name = "core/report.html"

    def _permission_check(self, request, role, *args, **kwargs):
        couple_id = int(kwargs.get("couple_id", 0))
        get_object_or_404(Couple, id=couple_id)
        return role.can_view_report_for_couple(couple_id)

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, {})
