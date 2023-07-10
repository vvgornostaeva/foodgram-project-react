from django.contrib.auth.models import AbstractUser
from django.db import models

from users.constants import (FIRST_NAME_MAX_LENGTH, LAST_NAME_MAX_LENGTH,
                             USERNAME_MAX_LENGTH)


class User(AbstractUser):
    """Кастомная модель пользователя."""
    email = models.EmailField(
        'Адрес электронной почты',
        unique=True
    )
    username = models.CharField(
        'Уникальный юзернейм',
        max_length=USERNAME_MAX_LENGTH,
        unique=True,
    )
    first_name = models.CharField(
        'Имя',
        max_length=FIRST_NAME_MAX_LENGTH
    )
    last_name = models.CharField(
        'Фамилия',
        max_length=LAST_NAME_MAX_LENGTH
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name', 'username']

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ('id',)

    def __str__(self):
        return self.username
