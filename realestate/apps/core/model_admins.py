# Imports
from django.contrib import admin
from realestate.apps.core.inlines import (
    CategoryInline,
    HomebuyerInline,
    HouseInline,
)


# Custom ModelAdmins
class CategoryAdmin(admin.ModelAdmin):
    fields = ("couple", "summary", "description")
    list_display = ("summary", "couple")


class CoupleAdmin(admin.ModelAdmin):
    inlines = [HomebuyerInline, HouseInline, CategoryInline]
    list_display = ("__str__", "realtor")
