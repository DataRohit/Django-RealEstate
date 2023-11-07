# Django imports
from django.contrib import admin


# App imports
from .models import Homebuyer


# Homebuyer inline
class HomebuyerInline(admin.StackedInline):
    model = Homebuyer
    extra = 0
    max_num = 2
