from django.db import transaction
from django.shortcuts import get_object_or_404
from djoser.serializers import UserCreateSerializer, UserSerializer
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers
from rest_framework.serializers import ModelSerializer
from rest_framework.validators import UniqueTogetherValidator

from recipes.models import (Favorite, Ingredient, IngredientInRecipe, Recipe,
                            ShoppingCart, Subscription, Tag)
from users.models import User


class UserSerializer(UserSerializer):
    """Сериализатор для модели User при чтении данных."""
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email', 'id', 'username', 'first_name', 'last_name',
            'is_subscribed')

    def get_is_subscribed(self, obj):
        """Метод проверки подписан ли пользователь."""
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return Subscription.objects.filter(user=user, author__id=obj.id
                                           ).exists()


class UserCreateSerializer(UserCreateSerializer, UserSerializer):
    """Сериализатор для модели User при записи данных."""

    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name',
                  'last_name', 'is_subscribed', 'password')


class TagSerializer(ModelSerializer):
    """Сериализатор для модели Tag."""
    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')


class IngredientSerializer(ModelSerializer):
    """Сериализатор для модели Ingredient при чтении данных."""
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class IngredientinRecipeCreateSerializer(ModelSerializer):
    """Сериализатор для модели IngredientInRecipe при записи данных."""
    id = serializers.PrimaryKeyRelatedField(
        source='ingredient',
        queryset=Ingredient.objects.all()
    )
    amount = serializers.IntegerField(write_only=True, min_value=1)

    class Meta:
        model = IngredientInRecipe
        fields = ('id', 'amount')


class IngredientInRecipeSerializer(ModelSerializer):
    """Сериализатор для модели IngredientInRecipe при чтении данных."""

    id = serializers.PrimaryKeyRelatedField(source='ingredient.id',
                                            read_only=True)
    name = serializers.CharField(source='ingredient.name', read_only=True)
    measurement_unit = serializers.CharField(
        source='ingredient.measurement_unit', read_only=True
    )

    class Meta:
        model = IngredientInRecipe
        fields = ('id', 'name', 'measurement_unit', 'amount')


class RecipeSerializer(ModelSerializer):
    """Сериализатор для модели Recipe при чтении данных."""
    author = UserSerializer(read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    ingredients = IngredientInRecipeSerializer(
        source='total_ingredients', read_only=True, many=True)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'author', 'ingredients',
                  'is_favorited', 'is_in_shopping_cart', 'name',
                  'image', 'text', 'cooking_time'
                  )

    def get_is_favorited(self, obj):
        """Метод проверки добавлено ли в избранное."""
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return Favorite.objects.filter(
            user=user, recipe__id=obj.id
        ).exists()

    def get_is_in_shopping_cart(self, obj):
        """Метод проверки на присутствие в листе покупок."""
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return ShoppingCart.objects.filter(
            user=user, recipe__id=obj.id
        ).exists()


class ShortRecipeSerializer(ModelSerializer):
    """"Сериализатор для короткой версии рецептов модели Recipe."""
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'cooking_time', 'image')


