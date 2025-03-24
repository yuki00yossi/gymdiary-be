# health_hub/models.py
from wagtail.models import Page
from wagtail.admin.panels import FieldPanel  # ここでFieldPanelを使う
from wagtail.images.models import Image  # 画像を管理するためのモデル
from wagtail.fields import RichTextField
from django.db import models

from recipe.models import Recipe, RecipeTag


class HomePage(Page):
    """トップページ"""
    body = RichTextField(blank=True)

    content_panels = Page.content_panels + [
        FieldPanel('body'),
    ]


class RecipeIndexPage(Page):
    """レシピ一覧ページモデル"""
    intro = models.TextField(blank=True, help_text="記事のイントロを入力してください")

    content_panels = Page.content_panels + [
        FieldPanel('intro'),
    ]

    def get_context(self, request):
        context = super().get_context(request)
        # context['articles'] = ArticlePage.objects.live().order_by('-published_at')
        context['tags'] = RecipeTag.objects.all()
        context['recipes'] = Recipe.objects.all()
        return context


class ArticlePage(Page):
    """記事ページモデル"""
    intro = models.TextField(blank=True, help_text="記事のイントロを入力してください")
    body = models.TextField(help_text="記事の本文を入力してください")
    published_at = models.DateTimeField(auto_now_add=True)

    thumbnail = models.ForeignKey(
        'wagtailimages.Image', null=True, blank=True, on_delete=models.SET_NULL, related_name='+'
    )

    content_panels = Page.content_panels + [
        FieldPanel('intro'),
        FieldPanel('body'),
        FieldPanel('thumbnail'),
    ]


class BlogIndexPage(Page):
    """記事一覧ページ"""
    intro = models.TextField(blank=True)

    content_panels = Page.content_panels + [
        FieldPanel('intro'),
    ]

    def get_context(self, request):
        context = super().get_context(request)
        context['articles'] = ArticlePage.objects.live().order_by('-published_at')
        return context
