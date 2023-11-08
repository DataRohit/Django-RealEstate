# Django imports
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404
from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.views.generic import View


# App imports
from .models import Couple
from .models import Realtor
from realestate.apps.appauth.models import User
from realestate.apps.house.models import House


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
    # Set the template names
    homebuyer_template_name = "core/homebuyer_home.html"
    realtor_template_name = "core/realtor_home.html"

    # Method to handle the homebuyer get request
    def _homebuyer_get(self, request, homebuyer, *args, **kwargs):
        # Get the couple of the homebuyer
        couple = homebuyer.couple

        # Get the houses of the couple
        house = House.objects.filter(couple=couple)

        # Prepare the context
        context = {"couple": couple, "house": house}

        # Render the template
        return render(request, self.homebuyer_template_name, context)

    # Method to handle the realtor get request
    def _realtor_get(self, request, realtor, *args, **kwargs):
        # Render the template
        return render(request, self.realtor_template_name, {})

    # Method to handle the get request
    def get(self, request, *args, **kwargs):
        # Get the role of the user
        role = request.user.role_object

        # If the user is a homebuyer
        if role.role_type in User._HOMEBUYER_ONLY:
            # Return the homebuyer get method
            return self._homebuyer_get(request, role, *args, **kwargs)

        # If the user is a realtor
        elif role.role_type in User._REALTOR_ONLY:
            # Return the realtor get method
            return self._realtor_get(request, role, *args, **kwargs)


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
