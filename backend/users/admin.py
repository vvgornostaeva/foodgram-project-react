from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User


class MyUserAdmin(UserAdmin):
    """"Модель для отображения aдмин-зоны пользователей."""
    list_display = ('username', 'email', 'first_name', 'last_name')
    list_filter = ('username', 'email')


admin.site.register(User, MyUserAdmin)
