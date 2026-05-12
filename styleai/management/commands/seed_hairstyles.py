
# -*- coding: utf-8 -*-
"""
Management command для заповнення бази даних зачісками.

Розташування файлу:
    hairstyles/management/commands/seed_hairstyles.py

Як запустити:
    python manage.py seed_hairstyles

Що робить:
    - Створює всі зачіски з constants.py
    - Прив'язує зображення за явною мапою (файл → назва зачіски)
    - Не дублює: якщо зачіска вже є — оновлює зображення якщо його не було
    - З --force перезаписує опис та категорію
"""

import os
from django.core.management.base import BaseCommand
from django.conf import settings
from hairstyles.models import Hairstyle
from styleai.constants import (
    POPULAR_HAIRSTYLE_NAMES,
    EXTRA_WOMEN_HAIRSTYLE_NAMES,
    EXTRA_MEN_HAIRSTYLE_NAMES,
    WOMEN_HAIRSTYLES,
    MEN_HAIRSTYLES,
    HAIRSTYLE_LENGTH,
    HAIRSTYLE_LENGTH_LABELS,
    EXTRA_WOMEN_STYLE_DESCRIPTIONS,
    EXTRA_MEN_STYLE_DESCRIPTIONS,
)

# ── Явна мапа: ім'я файлу (відносно media/hairstyles/) → назва зачіски ───────
# Якщо для однієї зачіски є кілька файлів — береться перший що існує на диску.
IMAGE_MAP = {
    # --- Чоловічі популярні ---
    'drop_fade.jpg':         'Drop Fade',
    'drop-fade.webp':        'Drop Fade',
    'taper_fade.jpg':        'Taper Fade',
    'teper-fade.jpg':        'Taper Fade',   # опечатка в назві файлу
    'low_fade.jpg':          'Low Fade',
    'low-fade.jpg':          'Low Fade',
    'mid-fade.jpg':          'Mid Fade',
    'high_fade.jpg':         'High Fade',
    'high_fade..jfif':       'High Fade',
    'skin-fade.jpg':         'Skin Fade',
    'textured_crop..jpg':    'Textured Crop',
    'burst_fade.jpg':        'Burst Fade',
    'burst-fade..jpg':       'Burst Fade',
    'edgar_cut.jfif':        'Edgar Cut',
    'slick_back.jpg':        'Slick Back',
    'slick-back.webp':       'Slick Back',
    'pompadour.jpg':         'Pompadour',
    'quiff.jpg':             'Quiff',
    'mod_cut.jpg':           'Mod Cut',
    'mod_cut.jfif':          'Mod Cut',
    'brush-up-fade.jpg':     'Brush Up Fade',
    'undercut.jpg':          'Undercut',
    'undercut.webp':         'Undercut',
    'faux-hawk.jpg':         'Faux Hawk',
    'crew_cut.jpg':          'Crew Cut',
    'buzz-cut.jpg':          'Buzz Cut',
    # --- Унісекс / жіночі популярні ---
    'long_wavy_hair..jpg':   'Long Wavy Hair',
    'long_wavy_hair.jpg':    'Long Wavy Hair',
    'bob.jpg':               'Bob',
    'pixie-cut.webp':        'Pixie Cut',
    # --- Українські назви ---
    'каре.webp':             'Каре',
    'кучерявий_боб.jpg':     'Кучерявий Боб',
    'кучерявий-боб..webp':   'Кучерявий Боб',
    'піксі.webp':            'Піксі',
    'нікcі.webp':            'Піксі',
    'гарсон.webp':           'Гарсон',
    'сесон.webp':            'Сесон',
    'їжачок.webp':           'Їжачок',
    'yizhachok.jpg':         'Їжачок',
    'шеггі.jfif':            'Шеггі',
    'шерри.jfif':            'Шеггі',
}

# ── Описи для популярних зачісок ─────────────────────────────────────────────
POPULAR_DESCRIPTIONS = {
    'Drop Fade':       'Фейд що плавно спускається вниз — сучасно та охайно.',
    'Taper Fade':      'Класичний конічний фейд по боках і потилиці.',
    'Low Fade':        'Низький фейд — мінімалістично й елегантно.',
    'Mid Fade':        'Середній фейд: баланс між класикою та сучасністю.',
    'High Fade':       'Високий фейд для максимального контрасту.',
    'Skin Fade':       'Бритий фейд до шкіри — чітко та стильно.',
    'Textured Crop':   "Коротка стрижка з текстурою та об'ємом на верхівці.",
    'Burst Fade':      'Розкритий фейд навколо вуха — динамічний образ.',
    'Edgar Cut':       'Різкий прямий чубчик із фейдом по боках.',
    'Slick Back':      'Зачесане назад волосся — класика на всі часи.',
    'Pompadour':       "Висока об'ємна зачіска з гладкими боками.",
    'Quiff':           "Піднятий чуб із об'ємом — між помпадуром та кіком.",
    'Long Wavy Hair':  'Довге хвилясте волосся — природно та красиво.',
    'Mod Cut':         'Британська стрижка 60-х із прямим чубчиком.',
    'Brush Up Fade':   "Зачесаний догори верх із фейдом — свіжо та сучасно.",
    'Undercut':        'Виголені боки з довгим верхом — контрастно та сміливо.',
    'Faux Hawk':       'Несправжній ірокез — стильно без зайвої екстравагантності.',
    'Crew Cut':        'Коротка класична стрижка — практично та охайно.',
    'Buzz Cut':        'Рівномірно коротко по всій голові — мінімалізм.',
    'Bob':             'Класичний боб — вічна жіноча стрижка до підборіддя.',
    'Pixie Cut':       'Дуже коротка жіноча стрижка з характером.',
    'Каре':            'Рівний зріз по лінії щелепи — елегантно та практично.',
    'Кучерявий Боб':   'Боб із кучерями — пружно та жіночно.',
    'Піксі':           'Коротка стрижка з легкою текстурою.',
    'Гарсон':          'Хлопчача жіноча стрижка — сміливо та стильно.',
    'Сесон':           'Рівний зріз із чубчиком — класика французького стилю.',
    'Їжачок':          'Дуже коротка рівномірна стрижка.',
    'Шеггі':           "Багатошарова стрижка з рваними кінчиками та об'ємом.",
}


