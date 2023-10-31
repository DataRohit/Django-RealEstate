from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from realestate.apps.core.admin import BaseAdmin
from realestate.apps.appauth.models import User
from realestate.apps.appauth.forms import RegisterForm


# Register your models here.
admin.site.site_header = "Real Estate Admin"


@admin.register(User)
class UserAdmin(BaseUserAdmin, BaseAdmin):
    fieldsets = (
        (None, {"fields": ("email", "password")}),
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
                    "phone",
                    "password1",
                    "password2",
                ),
            },
        ),
    )
    readonly_fields = ("last_login",)

    save_on_top = True

    add_form = RegisterForm

    list_display = (
        "email",
        "homebuyer_realtor_link",
        "first_name",
        "last_name",
        "phone",
        "is_staff",
        "phone",
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
