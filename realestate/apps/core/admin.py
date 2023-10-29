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
from realestate.apps.core.model_admins import (
    CategoryAdmin,
    CoupleAdmin,
)


# Set the site header.
admin.site.site_header = "Real Estate Admin"


# Register the models to the admin site.
admin.site.register(Category, CategoryAdmin)
admin.site.register(CategoryWeight)
admin.site.register(Couple, CoupleAdmin)
admin.site.register(Grade)
admin.site.register(Homebuyer)
admin.site.register(House)
admin.site.register(Realtor)
