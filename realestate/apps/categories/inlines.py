from django.contrib import admin
from realestate.apps.categories.models import Category, CategoryWeight, Grade


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
