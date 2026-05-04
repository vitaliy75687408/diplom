# -*- coding: utf-8 -*-
"""
Додає 3 відгуки для головної сторінки. Середній — з фото з інтернету (аватар у view).
Запуск: python manage.py add_reviews
"""
from django.core.management.base import BaseCommand
from masters.models import Master, Review


# Три відгуки для блоку на головній; посередині (Олена К.) — аватар з REVIEW_AVATAR_URLS[1]
DEFAULT_REVIEWS = [
    {'author_name': 'Андрій М.', 'rating': 5, 'text': 'АІ підбір зачіски допіг знайти ідеальний стиль! Майстер зробив все ідеально!'},
    {'author_name': 'Олена К.', 'rating': 5, 'text': 'Знайшла майстра за хвилини. Зачіска перевершила очікування. Рекомендую!'},
    {'author_name': 'Максим П.', 'rating': 5, 'text': 'AI точно визначив зачіску. Барбер — професіонал. Дуже задоволений!'},
]


class Command(BaseCommand):
    help = 'Додає 3 відгуки на головну (середній — з фото з інтернету)'

    def handle(self, *args, **options):
        master = Master.objects.first()
        if not master:
            self.stdout.write(self.style.WARNING('Немає майстрів у базі. Спочатку запустіть add_10_masters.'))
            return
        count_before = Review.objects.count()
        added = 0
        for data in DEFAULT_REVIEWS[:3]:
            if Review.objects.filter(master=master, author_name=data['author_name'], text=data['text']).exists():
                continue
            Review.objects.create(master=master, **data)
            added += 1
            self.stdout.write(self.style.SUCCESS(f'  + Відгук від {data["author_name"]}'))
        count_after = Review.objects.count()
        self.stdout.write(self.style.SUCCESS(f'Готово. Додано: {added}, всього відгуків: {count_after}.'))
