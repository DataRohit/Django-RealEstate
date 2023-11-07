from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from realestate.apps.appauth.forms import HomebuyerSignupForm
from realestate.apps.appauth.models import User
from realestate.apps.core.admin import BaseAdmin


@admin.register(User)
class UserAdmin(BaseUserAdmin, BaseAdmin):
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
    readonly_fields = (
        "id",
        "last_login",
    )

    save_on_top = True

    add_form = HomebuyerSignupForm

    list_display = (
        "email",
        "homebuyer_realtor_link",
        "first_name",
        "last_name",
        "phone",
        "is_staff",
        "last_login",
    )
    list_filter = ("is_staff", "is_superuser", "is_active", "groups", "last_login")
    search_fields = ("first_name", "last_name", "phone", "email")
    ordering = ("email",)
    filter_horizontal = (
        "groups",
        "user_permissions",
    )

    def homebuyer_realtor_link(self, obj):
        role = obj.role_object
        if role:
            return self._change_link(role, display_text=role.role_type)
        return "?"

    homebuyer_realtor_link.short_description = "Homebuyer/Realtor"
