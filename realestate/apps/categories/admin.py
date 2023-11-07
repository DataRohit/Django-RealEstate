# Django imports
from django.contrib import admin


# App imports
from .models import Category
from realestate.apps.core.admin import BaseAdmin


# Register the Category model
@admin.register(Category)
class CategoryAdmin(BaseAdmin):
    # Set the readonly fields
    readonly_fields = ("id",)

    # Fields to be displayed in the admin panel
    fields = ("id", "couple", "summary", "description")

    # Fields to be displayed in the admin list view
    list_display = ("summary", "couple")
