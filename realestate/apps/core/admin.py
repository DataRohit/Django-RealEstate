# Django imports
from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html


# App imports
from .inlines import HomebuyerInline
from .models import Couple
from .models import Homebuyer
from .models import Realtor
from realestate.apps.categories.inlines import CategoryInline
from realestate.apps.categories.inlines import CategoryWeightInline
from realestate.apps.house.inlines import HouseInline


# Base admin class for all models
class BaseAdmin(admin.ModelAdmin):
    # Set the fields to be readonly after creation
    _READONLY_FIELDS_AFTER_CREATION = ("couple", "user")

    # Save on top
    save_on_top = True

    # Method to create a link to the change page for an object
    def _change_link(self, obj, display_text=None):
        # If the object is None, return a question mark
        if not obj:
            return "?"

        # Get the parts for the URL
        fragments = [obj._meta.app_label, obj._meta.model_name, "change"]

        # Put the URL together
        change_url = reverse("admin:" + "_".join(fragments), args=(obj.id,))

        # Set the display the text
        display_text = display_text or str(obj)

        # Return the link
        return format_html(f"<a href={change_url}>{display_text}</a>")

    # Method to get the readonly fields
    def get_readonly_fields(self, request, obj=None):
        # Call the super method to get the readonly fields
        readonly_fields = super(BaseAdmin, self).get_readonly_fields(request, obj=obj)

        # If the object exists
        if obj:
            # Get the readonly fields
            readonly_fields = list(readonly_fields)

            # Get the fieldnames for the object
            fieldnames_for_object = map(lambda f: f.name, obj._meta.fields)

            # If the fieldname is in the readonly fields after creation, add it to the readonly fields
            for fieldname in self._READONLY_FIELDS_AFTER_CREATION:
                if fieldname in fieldnames_for_object:
                    readonly_fields.append(fieldname)

        # Return the readonly fields
        return readonly_fields

    # Method to get the inline instances
    def get_inline_instances(self, request, obj=None):
        # If the object is None, return an empty list
        if not obj:
            return []

        # Else call the super method
        return super(BaseAdmin, self).get_inline_instances(request, obj=obj)


# Register the Homebuyer model
@admin.register(Homebuyer)
class HomebuyerAdmin(BaseAdmin):
    # Set the readonly fields
    readonly_fields = ("id",)

    # Set the fields to be displayed in the admin panel
    fields = ("id", "user", "couple")

    # Set the inlines
    inlines = [CategoryWeightInline]

    # Se the list display
    list_display = ("__str__", "user_link", "partner_link", "couple_link")

    # Method to get the couple link
    def couple_link(self, obj):
        return self._change_link(obj.couple)

    # Set the couple link description
    couple_link.short_description = "Couple"

    # Method to get the partner link
    def partner_link(self, obj):
        return self._change_link(obj.partner)

    # Set the partner link description
    partner_link.short_description = "Partner"

    # Method to get the user link
    def user_link(self, obj):
        return self._change_link(obj.user)

    # Set the user link description
    user_link.short_description = "User"


# Register the Realtor model
@admin.register(Realtor)
class RealtorAdmin(BaseAdmin):
    # Set the readonly fields
    readonly_fields = ("id",)

    # Set the fields to be displayed in the admin panel
    fields = ("id", "user")

    # Set the admin list display
    list_display = ("__str__", "user_link", "phone")

    # Method to get the phone number
    def phone(self, obj):
        return obj.user.phone

    # Set the phone number description
    phone.short_description = "Phone Number"

    # Method to get the user link
    def user_link(self, obj):
        return self._change_link(obj.user)

    # Set the user link description
    user_link.short_description = "User"


# Register the Couple model
@admin.register(Couple)
class CoupleAdmin(BaseAdmin):
    # Set the readonly fields
    readonly_fields = ("id",)

    # Set the fields to be displayed in the admin panel
    fields = ("id", "realtor")

    # Set the inlines
    inlines = [HomebuyerInline, HouseInline, CategoryInline]

    # Set the fields to be displayed in the admin panel
    list_display = ("__str__", "realtor_link", "homebuyer_one", "homebuyer_two")

    # Method to get the homebuyer link
    def _homebuyer_link(self, obj, first=True):
        # Try to get both homebuyers
        try:
            homebuyer_one, homebuyer_two = obj._homebuyers()

        # If there are too many homebuyers, return an error
        except ValueError:
            return "Too many Homebuyers for Couple."

        # Get the homebuyer
        hb = homebuyer_one if first else homebuyer_two

        # Return the link
        return self._change_link(hb)

    # Method to get the first homebuyer link
    def homebuyer_one(self, obj):
        return self._homebuyer_link(obj)

    # Set the first homebuyer description
    homebuyer_one.short_description = "First Homebuyer"

    # Method to get the second homebuyer link
    def homebuyer_two(self, obj):
        return self._homebuyer_link(obj, first=False)

    # Set the second homebuyer description
    homebuyer_two.short_description = "Second Homebuyer"

    # Method to get the assigned realtor link
    def realtor_link(self, obj):
        return self._change_link(obj.realtor)

    # Set the assigned realtor description
    realtor_link.short_description = "Realtor"
