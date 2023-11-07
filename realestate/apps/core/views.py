# Django imports
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404
from django.core.exceptions import PermissionDenied
from django.utils.decorators import method_decorator
from django.views.generic import View


# App imports
from realestate.apps.appauth.models import User
from realestate.apps.house.models import House
from .models import Couple, Realtor


# Base view for all views
class BaseView(View):
    # Get the list of all allowed user types
    _USER_TYPES_ALLOWED = User._ALL_TYPES_ALLOWED

    # Protected method for the permission check
    def _permission_check(self, request, role, *args, **kwargs):
        return True

    # Dispatch method with login required decorator
    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        # Get the role of the user
        role = request.user.role_object

        # If the user has the role type in the allowed user types
        if role.role_type in self._USER_TYPES_ALLOWED:
            # Check if the user has permission to access the view
            if self._permission_check(request, role, *args, **kwargs):
                # Return the super dispatch method
                return super(BaseView, self).dispatch(request, *args, **kwargs)

        # Raise permission denied exception
        raise PermissionDenied


# View for the home page
class HomeView(BaseView):
    # Method to handle the get request
    def get(self, request, *args, **kwargs):
        # If the user is a realtor
        if Realtor.objects.filter(user=request.user).exists():
            # Return the realtor home page
            return render(request, "core/realtor_home.html")

        # Get the couple of the user
        couple = Couple.objects.filter(homebuyer__user=request.user).first()

        # Filter the houses by the couple
        house = House.objects.filter(couple=couple)

        # Return the homebuyer home page
        return render(
            request, "core/homebuyer_home.html", {"couple": couple, "house": house}
        )


# View for the report page
class ReportView(BaseView):
    # Set the template name
    template_name = "core/report.html"

    # Method to check if the user can view the report for the couple
    def _permission_check(self, request, role, *args, **kwargs):
        # Get the couple id from the kwargs
        couple_id = int(kwargs.get("couple_id", 0))

        # Get the couple object
        get_object_or_404(Couple, id=couple_id)

        # Return the permission check
        return role.can_view_report_for_couple(couple_id)

    # Method to handle the get request
    def get(self, request, *args, **kwargs):
        # Render the template
        return render(request, self.template_name, {})
