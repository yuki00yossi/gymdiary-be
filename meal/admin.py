from django.contrib import admin

from .models import *

# Register your models here.
admin.site.register(MealItem)
admin.site.register(MealRecord)
admin.site.register(MealRecordItem)
