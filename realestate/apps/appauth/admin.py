from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from realestate.apps.appauth.models import User
from realestate.apps.appauth.forms import RegisterForm


# Register your models here.
admin.site.site_header = "Real Estate Admin"


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Personal info", {"fields": ("username", "first_name", "last_name", "phone")}),
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
                    "email",
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
        "first_name",
        "last_name",
        "is_staff",
        "is_superuser",
        "phone",
    )
    list_filter = ("is_staff", "is_superuser", "is_active", "groups", "last_login")
    search_fields = ("username", "first_name", "last_name", "phone", "email")
    ordering = ("email",)
    filter_horizontal = (
        "groups",
        "user_permissions",
    )
