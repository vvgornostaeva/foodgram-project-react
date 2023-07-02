from django.contrib import admin

from .models import (Favorite, Ingredient, IngredientInRecipe, Recipe,
                     ShoppingCart, Subscription, Tag)


class RecipeAdmin(admin.ModelAdmin):
    """"Модель для отображения aдмин-зоны рецептов."""
    list_display = (
        'author',
        'name',
        'count_favorites'
    )
    list_filter = ('author', 'name', 'tags')

    def count_favorites(self, obj):
        """"Метод подсчета количества добавлений в избранное."""
        return Favorite.objects.filter(recipe=obj).count()
    count_favorites.short_description = 'Количество добавлений в избранное'


class IngredientAdmin(admin.ModelAdmin):
    """"Модель для отображения админ-зоны ингредиентов."""
    list_display = (
        'name',
        'measurement_unit'
    )
    list_filter = ('name',)
    search_fields = ('name',)


admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Subscription)
admin.site.register(Favorite)
admin.site.register(Tag)
admin.site.register(IngredientInRecipe)
admin.site.register(ShoppingCart)
