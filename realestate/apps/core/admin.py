# Imports
from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html

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

    def _change_link(self, obj, display_text=None):
        if not obj:
            return "?"

        fragments = [obj._meta.app_label, obj._meta.model_name, "change"]
        change_url = reverse("admin:" + "_".join(fragments), args=(obj.id,))
        display_text = display_text or str(obj)

        return format_html(f"<a href={change_url}>{display_text}</a>")

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
    list_display = ("__str__", "realtor_link", "homebuyer_one", "homebuyer_two")

    def _homebuyer_link(self, obj, first=True):
        try:
            homebuyer_one, homebuyer_two = obj._homebuyers()
        except ValueError:
            return "Too many Homebuyers for Couple."
        hb = homebuyer_one if first else homebuyer_two
        return self._change_link(hb)

    def homebuyer_one(self, obj):
        return self._homebuyer_link(obj)

    homebuyer_one.short_description = "First Homebuyer"

    def homebuyer_two(self, obj):
        return self._homebuyer_link(obj, first=False)

    homebuyer_two.short_description = "Second Homebuyer"

    def realtor_link(self, obj):
        return self._change_link(obj.realtor)

    realtor_link.short_description = "Realtor"


@admin.register(Homebuyer)
class HomebuyerAdmin(BaseAdmin):
    fields = ("user", "couple")
    inlines = [CategoryWeightInline]
    list_display = ("__str__", "user_link", "partner_link", "couple_link")

    def couple_link(self, obj):
        return self._change_link(obj.couple)

    couple_link.short_description = "Couple"

    def partner_link(self, obj):
        return self._change_link(obj.partner)

    partner_link.short_description = "Partner"

    def user_link(self, obj):
        return self._change_link(obj.user)

    user_link.short_description = "User"


@admin.register(House)
class HouseAdmin(BaseAdmin):
    inlines = [GradeInline]
    list_display = ("nickname", "address")


@admin.register(Realtor)
class RealtorAdmin(BaseAdmin):
    list_display = ("__str__", "user_link", "phone")

    def phone(self, obj):
        return obj.user.phone

    phone.short_description = "Phone Number"

    def user_link(self, obj):
        return self._change_link(obj.user)

    user_link.short_description = "User"
