# Django imports
from django.contrib import admin


# App imports
from realestate.apps.core.admin import BaseAdmin
from realestate.apps.pending.models import PendingCouple
from realestate.apps.pending.models import PendingHomebuyer


# PendingHomebuyer inline
class PendingHomebuyerInline(admin.StackedInline):
    model = PendingHomebuyer
    extra = 1
    max_num = 2
    fields = (
        "email",
        "registration_token",
        "registration_status",
    )
    readonly_fields = ("registration_status", "registration_token")


# Register the PendingCouple model
@admin.register(PendingCouple)
class PendingCoupleAdmin(BaseAdmin):
    # Set the inlines
    inlines = [PendingHomebuyerInline]

    # Set the fields to be displayed in the admin list view
    list_display = ["__str__", "couple_link", "realtor_link"]

    # Set the field to be used for ordering
    ordering = ["realtor"]

    # Method to get the couple link
    def couple_link(self, obj):
        return self._change_link(obj.couple)

    # Set short description for the couple link
    couple_link.short_description = "Couple"

    # Method to get the realtor link
    def realtor_link(self, obj):
        return self._change_link(obj.realtor)

    # Set short description for the realtor link
    realtor_link.short_description = "Realtor"
