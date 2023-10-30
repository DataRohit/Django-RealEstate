from django.contrib import admin

from realestate.apps.core.admin import BaseAdmin
from realestate.apps.pending.models import PendingCouple, PendingHomebuyer


# Register your models here.
class PendingHomebuyerInline(admin.StackedInline):
    model = PendingHomebuyer
    extra = 1
    max_num = 2
    fields = (
        "email",
        "first_name",
        "last_name",
        "registration_token",
        "registration_status",
    )
    readonly_fields = ("registration_status", "registration_token")


@admin.register(PendingCouple)
class PendingCoupleAdmin(BaseAdmin):
    inlines = [PendingHomebuyerInline]
