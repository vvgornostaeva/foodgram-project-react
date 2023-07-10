from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django_admin_display import admin_display

from .models import User


@admin.register(User)
class MyUserAdmin(UserAdmin):
    """"Модель для отображения aдмин-зоны пользователей."""
    list_display = ('username', 'email', 'first_name', 'last_name',
                    'count_subscriptions', 'count_recipes')
    list_filter = ('username', 'email')

    @admin_display(short_description='Количество подписок',)
    def count_subscriptions(self, obj):
        """"Метод подсчета количества подписок."""
        user = User.objects.filter(id=obj.id)
        return user.follower.count()
#    count_subscriptions.short_description = 'Количество подписок'

    @admin_display(short_description='Количество рецептов',)
    def count_recipes(self, obj):
        """"Метод подсчета количества рецептов."""
        user = User.objects.filter(id=obj.id)
        return user.recipes.count()
#    count_recipes.short_description = 'Количество рецептов'
