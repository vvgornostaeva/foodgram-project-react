import csv
import os

from django.conf import settings
from django.core.management import BaseCommand

from recipes.models import Ingredient


class Command(BaseCommand):
    """
    Management-команда, добавляющая данные в базу данных.
    python manage.py import_csv
    """
    help = 'Импорт данных из CSV файла в модель Ingredient'

    def handle(self, *args, **options):
        with open(os.path.join(settings.BASE_DIR, 'data/ingredients.csv'),
                  'rt', encoding='utf-8') as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',')
            for row in csv_reader:
                Ingredient.objects.get_or_create(
                    name=row[0],
                    measurement_unit=row[1]
                )
