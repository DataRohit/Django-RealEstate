# Django imports
from django.contrib import admin


# App imports
from .models import House


# House Inline
class HouseInline(admin.TabularInline):
    model = House
    extra = 0
