from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, UserRole


# Register your models here.
class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = (
        'username', 'name', 'is_active',
        'is_staff', 'is_superuser', 'created_at')
    list_filter = ('is_staff', 'is_superuser', 'is_active')
    ordering = ('created_at', 'username',)
    search_fields = ('username',)
    fieldsets = (
        (None, {'fields': ('username', 'name', 'password')}),
        ("権限", {'fields': ('is_staff', 'is_superuser')}),
        ('その他', {'fields': ('is_active', 'created_at')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'username', 'name', 'password1', 'password2',
                'is_active', 'is_staff', 'is_superuser')
        })
    )


admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(UserRole)
