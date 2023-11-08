# Django imports
from django.contrib import admin


# App imports
from .models import House
from realestate.apps.categories.inlines import GradeInline
from realestate.apps.core.admin import BaseAdmin


# Register the house model
@admin.register(House)
class HouseAdmin(BaseAdmin):
    # Set the readonly fields
    readonly_fields = ("id",)

    # Set the fields to be displayed in the admin
    fields = ("id", "nickname", "address", "couple")

    # Set the inlines
    inlines = [GradeInline]

    # Set the fields to be displayed in the admin list view
    list_display = ("nickname", "address")
