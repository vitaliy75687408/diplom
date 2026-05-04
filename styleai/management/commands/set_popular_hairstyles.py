# -*- coding: utf-8 -*-
"""
Список «Популярні зачіски»: Drop Fade, Taper Fade, Low Fade, Mid Fade, Textured Crop,
Burst Fade, Edgar Cut, Slick Back, Long Wavy Hair, Mod Cut.
Прив'язка до форм обличчя для точного підбору.
Запуск: python manage.py set_popular_hairstyles
"""
from django.core.management.base import BaseCommand
from django.db import transaction
from hairstyles.models import Hairstyle, FaceShape


# Порядок на сайті: спочатку короткі/фейди, потім подовжені
HAIRSTYLES_DATA = [
    # Короткі / фейди
    {'name': 'Drop Fade', 'name_en': 'Drop Fade', 'description': 'Фейд із опущенням лінії по потилиці.', 'category': 'men', 'master_count': 3100},
    {'name': 'Taper Fade', 'name_en': 'Taper Fade', 'description': 'Тейпер із плавним переходом по краях.', 'category': 'men', 'master_count': 3000},
    {'name': 'Low Fade', 'name_en': 'Low Fade', 'description': 'Низький фейд від вух.', 'category': 'men', 'master_count': 2900},
    {'name': 'Mid Fade', 'name_en': 'Mid Fade', 'description': 'Середній фейд по всьому периметру.', 'category': 'men', 'master_count': 2850},
    {'name': 'High Fade', 'name_en': 'High Fade', 'description': 'Високий фейд, волосся зверху довше.', 'category': 'men', 'master_count': 2820},
    {'name': 'Skin Fade', 'name_en': 'Skin Fade', 'description': 'Фейд під нуль по краях.', 'category': 'men', 'master_count': 2800},
    {'name': 'Textured Crop', 'name_en': 'Textured Crop', 'description': 'Короткий кроп з текстурою зверху.', 'category': 'men', 'master_count': 2780},
    {'name': 'Burst Fade', 'name_en': 'Burst Fade', 'description': 'Фейд із «вибухом» об\'єму над вухами.', 'category': 'men', 'master_count': 2750},
    {'name': 'Edgar Cut', 'name_en': 'Edgar Cut', 'description': 'Короткі боки, чубчик уперед і вгору.', 'category': 'men', 'master_count': 2700},
    {'name': 'Slick Back', 'name_en': 'Slick Back', 'description': 'Волосся зачесане назад з фіксацією.', 'category': 'men', 'master_count': 2650},
    {'name': 'Pompadour', 'name_en': 'Pompadour', 'description': 'Класичний помпадур з об\'ємом зверху.', 'category': 'men', 'master_count': 2620},
    {'name': 'Quiff', 'name_en': 'Quiff', 'description': 'Чуб із підняттям уперед і вбік.', 'category': 'men', 'master_count': 2600},
    {'name': 'Long Wavy Hair', 'name_en': 'Long Wavy Hair', 'description': 'Довге хвилясте волосся.', 'category': 'men', 'master_count': 2580},
    {'name': 'Mod Cut', 'name_en': 'Mod Cut', 'description': 'Сучасна стрижка середньої довжини з чіткими лініями.', 'category': 'men', 'master_count': 2550},
    {'name': 'Brush Up Fade', 'name_en': 'Brush Up Fade', 'description': 'Вертикальний об\'єм вперед з фейдом.', 'category': 'men', 'master_count': 2520},
    {'name': 'Undercut', 'name_en': 'Undercut', 'description': 'Короткі або виголені боки, довге зверху.', 'category': 'men', 'master_count': 2500},
    {'name': 'Faux Hawk', 'name_en': 'Faux Hawk', 'description': 'Імітація ірокеза, пом\'якшений варіант.', 'category': 'men', 'master_count': 2480},
    {'name': 'Crew Cut', 'name_en': 'Crew Cut', 'description': 'Коротка військова стрижка.', 'category': 'men', 'master_count': 2450},
    {'name': 'Buzz Cut', 'name_en': 'Buzz Cut', 'description': 'Рівномірно дуже коротка стрижка.', 'category': 'men', 'master_count': 2420},
    {'name': 'Bob', 'name_en': 'Bob', 'description': 'Каре, класична стрижка до підборіддя.', 'category': 'women', 'master_count': 2400},
    {'name': 'Pixie Cut', 'name_en': 'Pixie Cut', 'description': 'Коротка жіноча стрижка піксі.', 'category': 'women', 'master_count': 2380},
    # Жіночі зачіски
    {'name': 'Каре', 'name_en': 'Kare', 'description': 'Класичне каре, рівний або скошений крок.', 'category': 'women', 'master_count': 2350},
    {'name': 'Кучерявий Боб', 'name_en': 'Curly Bob', 'description': 'Короткий кучерявий боб, об\'ємна форма.', 'category': 'women', 'master_count': 2320},
    {'name': 'Піксі', 'name_en': 'Pixie', 'description': 'Коротка жіноча стрижка піксі.', 'category': 'women', 'master_count': 2300},
    {'name': 'Гарсон', 'name_en': 'Garcon', 'description': 'Коротка стрижка в стилі гарсон.', 'category': 'women', 'master_count': 2280},
    {'name': 'Сесон', 'name_en': 'Saison', 'description': 'Стрижка сезон — багатошаровий об\'єм.', 'category': 'women', 'master_count': 2260},
    {'name': 'Їжачок', 'name_en': 'Hedgehog', 'description': 'Коротка стрижка їжачок, підняте волосся.', 'category': 'women', 'master_count': 2240},
    {'name': 'Шеггі', 'name_en': 'Shaggy', 'description': 'Шеггі — багатошарова рвана стрижка.', 'category': 'women', 'master_count': 2220},
]

