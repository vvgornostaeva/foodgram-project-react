# Generated by Django 2.2.19 on 2023-07-01 20:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0004_auto_20230701_2136'),
    ]

    operations = [
        migrations.AlterField(
            model_name='recipe',
            name='image',
            field=models.ImageField(upload_to='recipes/', verbose_name='Картинка'),
        ),
    ]