class RecipeCreateSerializer(ModelSerializer):
    """Сериализатор модели Recipe при записи данных."""
    ingredients = IngredientinRecipeCreateSerializer(many=True)
    author = UserSerializer(read_only=True)
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True
    )
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = ('id', 'author', 'name', 'image', 'text',
                  'ingredients', 'tags', 'cooking_time')

    def validate_ingredients(self, value):
        """Метод валидации ингредиентов в рецепте."""
        ingredients = self.initial_data.get('ingredients')
        if len(ingredients) < 1:
            raise serializers.ValidationError(
                'В рецепте должен быть хотя бы один ингредиент'
            )
        ingredients_list = []
        for ingredient in ingredients:
            ingredient_check = get_object_or_404(Ingredient,
                                                 id=ingredient['id'])
            if ingredient_check in ingredients_list:
                raise serializers.ValidationError(
                    'Ингредиенты в рецепте не должны повторяться'
                )
            ingredients_list.append(ingredient_check)
        return value

    @transaction.atomic
    def create_ingredients(self, ingredients, recipe):
        """Метод создания ингредиента."""
        create_ingredients = [
            IngredientInRecipe(
                recipe=recipe,
                ingredient=ingredient['ingredient'],
                amount=ingredient['amount']
            )
            for ingredient in ingredients
        ]
        IngredientInRecipe.objects.bulk_create(
            create_ingredients
        )

    def create(self, validated_data):
        """Метод создания рецепта."""
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags)
        self.create_ingredients(ingredients, recipe)
        return recipe

    def update(self, instance, validated_data):
        """Изменение рецепта."""
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        IngredientInRecipe.objects.filter(recipe=instance).delete()
        instance.tags.clear()
        instance.tags.set(tags)
        self.create_ingredients(ingredients, instance)
        return super().update(instance, validated_data)

    def to_representation(self, instance):
        """Метод представления модели"""
        return RecipeSerializer(
            instance,
            context={
                'request': self.context.get('request')
            }
        ).data


class SubscriptionSerializer(UserSerializer):
    """Сериализатор для модели Subscription при чтении данных."""

    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name', 'last_name',
                  'is_subscribed', 'recipes', 'recipes_count',)
        read_only_fields = ('email', 'id', 'username', 'first_name',
                            'last_name', 'is_subscribed', 'recipes',
                            'recipes_count')

    def get_recipes(self, obj):
        """Метод для получения рецептов"""
        request = self.context.get('request')
        recipes_limit = request.GET.get('recipes_limit')
        recipes = Recipe.objects.filter(author__id=obj.id)
        if recipes_limit:
            recipes = recipes[:int(recipes_limit)]
        context = {'request': request}
        return ShortRecipeSerializer(recipes, many=True,
                                     context=context).data

    def get_recipes_count(self, obj):
        """Метод для получения количества рецептов."""
        return obj.recipes.count()

    def get_is_subscribed(self, obj):
        """Метод проверки подписан ли пользователь."""
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return Subscription.objects.filter(user=user, author__id=obj.id
                                           ).exists()


class SubscriptionCreateSerializer(ModelSerializer):
    """Сериализатор для модели Subscription при записи данных."""
    class Meta:
        model = Subscription
        fields = ('user', 'author')
        validators = [
            UniqueTogetherValidator(
                queryset=Subscription.objects.all(),
                fields=('user', 'author'),
                message='Вы уже подписаны на этого пользователя'
            )
        ]

    def validate(self, data):
        """Метод проверки подписки на самого себя."""
        user = self.context.get('request').user
        author = data['author']
        if user == author:
            raise serializers.ValidationError(
                'Вы не можете подписаться на самого себя'
            )
        return data

    def to_representation(self, instance):
        return SubscriptionSerializer(
            instance.author,
            context={'request': self.context.get('request')}
        ).data


class FavoriteSerializer(ModelSerializer):
    """Сериализатор модели Favorite."""
    class Meta:
        model = Favorite
        fields = ('user', 'recipe')
        validators = [
            UniqueTogetherValidator(
                queryset=Favorite.objects.all(),
                fields=('user', 'recipe'),
                message='Вы уже добавили этот рецепт в избранное'
            )
        ]

    def to_representation(self, instance):
        return ShortRecipeSerializer(
            instance.recipe,
            context={'request': self.context.get('request')}
        ).data


class ShoppingCartSerialiser(ModelSerializer):
    """Сериализатор модели ShoppingCart."""
    class Meta:
        model = ShoppingCart
        fields = ('user', 'recipe')
        validators = [
            UniqueTogetherValidator(
                queryset=ShoppingCart.objects.all(),
                fields=('user', 'recipe'),
                message='Вы уже добавили этот рецепт в список покупок.'
            )
        ]

    def to_representation(self, instance):
        return ShortRecipeSerializer(
            instance.recipe,
            context={'request': self.context.get('request')}
        ).data
