# Django imports
from django.contrib import admin


# App imports
from realestate.apps.categories.models import Category
from realestate.apps.categories.models import CategoryWeight
from realestate.apps.categories.models import Grade


# Category inlines
class CategoryInline(admin.TabularInline):
    model = Category
    extra = 0


# Category weight inlines
class CategoryWeightInline(admin.TabularInline):
    model = CategoryWeight
    extra = 0


# Grade inlines
class GradeInline(admin.TabularInline):
    model = Grade
    extra = 0
    fields = ("homebuyer", "category", "score")
    radio_fields = {"score": admin.HORIZONTAL}