def get_description(name):
    if name in POPULAR_DESCRIPTIONS:
        return POPULAR_DESCRIPTIONS[name]
    if name in EXTRA_WOMEN_STYLE_DESCRIPTIONS:
        return EXTRA_WOMEN_STYLE_DESCRIPTIONS[name]
    if name in EXTRA_MEN_STYLE_DESCRIPTIONS:
        return EXTRA_MEN_STYLE_DESCRIPTIONS[name]
    length = HAIRSTYLE_LENGTH.get(name, '')
    length_label = HAIRSTYLE_LENGTH_LABELS.get(length, '')
    return f"Стрижка «{name}»." + (f' Довжина: {length_label}.' if length_label else '')


def get_category(name):
    if name in WOMEN_HAIRSTYLES and name not in MEN_HAIRSTYLES:
        return 'women'
    if name in MEN_HAIRSTYLES and name not in WOMEN_HAIRSTYLES:
        return 'men'
    return 'unisex'


def build_name_to_image_map():
    """Будує зворотню мапу: назва зачіски → перший існуючий файл."""
    hairstyles_dir = os.path.join(settings.MEDIA_ROOT, 'hairstyles')
    name_to_file = {}

    for filename, hairstyle_name in IMAGE_MAP.items():
        if hairstyle_name in name_to_file:
            continue  # вже знайшли файл для цієї зачіски
        filepath = os.path.join(hairstyles_dir, filename)
        if os.path.isfile(filepath):
            name_to_file[hairstyle_name] = os.path.join('hairstyles', filename)

    return name_to_file


class Command(BaseCommand):
    help = "Заповнює базу даних зачісками з constants.py і прив'язує зображення"

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Перезаписати опис, категорію та зображення навіть якщо зачіска вже існує',
        )

    def handle(self, *args, **options):
        force = options['force']

        all_names = (
            POPULAR_HAIRSTYLE_NAMES
            + [n for n in EXTRA_WOMEN_HAIRSTYLE_NAMES if n not in POPULAR_HAIRSTYLE_NAMES]
            + [n for n in EXTRA_MEN_HAIRSTYLE_NAMES if n not in POPULAR_HAIRSTYLE_NAMES]
        )

        name_to_image = build_name_to_image_map()

        created_count = 0
        updated_count = 0
        image_count = 0
        no_image = []

        for name in all_names:
            description = get_description(name)
            category = get_category(name)
            image_path = name_to_image.get(name)

            defaults = {
                'description': description,
                'category': category,
                'name_en': name,
            }
            if image_path:
                defaults['image'] = image_path

            obj, created = Hairstyle.objects.get_or_create(name=name, defaults=defaults)

            if created:
                created_count += 1
                img_marker = '🖼' if image_path else '—'
                self.stdout.write(f'  ✓ {name} [{category}] {img_marker}')
                if image_path:
                    image_count += 1
            elif force:
                obj.description = description
                obj.category = category
                if image_path:
                    obj.image = image_path
                    image_count += 1
                obj.save()
                updated_count += 1
                self.stdout.write(f'  ↻ {name} [{category}]')
            else:
                # Зачіска є але без зображення — тихо додаємо
                if image_path and not obj.image:
                    obj.image = image_path
                    obj.save()
                    image_count += 1
                    self.stdout.write(f'  🖼  Зображення додано: {name}')

            if not image_path:
                no_image.append(name)

        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS(
            f'Готово! Створено: {created_count}, оновлено: {updated_count}, '
            f"зображень прив'язано: {image_count} / {len(all_names)}"
        ))

        if no_image:
            self.stdout.write(self.style.WARNING(
                f'\n⚠️ Зображення не знайдено для {len(no_image)} зачісок:'
            ))
            for n in no_image:
                self.stdout.write(f'   - {n}')
            self.stdout.write(
                '\nДодай файли в media/hairstyles/ і знову запусти команду.'
            )