# Які зачіски підходять для кожної форми обличчя (для точного підбору)
WOMEN_STYLES = ['Bob', 'Pixie Cut', 'Каре', 'Кучерявий Боб', 'Піксі', 'Гарсон', 'Сесон', 'Їжачок', 'Шеггі']
ALL_STYLE_NAMES = [
    'Drop Fade', 'Taper Fade', 'Low Fade', 'Mid Fade', 'High Fade', 'Skin Fade',
    'Textured Crop', 'Burst Fade', 'Edgar Cut', 'Slick Back', 'Pompadour', 'Quiff',
    'Long Wavy Hair', 'Mod Cut', 'Brush Up Fade', 'Undercut', 'Faux Hawk',
    'Crew Cut', 'Buzz Cut', 'Bob', 'Pixie Cut', 'Каре', 'Кучерявий Боб', 'Піксі', 'Гарсон', 'Сесон', 'Їжачок', 'Шеггі',
]
FACE_SHAPE_HAIRSTYLES = {
    'Овальна': ALL_STYLE_NAMES,
    'Кругла': ['Textured Crop', 'Burst Fade', 'Edgar Cut', 'Slick Back', 'Long Wavy Hair', 'Mod Cut', 'Brush Up Fade', 'Pompadour', 'Quiff', 'Bob', 'Pixie Cut'] + WOMEN_STYLES,
    'Квадратна': ['Taper Fade', 'Low Fade', 'Mid Fade', 'Long Wavy Hair', 'Mod Cut', 'Slick Back', 'Brush Up Fade', 'Undercut', 'Bob', 'Pixie Cut'] + WOMEN_STYLES,
    'Довга': ['Mid Fade', 'Burst Fade', 'Edgar Cut', 'Textured Crop', 'Drop Fade', 'Slick Back', 'Brush Up Fade', 'Pompadour', 'Quiff', 'Bob'] + WOMEN_STYLES,
}


class Command(BaseCommand):
    help = 'Встановлює 10 популярних зачісок та прив\'язку до форм обличчя'

    def handle(self, *args, **options):
        with transaction.atomic():
            for i, data in enumerate(HAIRSTYLES_DATA):
                style, created = Hairstyle.objects.update_or_create(
                    name=data['name'],
                    defaults={
                        'name_en': data['name_en'],
                        'description': data['description'],
                        'category': data['category'],
                        'master_count': data['master_count'],
                    }
                )
                self.stdout.write(f'  {"+" if created else "~"} {style.name}')

            for shape_name, style_names in FACE_SHAPE_HAIRSTYLES.items():
                try:
                    shape = FaceShape.objects.get(name=shape_name)
                except FaceShape.DoesNotExist:
                    self.stdout.write(self.style.WARNING('  Face shape "%s" not found, skip.' % shape_name))
                    continue
                styles = list(Hairstyle.objects.filter(name__in=style_names))
                shape.suitable_hairstyles.set(styles)
                self.stdout.write('  %s: %s styles' % (shape_name, len(styles)))

        self.stdout.write(self.style.SUCCESS('Done. Hairstyles and face-shape links updated.'))
