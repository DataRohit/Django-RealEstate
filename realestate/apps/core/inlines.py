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


# Inlines
class CategoryInline(admin.TabularInline):
    model = Category
    extra = 1


class CategoryWeightInline(admin.TabularInline):
    model = CategoryWeight
    extra = 1


class GradeInline(admin.TabularInline):
    model = Grade
    extra = 1


class HomebuyerInline(admin.StackedInline):
    model = Homebuyer
    extra = 1
    max_num = 2


class HouseInline(admin.TabularInline):
    model = House
    extra = 1
