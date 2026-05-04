# -*- coding: utf-8 -*-
"""
Призначає ціни всім майстрам, у яких немає ціни.

Логіка:
  - Рейтинг >= 4.9 і досвід >= 7 років  → Топ-майстер  (350–500 грн)
  - Рейтинг >= 4.7 і досвід >= 5 років  → Хороший майстер (280–360 грн)
  - Інші                                → Середній майстер (200–280 грн)

  Тип послуги (profession) також враховується:
    colorist +50 грн, stylist +30 грн, barber базова ціна.

Запуск: python manage.py assign_prices
        python manage.py assign_prices --force   (перезаписати ціни у ВСІХ майстрів)
"""
from decimal import Decimal
from django.core.management.base import BaseCommand
from masters.models import Master


# ──── Таблиця цін за рівнем ────────────────────────────────────────────────

PRICE_TABLE = {
    'top': {
        'barber':   Decimal('450'),
        'stylist':  Decimal('500'),
        'colorist': Decimal('600'),
    },
    'average': {
        'barber':   Decimal('300'),
        'stylist':  Decimal('350'),
        'colorist': Decimal('400'),
    },
}

# Бонус за досвід: +15 грн за кожен рік понад 5 (але не більше +150)
EXPERIENCE_BONUS_PER_YEAR = Decimal('15')
EXPERIENCE_BONUS_MIN_YEARS = 5
EXPERIENCE_BONUS_MAX = Decimal('150')


def calculate_price_and_level(master: Master):
    rating = float(master.rating)
    experience = master.experience_years
    profession = master.profession

    # 1. Визначити рівень: Топ (rating >= 4.8 AND exp >= 8)
    if rating >= 4.8 and experience >= 8:
        level = 'top'
    else:
        level = 'average'

    base = PRICE_TABLE[level].get(profession, PRICE_TABLE[level]['barber'])

    # 2. Бонус за досвід
    if experience > EXPERIENCE_BONUS_MIN_YEARS:
        bonus = min(
            EXPERIENCE_BONUS_PER_YEAR * (experience - EXPERIENCE_BONUS_MIN_YEARS),
            EXPERIENCE_BONUS_MAX,
        )
        base += bonus

    # 3. Округлити до 10 грн
    base = (base // 10) * 10

    return base, level


LEVEL_LABEL = {
    'top':    '[ТОП]      Топ-майстер',
    'average': '[СЕРЕДНІЙ] Середній майстер',
}


class Command(BaseCommand):
    help = 'Призначає ціни та рівні майстрам на основі рейтингу та досвіду'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Перезаписати ціни навіть якщо вони вже є',
        )

    def handle(self, *args, **options):
        force = options['force']

        if force:
            qs = Master.objects.all()
        else:
            qs = Master.objects.filter(default_price__isnull=True) | Master.objects.filter(level='average')

        updated = 0
        for master in qs:
            new_price, level = calculate_price_and_level(master)
            master.default_price = new_price
            master.level = level
            master.save(update_fields=['default_price', 'level'])
            updated += 1

            label = LEVEL_LABEL[level]
            self.stdout.write(
                f'  {label}  {master.full_name:25s} | '
                f'rating={master.rating} exp={master.experience_years} | '
                f'{new_price} грн'
            )

        self.stdout.write(self.style.SUCCESS(
            f'\nГотово! Оновлено ціни та рівні для {updated} майстрів.'
        ))
