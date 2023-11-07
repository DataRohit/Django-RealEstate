# Django imports
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin


# App imports
from realestate.apps.appauth.forms import HomebuyerSignupForm
from realestate.apps.appauth.models import User
from realestate.apps.core.admin import BaseAdmin


# Register the user model
@admin.register(User)
class UserAdmin(BaseUserAdmin, BaseAdmin):
    # Fields to be displayed in the admin panel
    fieldsets = (
        (None, {"fields": ("id", "username", "email", "password")}),
        ("Personal info", {"fields": ("first_name", "last_name", "phone")}),
        (
            "Permissions",
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                )
            },
        ),
        ("Important dates", {"fields": ("last_login",)}),
    )

    # Fields required to create a new user
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "username",
                    "first_name",
                    "last_name",
                    "password1",
                    "password2",
                ),
            },
        ),
    )

    # Read only fields
    readonly_fields = (
        "id",
        "last_login",
    )

    # Save on top
    save_on_top = True

    # Custom form for signing up a user as Homebuyer
    add_form = HomebuyerSignupForm

    # Fields to be displayed in the models admin list view
    list_display = (
        "email",
        "homebuyer_realtor_link",
        "first_name",
        "last_name",
        "phone",
        "is_staff",
        "last_login",
    )

    # Fields for filtering the data in admin list view
    list_filter = ("is_staff", "is_superuser", "is_active", "groups", "last_login")

    # Fields for searching/filtering records in the admin list view
    search_fields = ("first_name", "last_name", "phone", "email")

    # Set field for ordering the data
    ordering = ("email",)

    # Horizontal filters
    filter_horizontal = (
        "groups",
        "user_permissions",
    )

    # Method to return the link to the assigned realtor
    def homebuyer_realtor_link(self, obj):
        # Get the role object for the user
        role = obj.role_object

        # If the user is registered and role object exist
        if role:
            # Return the link
            return self._change_link(role, display_text=role.role_type)

        # Else return a question mark
        return "?"

    # Set short description for the realtor link
    homebuyer_realtor_link.short_description = "Homebuyer/Realtor"
