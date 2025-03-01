from django.contrib import admin
from .models import (
    TrainingSession,
    Workout,
    WorkoutSet,
)


# Register your models here.
admin.site.register(TrainingSession)
admin.site.register(Workout)
admin.site.register(WorkoutSet)
