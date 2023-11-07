from django.contrib import admin
from .models import Category
from realestate.apps.core.admin import BaseAdmin


@admin.register(Category)
class CategoryAdmin(BaseAdmin):
    readonly_fields = ("id",)
    fields = ("id", "couple", "summary", "description")
    list_display = ("summary", "couple")
