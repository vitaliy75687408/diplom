# -*- coding: utf-8 -*-
"""
Додає майстрів (барберів/стилістів) у базу даних для пошуку на сторінці «Знайдіть майстра».
Кожна популярна зачіска має кілька майстрів.

Працює з SQLite та MySQL.
Запуск: python manage.py add_10_masters
"""
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.db import transaction
from django.core.files.base import ContentFile
import os

from hairstyles.models import Hairstyle
from masters.models import Master
from styleai.constants import POPULAR_HAIRSTYLE_NAMES


# Кожен барбер/майстер має унікальний набір стрижок — без однакових наборів між собою.
# При записі до конкретного майстра в модалці показуються лише його зачіски (різні для кожного).
MASTERS_DATA = [
    # Барбери — різні спеціалізації
    {'first_name': 'Олександр', 'last_name': 'Коваленко', 'profession': 'barber', 'city': 'Київ', 'district': 'Подільський', 'experience_years': 8, 'rating': Decimal('4.9'), 'default_price': Decimal('350'), 'style_names': ['Drop Fade', 'Low Fade', 'High Fade', 'Каре', 'Піксі']},
    {'first_name': 'Дмитро', 'last_name': 'Шевченко', 'profession': 'barber', 'city': 'Київ', 'district': 'Шевченківський', 'experience_years': 5, 'rating': Decimal('4.7'), 'default_price': Decimal('300'), 'style_names': ['Taper Fade', 'Mid Fade', 'Skin Fade', 'Гарсон', 'Їжачок']},
    {'first_name': 'Ігор', 'last_name': 'Бондаренко', 'profession': 'barber', 'city': 'Київ', 'district': 'Солом\'янський', 'experience_years': 6, 'rating': Decimal('4.8'), 'default_price': Decimal('320'), 'style_names': ['Brush Up Fade', 'Burst Fade', 'Кучерявий Боб', 'Шеггі']},
    {'first_name': 'Ігор', 'last_name': 'Мельник', 'profession': 'barber', 'city': 'Львів', 'district': '', 'experience_years': 6, 'rating': Decimal('4.8'), 'default_price': Decimal('320'), 'style_names': ['Edgar Cut', 'Low Fade', 'Піксі', 'Сесон']},
    {'first_name': 'Андрій', 'last_name': 'Бондаренко', 'profession': 'barber', 'city': 'Харків', 'district': 'Холодногірський', 'experience_years': 4, 'rating': Decimal('4.6'), 'default_price': Decimal('280'), 'style_names': ['Slick Back', 'Mod Cut', 'Pompadour', 'Каре', 'Гарсон']},
    {'first_name': 'Сергій', 'last_name': 'Кравцов', 'profession': 'barber', 'city': 'Запоріжжя', 'district': '', 'experience_years': 4, 'rating': Decimal('4.6'), 'default_price': Decimal('270'), 'style_names': ['Textured Crop', 'Taper Fade']},
    {'first_name': 'Роман', 'last_name': 'Федоренко', 'profession': 'barber', 'city': 'Івано-Франківськ', 'district': '', 'experience_years': 5, 'rating': Decimal('4.7'), 'default_price': Decimal('290'), 'style_names': ['Mid Fade', 'Burst Fade']},
    {'first_name': 'Максим', 'last_name': 'Ткаченко', 'profession': 'barber', 'city': 'Одеса', 'district': 'Приморський', 'experience_years': 7, 'rating': Decimal('4.9'), 'default_price': Decimal('340'), 'style_names': ['Drop Fade', 'Edgar Cut', 'Quiff']},
    {'first_name': 'Віталій', 'last_name': 'Гриценко', 'profession': 'barber', 'city': 'Київ', 'district': 'Оболонський', 'experience_years': 5, 'rating': Decimal('4.7'), 'default_price': Decimal('310'), 'style_names': ['Low Fade', 'Mid Fade']},
    {'first_name': 'Юрій', 'last_name': 'Лисенко', 'profession': 'barber', 'city': 'Львів', 'district': 'Франківський', 'experience_years': 4, 'rating': Decimal('4.6'), 'default_price': Decimal('290'), 'style_names': ['Brush Up Fade', 'Textured Crop']},
    {'first_name': 'Олег', 'last_name': 'Сидоренко', 'profession': 'barber', 'city': 'Харків', 'district': 'Шевченківський', 'experience_years': 6, 'rating': Decimal('4.8'), 'default_price': Decimal('300'), 'style_names': ['Drop Fade', 'Mid Fade', 'Undercut']},
    {'first_name': 'Михайло', 'last_name': 'Павленко', 'profession': 'barber', 'city': 'Дніпро', 'district': '', 'experience_years': 7, 'rating': Decimal('4.9'), 'default_price': Decimal('330'), 'style_names': ['Edgar Cut', 'Brush Up Fade']},
    {'first_name': 'Станіслав', 'last_name': 'Козак', 'profession': 'barber', 'city': 'Вінниця', 'district': '', 'experience_years': 4, 'rating': Decimal('4.5'), 'default_price': Decimal('260'), 'style_names': ['Slick Back', 'Taper Fade', 'Faux Hawk', 'Їжачок', 'Шеггі']},
    {'first_name': 'Артем', 'last_name': 'Мороз', 'profession': 'barber', 'city': 'Чернігів', 'district': '', 'experience_years': 5, 'rating': Decimal('4.7'), 'default_price': Decimal('280'), 'style_names': ['Textured Crop', 'Low Fade', 'Crew Cut', 'Кучерявий Боб', 'Піксі']},
    {'first_name': 'Євген', 'last_name': 'Захарченко', 'profession': 'barber', 'city': 'Полтава', 'district': '', 'experience_years': 6, 'rating': Decimal('4.8'), 'default_price': Decimal('295'), 'style_names': ['Burst Fade', 'Edgar Cut', 'Buzz Cut']},
    {'first_name': 'Денис', 'last_name': 'Білоус', 'profession': 'barber', 'city': 'Хмельницький', 'district': '', 'experience_years': 3, 'rating': Decimal('4.4'), 'default_price': Decimal('250'), 'style_names': ['Drop Fade', 'Slick Back']},
    {'first_name': 'Назар', 'last_name': 'Тарасенко', 'profession': 'barber', 'city': 'Суми', 'district': '', 'experience_years': 4, 'rating': Decimal('4.5'), 'default_price': Decimal('265'), 'style_names': ['Mid Fade', 'Textured Crop']},
    # Стилісти
    {'first_name': 'Вадим', 'last_name': 'Коваль', 'profession': 'stylist', 'city': 'Київ', 'district': 'Печерський', 'experience_years': 10, 'rating': Decimal('5.0'), 'default_price': Decimal('400'), 'style_names': ['Long Wavy Hair', 'Mod Cut', 'Bob', 'Каре', 'Кучерявий Боб', 'Шеггі']},
    {'first_name': 'Марія', 'last_name': 'Петренко', 'profession': 'stylist', 'city': 'Львів', 'district': '', 'experience_years': 9, 'rating': Decimal('4.8'), 'default_price': Decimal('380'), 'style_names': ['Long Wavy Hair', 'Textured Crop', 'Pixie Cut', 'Піксі', 'Гарсон', 'Сесон']},
    {'first_name': 'Ілля', 'last_name': 'Семененко', 'profession': 'stylist', 'city': 'Харків', 'district': '', 'experience_years': 8, 'rating': Decimal('4.8'), 'default_price': Decimal('370'), 'style_names': ['Mod Cut', 'Slick Back', 'Каре', 'Їжачок']},
    {'first_name': 'Катерина', 'last_name': 'Кравченко', 'profession': 'stylist', 'city': 'Одеса', 'district': '', 'experience_years': 7, 'rating': Decimal('4.7'), 'default_price': Decimal('360'), 'style_names': ['Long Wavy Hair', 'Textured Crop', 'Mod Cut', 'Кучерявий Боб', 'Шеггі']},
    {'first_name': 'Анна', 'last_name': 'Шевчук', 'profession': 'stylist', 'city': 'Дніпро', 'district': '', 'experience_years': 6, 'rating': Decimal('4.6'), 'default_price': Decimal('350'), 'style_names': ['Long Wavy Hair', 'Bob', 'Каре', 'Піксі']},
    {'first_name': 'Владислав', 'last_name': 'Гончаренко', 'profession': 'barber', 'city': 'Черкаси', 'district': '', 'experience_years': 5, 'rating': Decimal('4.6'), 'default_price': Decimal('275'), 'style_names': ['Mod Cut', 'Textured Crop']},
    # Колористи
    {'first_name': 'Олена', 'last_name': 'Савченко', 'profession': 'colorist', 'city': 'Київ', 'district': 'Дарницький', 'experience_years': 6, 'rating': Decimal('4.7'), 'default_price': Decimal('450'), 'style_names': ['Long Wavy Hair', 'Textured Crop', 'Bob', 'Каре', 'Кучерявий Боб', 'Шеггі']},
    {'first_name': 'Наталія', 'last_name': 'Ковальчук', 'profession': 'colorist', 'city': 'Львів', 'district': '', 'experience_years': 8, 'rating': Decimal('4.9'), 'default_price': Decimal('420'), 'style_names': ['Long Wavy Hair', 'Mod Cut', 'Pixie Cut', 'Піксі', 'Гарсон', 'Сесон']},
    {'first_name': 'Тетяна', 'last_name': 'Бойко', 'profession': 'colorist', 'city': 'Харків', 'district': '', 'experience_years': 5, 'rating': Decimal('4.6'), 'default_price': Decimal('400'), 'style_names': ['Textured Crop', 'Каре', 'Їжачок']},
]


