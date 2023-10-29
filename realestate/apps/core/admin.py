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
from realestate.apps.core.inlines import (
    HomebuyerInline,
    HouseInline,
    CategoryInline,
    CategoryWeightInline,
    GradeInline,
)


# Custom ModelAdmins
class BaseAdmin(admin.ModelAdmin):
    save_on_top = True


@admin.register(Category)
class CategoryAdmin(BaseAdmin):
    fields = ("couple", "summary", "description")
    list_display = ("summary", "couple")


@admin.register(Couple)
class CoupleAdmin(BaseAdmin):
    inlines = [HomebuyerInline, HouseInline, CategoryInline]
    list_display = ("__str__", "realtor")


@admin.register(Grade)
class GradeAdmin(BaseAdmin):
    radio_fields = {"score": admin.VERTICAL}


@admin.register(Homebuyer)
class HomebuyerAdmin(BaseAdmin):
    inlines = [CategoryWeightInline]
    list_display = ("__str__", "email", "full_name")


@admin.register(House)
class HouseAdmin(BaseAdmin):
    inlines = [GradeInline]
    list_display = ("nickname", "address")


@admin.register(Realtor)
class RealtorAdmin(BaseAdmin):
    list_display = ("__str__", "email", "full_name")
