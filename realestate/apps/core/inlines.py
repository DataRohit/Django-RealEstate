# Imports
from django.contrib import admin
from realestate.apps.core.models import (
    Category,
    CategoryWeight,
    Couple,
    Grade,
    Homebuyer,
    House,
    Realtor,
)


admin.site.site_header = "Real Estate Admin"


# Inlines
class CategoryInline(admin.TabularInline):
    model = Category
    extra = 0


class CategoryWeightInline(admin.TabularInline):
    model = CategoryWeight
    extra = 0


class GradeInline(admin.TabularInline):
    model = Grade
    extra = 0
    fields = ("homebuyer", "category", "score")
    radio_fields = {"score": admin.HORIZONTAL}


class HomebuyerInline(admin.StackedInline):
    model = Homebuyer
    extra = 0
    max_num = 2


class HouseInline(admin.TabularInline):
    model = House
    extra = 0
