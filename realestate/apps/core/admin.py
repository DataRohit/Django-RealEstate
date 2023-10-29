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
    _READONLY_FIELDS_AFTER_CREATION = ("couple", "user")
    save_on_top = True

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = super(BaseAdmin, self).get_readonly_fields(request, obj=obj)

        if obj:
            readonly_fields = list(readonly_fields)
            fieldnames_for_object = map(lambda f: f.name, obj._meta.fields)

            for fieldname in self._READONLY_FIELDS_AFTER_CREATION:
                if fieldname in fieldnames_for_object:
                    readonly_fields.append(fieldname)

        return readonly_fields

    def get_inline_instances(self, request, obj=None):
        if not obj:
            return []

        return super(BaseAdmin, self).get_inline_instances(request, obj=obj)


@admin.register(Category)
class CategoryAdmin(BaseAdmin):
    fields = ("couple", "summary", "description")
    list_display = ("summary", "couple")


@admin.register(Couple)
class CoupleAdmin(BaseAdmin):
    inlines = [HomebuyerInline, HouseInline, CategoryInline]
    list_display = ("__str__", "realtor")


@admin.register(Homebuyer)
class HomebuyerAdmin(BaseAdmin):
    inlines = [CategoryWeightInline]
    list_display = ("__str__", "email", "full_name")


@admin.register(House)
class HouseAdmin(BaseAdmin):
    fields = ("user", "couple")
    inlines = [GradeInline]
    list_display = ("nickname", "address")


@admin.register(Realtor)
class RealtorAdmin(BaseAdmin):
    list_display = ("__str__", "email", "full_name")
