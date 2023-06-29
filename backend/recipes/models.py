from colorfield.fields import ColorField
from django.contrib.auth import get_user_model
from django.core import validators
from django.db import models

User = get_user_model()


class Ingredient(models.Model):
    """"Модель ингрeдиентов."""
    name = models.CharField(
        'Название ингредиента',
        db_index=True,
        max_length=200
    )
    measurement_unit = models.CharField(
        'Единица измерения ингредиента',
        max_length=200
    )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self) -> str:
        return self.name


class Tag(models.Model):
    """Модель тэгов."""
    name = models.CharField(
        'Название',
        max_length=200,
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
        constraints = (
            models.UniqueConstraint(
                fields=('name', 'color', 'slug'),
                name='unique_tags',
            ),
        )

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
        max_length=200)
    text = models.TextField(
        'Описание рецепта'
    )
    pub_date = models.DateTimeField(
        'Дата публикации',
        auto_now_add=True
    )
    image = models.ImageField(
        'Картинка',
        upload_to='recipe/',
        
    )
    cooking_time = models.PositiveSmallIntegerField(
        'Время приготовления (в минутах)',
        validators=[validators.MinValueValidator(
            1,
            message='Время приготовления должно быть не меньше 1 минуты')
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
        related_name='recipes')

    class Meta:
        ordering = ['-pub_date']
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
                1,
                message='Количество должно быть не меньше 1'
            ),
        ]
    )

    class Meta:
        verbose_name = 'Количество ингредиента в рецепте'
        verbose_name_plural = 'Количество ингредиентов в рецепте'
        constraints = [
            models.UniqueConstraint(
                fields=['recipe', 'ingredient'],
                name='unique_ingredient_for_recipe')]

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
        auto_now_add=True)

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        ordering = ['-created_at']
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'author'],
                name='unique_subscription'
            )
        ]

    def __str__(self):
        return f'{self.user} подписан(а) на {self.author}'


class Favorite(models.Model):
    """Модель для избранных рецептов."""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='favorites',
        verbose_name='Пользователь'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='favorites',
        verbose_name='Рецепт'
    )

    class Meta:
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранное'
        constraints = [
            models.UniqueConstraint(fields=['user', 'recipe'],
                                    name='unique_fav_connection')
        ]

    def __str__(self):
        return f'{self.user} добавил в избранное {self.recipe}'


class ShoppingCart(models.Model):
    """Модель списка покупок."""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='shopping_cart',
        verbose_name='Пользователь',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='shopping_cart',
        verbose_name='Рецепт',
    )

    class Meta:
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Списки покупок'
        constraints = [
            models.UniqueConstraint(fields=['user', 'recipe'],
                                    name='unique_shopping_cart')
        ]

    def __str__(self):
        return f'{self.user} добавил в список покупок {self.recipe}'