class Command(BaseCommand):
    help = 'Додає майстрів у базу (барбери, стилісти, колористи) — кожна зачіска має кілька майстрів'

    def add_arguments(self, parser):
        parser.add_argument('--replace', action='store_true', help='Видалити всіх майстрів і створити список заново (за замовчуванням лише додає нових).')
        parser.add_argument('--force-photo', action='store_true', help='Призначити локальні фото майстрам і перезаписати існуючі фото.')

    @transaction.atomic
    def handle(self, *args, **options):
        replace = options.get('replace', False)
        force_photo = options.get('force_photo', False)
        if replace:
            deleted, _ = Master.objects.all().delete()
            self.stdout.write(f'Видалено майстрів: {deleted}')

        # Переконатися, що є зачіски для прив'язки (назви як у POPULAR або з частиною, напр. Fade)
        all_style_names = set()
        for m in MASTERS_DATA:
            for name in m['style_names']:
                all_style_names.add(name)
        for name in POPULAR_HAIRSTYLE_NAMES:
            all_style_names.add(name)
        # Створюємо зачіски, якщо немає
        for name in all_style_names:
            Hairstyle.objects.get_or_create(
                name=name,
                defaults={
                    'name_en': name,
                    'description': f'Стиль: {name}.',
                    'category': 'men',
                    'master_count': 0,
                },
            )

        created = 0
        for data in MASTERS_DATA:
            style_names = data.pop('style_names')
            master, was_created = Master.objects.get_or_create(
                first_name=data['first_name'],
                last_name=data['last_name'],
                defaults={
                    **data,
                    'phone': '',
                    'email': '',
                },
            )
            if was_created:
                created += 1
            # Прив'язуємо спеціалізації (типи стрижок) — точна назва з бази
            for sname in style_names:
                style = Hairstyle.objects.filter(name=sname).first()
                if not style:
                    style = Hairstyle.objects.filter(name__icontains=sname).first()
                if style and not master.specialties.filter(pk=style.pk).exists():
                    master.specialties.add(style)
            if was_created:
                self.stdout.write(self.style.SUCCESS(f'  + {master.full_name} ({master.get_profession_display()}, {master.city})'))
            # Призначаємо локальне фото з медіа: використовуємо файли у media/masters, що починаються з 'work_'
            try:
                master_media_dir = os.path.join(os.getcwd(), 'media', 'masters')
                work_files = []
                if os.path.isdir(master_media_dir):
                    for fn in os.listdir(master_media_dir):
                        if fn.lower().startswith('work_') and os.path.isfile(os.path.join(master_media_dir, fn)):
                            work_files.append(fn)
                MASTER_WORK_PHOTOS = {
                    'Олександр Коваленко': 'Олександр_Коваленко_work_143.jpg',
                    'Максим Ткаченко': 'Максим_Ткаченко_work_116.jpg',
                    'Ігор Мельник': 'Ігор_Мельник_work_141.jpg',
                    'Катерина Кравченко': 'Катерина_Кравченко_work_107.jpg',
                    'Дмитро Шевченко': 'Дмитро_Шевченко_work_129.jpg',
                    'Артем Мороз': 'Артем_Мороз_work_126.jpg',
                    'Роман Федоренко': 'Роман_Федоренко_work_136.jpg',
                    'Віталій Гриценко': 'Віталій_Гриценко_work_113.jpg',
                    'Анна Шевчук': 'Анна_Шевчук_work_110.jpg',
                    'Юрій Лисенко': 'Юрій_Лисенко_work_109.jpg',
                    'Андрій Бондаренко': 'Андрій_Бондаренко_work_119.jpg',
                    'Назар Тарасенко': 'Назар_Тарасенко_work_134.jpg',
                    'Станіслав Козак': 'Станіслав_Козак_work_116.jpg',
                    'Денис Білоус': 'Денис_Білоус_work_140.jpg',
                }
                preferred = MASTER_WORK_PHOTOS.get(master.full_name)
                if preferred and os.path.exists(os.path.join(master_media_dir, preferred)):
                    photo_path = os.path.join(master_media_dir, preferred)
                elif work_files:
                    idx = abs(hash(master.full_name)) % len(work_files)
                    preferred = work_files[idx]
                    photo_path = os.path.join(master_media_dir, preferred)
                else:
                    # Запасний варіант: якщо work_* файлів немає, використовуємо наявні avatar-файли
                    avatar_dir = master_media_dir if os.path.isdir(master_media_dir) else os.path.join(os.getcwd(), 'static', 'images')
                    PHOTO_BY_FIRST = {
                        'Олександр': 'avatar_man1.png', 'Дмитро': 'avatar_man2.png', 'Ігор': 'avatar_man1.png',
                        'Віталій': 'avatar_man2.png', 'Іван': 'avatar_man1.png', 'Марія': 'avatar_woman.png',
                        'Тетяна': 'avatar_woman.png', 'Олена': 'avatar_woman.png', 'Андрій': 'avatar_man1.png',
                        'Сергій': 'avatar_man1.png', 'Роман': 'avatar_man2.png', 'Максим': 'avatar_man2.png',
                        'Вадим': 'avatar_man1.png', 'Юрій': 'avatar_man1.png', 'Олег': 'avatar_man1.png',
                        'Михайло': 'avatar_man1.png', 'Артем': 'avatar_man2.png', 'Наталія': 'avatar_woman.png',
                    }
                    preferred = PHOTO_BY_FIRST.get(master.first_name)
                    if not preferred:
                        preferred = 'avatar_man1.png' if master.profession == 'barber' else 'avatar_woman.png'
                    photo_path = os.path.join(avatar_dir, preferred)
                if (not master.photo) or force_photo:
                    if os.path.exists(photo_path):
                        with open(photo_path, 'rb') as f:
                            data_bytes = f.read()
                            filename = f"{master.first_name}_{master.last_name}_{preferred}"
                            master.photo.save(filename, ContentFile(data_bytes), save=True)
                            self.stdout.write(self.style.SUCCESS(f'  Фото призначено для {master.full_name}: {preferred}'))
                    else:
                        self.stdout.write(self.style.WARNING(f'  Не знайдено файл {preferred} у {os.path.dirname(photo_path)}'))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'  Помилка при призначенні фото для {master.full_name}: {e}'))

        # Гарантія: під кожну популярну зачіску є хоча б один майстер
        first_master = Master.objects.order_by('id').first()
        for name in POPULAR_HAIRSTYLE_NAMES:
            style = Hairstyle.objects.filter(name=name).first()
            if not style:
                style, _ = Hairstyle.objects.get_or_create(
                    name=name,
                    defaults={'name_en': name, 'description': f'Стиль: {name}.', 'category': 'men', 'master_count': 0},
                )
            has_master = Master.objects.filter(specialties=style).exists()
            if not has_master and first_master and not first_master.specialties.filter(pk=style.pk).exists():
                first_master.specialties.add(style)
                self.stdout.write(self.style.WARNING(f'  Прив\'язано зачіску «{name}» до майстра {first_master.full_name} (під усі зачіски є майстер).'))

        self.stdout.write(self.style.SUCCESS(f'Готово. Додано майстрів: {created}. Всього у базі: {Master.objects.count()}'))
        self.stdout.write('Запустіть python manage.py download_master_photos щоб завантажити їм фото з інтернету.')
