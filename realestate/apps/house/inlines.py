from django.contrib import admin
from .models import House


class HouseInline(admin.TabularInline):
    model = House
    extra = 0
