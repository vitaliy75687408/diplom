# -*- coding: utf-8 -*-
"""
Прив’язує популярні зачіски (Taper Fade, Low Fade тощо) до майстрів,
щоб пошук за цими зачісками на сторінці «Знайдіть майстра» повертав результат.

Запуск: python manage.py assign_popular_hairstyles_to_masters
"""
from django.core.management.base import BaseCommand
from django.db import transaction
from hairstyles.models import Hairstyle
from masters.models import Master
from styleai.constants import POPULAR_HAIRSTYLE_NAMES


class Command(BaseCommand):
    help = 'Додає популярні зачіски до майстрів, щоб пошук за стилем працював'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Показати, що буде зроблено, без змін у БД',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        if dry_run:
            self.stdout.write(self.style.WARNING('Режим dry-run — зміни не зберігаються'))

        # Зачіски з сайту (популярні)
        styles = list(Hairstyle.objects.filter(name__in=POPULAR_HAIRSTYLE_NAMES))
        name_to_style = {s.name: s for s in styles}
        missing = [n for n in POPULAR_HAIRSTYLE_NAMES if n not in name_to_style]
        if missing:
            self.stdout.write(
                self.style.WARNING(
                    f'У БД немає зачісок: {", ".join(missing)}. '
                    'Спочатку запустіть: python manage.py set_popular_hairstyles'
                )
            )
        if not styles:
            self.stdout.write(self.style.ERROR('Немає популярних зачісок у БД. Завершено.'))
            return

        masters = list(Master.objects.all())
        if not masters:
            self.stdout.write(self.style.WARNING('Немає майстрів у БД.'))
            return

        with transaction.atomic():
            for master in masters:
                added = []
                for style in styles:
                    if master.specialties.filter(pk=style.pk).exists():
                        continue
                    if not dry_run:
                        master.specialties.add(style)
                    added.append(style.name)
                if added:
                    self.stdout.write(
                        f'  {master.full_name}: +{len(added)} зачісок'
                        + (f' ({", ".join(added[:3])}{"…" if len(added) > 3 else ""})' if added else '')
                    )

        if dry_run and (masters or styles):
            self.stdout.write(self.style.SUCCESS('Dry-run завершено. Запустіть без --dry-run, щоб зберегти.'))
        else:
            self.stdout.write(self.style.SUCCESS('Готово. Пошук за зачіскою тепер покаже майстрів.'))
