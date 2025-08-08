# health_hub/models.py
from django import forms
from wagtail.models import Page
from wagtail.admin.panels import FieldPanel  # ここでFieldPanelを使う
from wagtail.images.models import AbstractImage, AbstractRendition  # 画像を管理するためのモデル
from wagtail.fields import RichTextField
from django.db import models
from modelcluster.fields import ParentalManyToManyField
from modelcluster.contrib.taggit import ClusterTaggableManager
from taggit.models import TaggedItemBase, Tag as TaggitTag
from django.db.models import Count
from wagtail.snippets.models import register_snippet
from django.utils.text import slugify

from recipe.models import Recipe, RecipeTag
from wagtailmarkdown.fields import MarkdownField


class CustomImage(AbstractImage):
    """カスタム画像モデル"""
    admin_form_fields = (
        'file',
        'title',
        'description',
    )

    def get_upload_to(self, filename):
        return 'public/images/%s' % filename

    @property
    def url(self):
        return self.file.url if self.file else None


class CustomRendition(AbstractRendition):
    image = models.ForeignKey(
        CustomImage, related_name='renditions', on_delete=models.CASCADE, editable=False
    )

    class Meta:
        unique_together = (('image', 'filter_spec', 'focal_point_key'),)


class HomePage(Page):
    """トップページ"""
    body = RichTextField(blank=True)

    content_panels = Page.content_panels + [
        FieldPanel('body'),
    ]

    def get_context(self, request):
        context = super().get_context(request)
        context['new_articles'] = ArticlePage.objects.live().order_by('-published_at')[:3]
        context['new_recipes'] = Recipe.objects.all().order_by('-id')[:3]

        return context


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
    body = MarkdownField()
    published_at = models.DateTimeField(auto_now_add=True)

    template = "health_hub/article_page.html"

    categories = ParentalManyToManyField('health_hub.ArticleCategory', blank=True, related_name='articles')

    thumbnail = models.ForeignKey(
        'health_hub.CustomImage', null=True, blank=True, on_delete=models.SET_NULL, related_name='+'
    )

    content_panels = Page.content_panels + [
        FieldPanel('intro'),
        FieldPanel('body'),
        FieldPanel('thumbnail'),
        FieldPanel('categories', widget=forms.CheckboxSelectMultiple),
    ]

    def get_context(self, request):
        context = super().get_context(request)
        # 記事カテゴリごとの記事数を取得して渡す
        context['categories'] = ArticleCategory.objects.annotate(
            article_count=Count('articles', filter=models.Q(articles__live=True))
        ).order_by('-article_count')

        return context


@register_snippet
class ArticleCategory(models.Model):
    """記事カテゴリ"""
    name = models.CharField(max_length=255, unique=True)
    slug = models.SlugField(max_length=255, unique=True)

    panels = [
        FieldPanel('name'),
        FieldPanel('slug'),
    ]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return str(self.name)

    class Meta:
        verbose_name = "記事カテゴリ"
        verbose_name_plural = "記事カテゴリ"


class BlogIndexPage(Page):
    """記事一覧ページ"""
    intro = models.TextField(blank=True)

    content_panels = Page.content_panels + [
        FieldPanel('intro'),
    ]

    def get_context(self, request):
        context = super().get_context(request)
        # 記事カテゴリごとの記事数を取得して渡す
        context['categories'] = ArticleCategory.objects.annotate(
            article_count=Count('articles', filter=models.Q(articles__live=True))
        ).order_by('-article_count')

        # カテゴリ検索のためのクエリパラメータを取得
        selected_category = request.GET.get('category')
        if selected_category:
            context['articles'] = ArticlePage.objects.live().filter(categories__slug=selected_category).order_by('-published_at')
            selected_category = ArticleCategory.objects.filter(slug=selected_category).first()
        else:
            context['articles'] = ArticlePage.objects.live().order_by('-published_at')
        context['selected_category'] = selected_category or None

        return context
