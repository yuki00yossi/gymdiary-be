from django.shortcuts import render
from django.views.generic import DetailView, ListView
from django.db.models import Q
from recipe.models import Recipe, RecipeTag


# Create your views here.
class RecipeDetailView(DetailView):
    """レシピの詳細画面"""
    model = Recipe
    template_name = "health_hub/recipe_detail.html"
    queryset = Recipe.objects.prefetch_related(
        'ingredients', 'steps', 'tips')


class RecipeSearchView(ListView):
    """レシピ検索ビュー"""
    model = Recipe
    template_name = "health_hub/recipe_search.html"
    paginate_by = 30
    context_object_name = 'recipes'

    def get_queryset(self):
        queryset = Recipe.objects.all().prefetch_related(
            'tags', 'ingredients__meal_item').distinct().order_by('-id')
        query = self.request.GET.get('q', '').strip()
        tag_slugs = self.request.GET.getlist('tags')

        if tag_slugs:
            print('tag_slugs: ', tag_slugs)
            queryset = queryset.filter(tags__slug__in=tag_slugs)

        if query:
            print('query: ', query)
            keywords = query.split()
            q_objects = Q()
            for word in keywords:
                q_objects &= (
                    Q(title__icontains=word) |
                    Q(description__icontains=word) |
                    Q(ingredients__meal_item__name__icontains=word)
                )
            queryset = queryset.filter(q_objects)
        print('queryset: ', queryset)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['query'] = self.request.GET.get('q', '').strip()
        context['tags'] = RecipeTag.objects.all()
        selected_slugs = self.request.GET.getlist('tags')

        print('query: ', context['query'])
        context['selected_tags'] = RecipeTag.objects.filter(slug__in=selected_slugs)
        return context
