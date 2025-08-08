from django.contrib import admin
from .models import ExerciseCategory, Exercise


@admin.register(ExerciseCategory)
class ExerciseCategoryAdmin(admin.ModelAdmin):
    """エクササイズカテゴリ管理"""
    list_display = ['name', 'created_at', 'updated_at']
    search_fields = ['name']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Exercise)
class ExerciseAdmin(admin.ModelAdmin):
    """エクササイズ管理（統合版）"""
    list_display = ['name', 'category', 'is_official', 'created_by', 'created_at']
    list_filter = ['is_official', 'category', 'created_at']
    search_fields = ['name', 'description']
    readonly_fields = ['created_at', 'updated_at']
    list_select_related = ['category', 'created_by']

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.select_related('category', 'created_by')

    def save_model(self, request, obj, form, change):
        """エクササイズ保存時のバリデーション"""
        # 公式エクササイズの場合、created_byをNullに設定
        if obj.is_official:
            obj.created_by = None
        # ユーザーエクササイズで作成者が指定されていない場合、現在のユーザーを設定
        elif not obj.created_by:
            obj.created_by = request.user

        super().save_model(request, obj, form, change)
