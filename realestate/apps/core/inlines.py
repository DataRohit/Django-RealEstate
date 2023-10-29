# Imports
from django.contrib import admin
from realestate.apps.core.models import (
    Category,
    Homebuyer,
    House,
)


# Inlines
class CategoryInline(admin.TabularInline):
    model = Category
    extra = 1


class HomebuyerInline(admin.StackedInline):
    model = Homebuyer
    extra = 1
    max_num = 2


class HouseInline(admin.TabularInline):
    model = House
    extra = 1
