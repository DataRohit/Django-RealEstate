# Imports
from django.contrib import admin
from realestate.apps.core.models import *


# Register the models to the admin site.
admin.site.register(Category)
admin.site.register(CategoryWeight)
admin.site.register(Couple)
admin.site.register(Grade)
admin.site.register(Homebuyer)
admin.site.register(House)
admin.site.register(Realtor)
