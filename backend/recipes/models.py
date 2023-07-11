from colorfield.fields import ColorField
from django.contrib.auth import get_user_model
from django.core import validators
from django.db import models

from recipes.constants import (INGREDIENT_NAME_MAX_LENGTH,
                               INGREDIENT_UNIT_MAX_LENGTH,
                               MAX_COOKING_TIME_IN_MIN, MAX_INGREDIENT_AMOUNT,
                               MIN_COOKING_TIME_IN_MIN, MIN_INGREDIENT_AMOUNT,
                               RECIPE_NAME_MAX_LENGTH, TAG_NAME_MAX_LENGTH)

User = get_user_model()


class Ingredient(models.Model):
    """"Модель ингрeдиентов."""
    name = models.CharField(
        'Название ингредиента',
        db_index=True,
        max_length=INGREDIENT_NAME_MAX_LENGTH
    )
    measurement_unit = models.CharField(
        'Единица измерения ингредиента',
        max_length=INGREDIENT_UNIT_MAX_LENGTH
    )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        constraints = [
            models.UniqueConstraint(
                fields=['name', 'measurement_unit'],
                name='unique_ingredient_unit'
            )
        ]

    def __str__(self) -> str:
        return self.name


class Tag(models.Model):
    """Модель тэгов."""
    name = models.CharField(
        'Название',
        max_length=TAG_NAME_MAX_LENGTH,
        unique=True
    )
    slug = models.SlugField(
        'Уникальный слаг',
        unique=True
    )
    color = ColorField(
        'Цвет в HEX',
        unique=True
    )

    class Meta:
        verbose_name = 'Тэг'
        verbose_name_plural = 'Тэги'
        constraints = [
            models.UniqueConstraint(
                fields=['name', 'color', 'slug'],
                name='unique_tags'
            )
        ]

    def __str__(self) -> str:
        return self.name


class Recipe(models.Model):
    """Модель рецептов."""
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Автор рецепта'
    )
    name = models.CharField(
        'Название рецепта',
        max_length=RECIPE_NAME_MAX_LENGTH,
        validators=[
            validators.RegexValidator(
                regex=r'^[А-Яа-яЁё][а-яё\s_-]+$',
                message='Проверьте, что название начинается с буквы и '
                        'и не содержит иных символов, кроме дефиса '
                        'нижнего подчеркивания и пробела')
        ]
    )
    text = models.TextField(
        'Описание рецепта'
    )
    pub_date = models.DateTimeField(
        'Дата публикации',
        auto_now_add=True
    )
    image = models.ImageField(
        'Картинка',
        upload_to='recipes/',

    )
    cooking_time = models.PositiveSmallIntegerField(
        'Время приготовления (в минутах)',
        validators=[
            validators.MinValueValidator(
                MIN_COOKING_TIME_IN_MIN,
                message='Время приготовления должно быть не меньше '
                        '1 минуты'
            ),
            validators.MaxValueValidator(
                MAX_COOKING_TIME_IN_MIN,
                message='Время приготовления должно быть не больше '
                        '1440 минут'
            )
        ]
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        verbose_name='Ингредиенты',
        through='IngredientInRecipe',
        related_name='recipes'

    )
    tags = models.ManyToManyField(
        Tag,
        verbose_name='Тэги',
        related_name='recipes'
    )

    class Meta:
        ordering = ('-pub_date',)
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return self.name


class IngredientInRecipe(models.Model):
    """Модель для описания количества ингредиентов в отдельных рецептах"""
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт',
        related_name='total_ingredients'
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        verbose_name='Ингрeдиент',
        related_name='in_recipes'
    )
    amount = models.PositiveSmallIntegerField(
        'Количество',
        validators=[
            validators.MinValueValidator(
                MIN_INGREDIENT_AMOUNT,
                message='Количество должно быть не меньше 1'
            ),
            validators.MaxValueValidator(
                MAX_INGREDIENT_AMOUNT,
                message='Количество должно быть не больше 10000'
            )
        ]
    )

    class Meta:
        verbose_name = 'Количество ингредиента в рецепте'
        verbose_name_plural = 'Количество ингредиентов в рецепте'
        constraints = [
            models.UniqueConstraint(
                fields=['recipe', 'ingredient'],
                name='unique_ingredient_for_recipe'
            )
        ]

    def __str__(self):
        return (f'В {self.recipe} - {self.ingredient} {self.amount} '
                f'{self.ingredient.measurement_unit}')


class Subscription(models.Model):
    """"Модель подписки на авторов."""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
        verbose_name='Подписчик'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following',
        verbose_name='Автор'
    )
    created_at = models.DateTimeField(
        'Дата подписки',
        auto_now_add=True
    )

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        ordering = ('-created_at',)
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'author'],
                name='unique_subscription'
            )
        ]

    def __str__(self):
        return f'{self.user} подписан(а) на {self.author}'


class BaseFavShopCart(models.Model):
    """Абстрактный класс для моделей Favorite и ShoppingCart."""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='%(class)s_related',
        verbose_name='Пользователь',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='%(class)s_related',
        verbose_name='Рецепт',
    )

    class Meta:
        abstract = True
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_user_recipe_connection'
            )
        ]


class Favorite(BaseFavShopCart):
    """Модель для избранных рецептов."""

    class Meta:
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранное'

    def __str__(self):
        return f'{self.user} добавил в избранное {self.recipe}'


class ShoppingCart(BaseFavShopCart):
    """Модель списка покупок."""
    class Meta:
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Списки покупок'

    def __str__(self):
        return f'{self.user} добавил в список покупок {self.recipe}'
