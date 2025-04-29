from django.contrib import admin
from .models import (
    TrainingSession,
    Workout,
    WorkoutSet,
    MySet,
    MySetSession,
    MySetWorkoutRecord,
    MySetWorkoutSetRecord,
)


# Register your models here.
admin.site.register(TrainingSession)
admin.site.register(Workout)
admin.site.register(WorkoutSet)
admin.site.register(MySet)
admin.site.register(MySetSession)
admin.site.register(MySetWorkoutRecord)
admin.site.register(MySetWorkoutSetRecord)
