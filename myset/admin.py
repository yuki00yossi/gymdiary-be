from django.contrib import admin
from .models import MySet, MySetExercise, MySetExerciseSet


class MySetExerciseSetInline(admin.TabularInline):
    """セット情報をインライン表示"""
    model = MySetExerciseSet
    extra = 1
    ordering = ['order']


class MySetExerciseInline(admin.TabularInline):
    """種目をインライン表示"""
    model = MySetExercise
    extra = 1
    ordering = ['order']


@admin.register(MySet)
class MySetAdmin(admin.ModelAdmin):
    """マイセット管理"""
    list_display = ['name', 'user_id', 'created_at', 'updated_at']
    list_filter = ['created_at', 'updated_at']
    search_fields = ['name', 'user_id__username']
    readonly_fields = ['created_at', 'updated_at']
    inlines = [MySetExerciseInline]

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.select_related('user_id')


@admin.register(MySetExercise)
class MySetExerciseAdmin(admin.ModelAdmin):
    """マイセット種目管理"""
    list_display = ['exercise_name', 'myset_id', 'order', 'created_at']
    list_filter = ['created_at', 'exercise__category']
    search_fields = ['exercise__name', 'myset_id__name']
    ordering = ['myset_id', 'order']
    inlines = [MySetExerciseSetInline]

    def exercise_name(self, obj):
        """エクササイズ名を表示"""
        return obj.exercise.name
    exercise_name.short_description = 'エクササイズ名'

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.select_related('exercise', 'myset_id')


@admin.register(MySetExerciseSet)
class MySetExerciseSetAdmin(admin.ModelAdmin):
    """マイセット種目セット管理"""
    list_display = ['myset_exercise_id', 'order', 'weight', 'reps', 'distance', 'duration']
    list_filter = ['myset_exercise_id__myset_id']
    ordering = ['myset_exercise_id', 'order']
