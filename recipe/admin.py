from django.contrib import admin

from .models import Recipe, RecipeIngredient, RecipeStep, RecipeTip, RecipeTag


# Register your models here.
class RecipeIngredientInline(admin.TabularInline):
    model = RecipeIngredient
    extra = 1


class RecipeStepInline(admin.TabularInline):
    model = RecipeStep
    extra = 1


class RecipeTipInline(admin.TabularInline):
    model = RecipeTip
    extra = 1


class RecipeAdmin(admin.ModelAdmin):
    inlines = [
        RecipeIngredientInline, RecipeStepInline,
        RecipeTipInline, ]
    search_fields = ('title',)
    filter_horizontal = ('tags',)


admin.site.register(Recipe, RecipeAdmin)
admin.site.register(RecipeTag)
admin.site.register(RecipeIngredient)
admin.site.register(RecipeStep)
admin.site.register(RecipeTip)
