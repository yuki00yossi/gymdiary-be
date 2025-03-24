from django.contrib import admin
from .models import ArticlePage

class ArticlePageAdmin(admin.ModelAdmin):
    list_display = ('title', 'published_at')
    prepopulated_fields = {'slug': ('title',)}  # スラッグ自動生成


admin.site.register(ArticlePage, ArticlePageAdmin)
