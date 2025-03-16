from django.contrib import admin
from .models import TrainerProfile, TrainingPlan, TrainingApplication

@admin.register(TrainerProfile)
class TrainerProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "experience", "rating", "created_at")
    search_fields = ("user__username", "certifications")
    ordering = ("created_at",)

@admin.register(TrainingPlan)
class TrainingPlanAdmin(admin.ModelAdmin):
    list_display = ("trainer", "title", "price", "plan_type", "is_available", "created_at")
    list_filter = ("plan_type", "is_available")
    search_fields = ("trainer__user__username", "title")
    ordering = ("created_at",)

@admin.register(TrainingApplication)
class TrainingApplicationAdmin(admin.ModelAdmin):
    list_display = ("user", "trainer", "plan", "status", "created_at", "expires_at")
    list_filter = ("status",)
    search_fields = ("user__username", "trainer__user__username", "plan__title")
    ordering = ("created_at",)
