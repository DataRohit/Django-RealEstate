from django.contrib import admin
from .models import Homebuyer


class HomebuyerInline(admin.StackedInline):
    model = Homebuyer
    extra = 0
    max_num = 2
