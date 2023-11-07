from django.contrib import admin
from .models import House
from realestate.apps.core.admin import BaseAdmin
from realestate.apps.categories.inlines import GradeInline


@admin.register(House)
class HouseAdmin(BaseAdmin):
    readonly_fields = ("id",)
    fields = ("id", "nickname", "address", "couple")
    inlines = [GradeInline]
    list_display = ("nickname", "address")
