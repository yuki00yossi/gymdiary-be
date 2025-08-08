from django.contrib import admin
from .models import WorkoutSession, WorkoutExercise, WorkoutExerciseSet


class WorkoutExerciseSetInline(admin.TabularInline):
    """セット情報をインライン表示"""
    model = WorkoutExerciseSet
    extra = 1
    ordering = ['order']


class WorkoutExerciseInline(admin.TabularInline):
    """種目をインライン表示"""
    model = WorkoutExercise
    extra = 1
    ordering = ['order']


@admin.register(WorkoutSession)
class WorkoutSessionAdmin(admin.ModelAdmin):
    """トレーニングセッション管理"""
    list_display = ['name', 'user_id', 'date', 'created_at', 'updated_at']
    list_filter = ['date', 'created_at', 'updated_at']
    search_fields = ['name', 'user_id__username']
    readonly_fields = ['created_at', 'updated_at']
    inlines = [WorkoutExerciseInline]
    date_hierarchy = 'date'

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.select_related('user_id')


@admin.register(WorkoutExercise)
class WorkoutExerciseAdmin(admin.ModelAdmin):
    """トレーニング種目管理"""
    list_display = ['exercise_name', 'workout_session_id', 'order', 'created_at']
    list_filter = ['created_at', 'workout_session_id__date', 'exercise__category']
    search_fields = ['exercise__name', 'workout_session_id__name']
    ordering = ['workout_session_id', 'order']
    inlines = [WorkoutExerciseSetInline]

    def exercise_name(self, obj):
        """エクササイズ名を表示"""
        return obj.exercise.name
    exercise_name.short_description = 'エクササイズ名'

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.select_related('exercise', 'workout_session_id')


@admin.register(WorkoutExerciseSet)
class WorkoutExerciseSetAdmin(admin.ModelAdmin):
    """トレーニング種目セット管理"""
    list_display = ['workout_exercise_id', 'order', 'weight', 'reps', 'distance', 'duration', 'fat_burn']
    list_filter = ['workout_exercise_id__workout_session_id__date', 'workout_exercise_id__workout_session_id']
    ordering = ['workout_exercise_id', 'order']
