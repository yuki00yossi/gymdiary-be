from django.contrib import admin
from .models import TrainerProfile


@admin.register(TrainerProfile)
class TrainerProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'is_public')
    search_fields = ('user__username',)
    list_filter = ('is_public',)
    # readonly_fields = ('user',)
