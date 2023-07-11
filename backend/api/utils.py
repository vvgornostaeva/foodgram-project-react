from django.db.models import F, Sum
from django.shortcuts import HttpResponse
from rest_framework import status
from rest_framework.response import Response

from recipes.models import IngredientInRecipe


def post_instance(request, instance, serializer):
    """Добавление в избарнное или в список покупок."""
    serializer = serializer(
        data={'user': request.user.id, 'recipe': instance.id, },
        context={'request': request}
    )
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return Response(serializer.data, status=status.HTTP_201_CREATED)


def delete_instance(request, name_model, instance, error_message,
                    success_message):
    """Удаление из избарнного или из списка покупок."""
    if not name_model.objects.filter(user=request.user,
                                     recipe=instance).exists():
        return Response({'errors': error_message},
                        status=status.HTTP_400_BAD_REQUEST)
    name_model.objects.filter(user=request.user, recipe=instance).delete()
    return Response(success_message, status=status.HTTP_204_NO_CONTENT)


def create_shopping_cart(request):
    """Метод создания списка покупок в формате txt."""
    ingredients = IngredientInRecipe.objects.select_related(
        'recipe', 'ingredient'
    )
    ingredients = ingredients.filter(
        recipe__shoppingcart_related__user=request.user
    ).values(
        'ingredient__name',
        'ingredient__measurement_unit'
    ).annotate(
        name=F('ingredient__name'),
        unit=F('ingredient__measurement_unit'),
        ingredient_amount=Sum('amount'),)
    shopping_list = ['Список покупок:\n']
    for ingredient in ingredients:
        shopping_list.append(
            f"{ingredient['name']} - {ingredient['ingredient_amount']}"
            f"{ingredient['unit']};\n"
        )
    response = HttpResponse(shopping_list, content_type='text/plain')
    response['Content-Disposition'] = ('attachment; '
                                       'filename="shopping_cart.txt"')
    return response
