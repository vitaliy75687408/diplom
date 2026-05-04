# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand
from hairstyles.models import Hairstyle


class Command(BaseCommand):
    help = 'Додає розширений список зачісок: тейпер, фейд, цезар, боб тощо'

    def handle(self, *args, **options):
        self.stdout.write('Додавання зачісок...')

        styles = [
            # Популярні стилі (як на головній)
            {'name': 'Довгий каскад (жін.)', 'name_en': 'Long cascade', 'description': 'Каскад на довге волосся.', 'category': 'women', 'master_count': 2700},
            {'name': 'Боб', 'name_en': 'Bob', 'description': 'Елегантна коротка стрижка.', 'category': 'women', 'master_count': 2670},
            {'name': 'Текстурована', 'name_en': 'Textured', 'description': 'Природні текстури волосся.', 'category': 'unisex', 'master_count': 2600},
            {'name': 'Андеркат (чол.)', 'name_en': 'Undercut', 'description': 'Стильна коротка стрижка з переходом.', 'category': 'men', 'master_count': 3200},
            {'name': 'Помпадур (чол.)', 'name_en': 'Pompadour', 'description': 'Класичний об\'єм та стиль.', 'category': 'men', 'master_count': 2950},
            # Чоловічі
            {'name': 'Тейпер фейд', 'name_en': 'Taper Fade', 'description': 'Класичний тейпер із плавним фейдом по краях.', 'category': 'men', 'master_count': 2100},
            {'name': 'Цезар', 'name_en': 'Caesar', 'description': 'Коротка рівна челка та однакова довжина по об\'єму.', 'category': 'men', 'master_count': 1800},
            {'name': 'Маллет', 'name_en': 'Mullet', 'description': 'Коротко спереду та по боках, довго ззаду.', 'category': 'men', 'master_count': 950},
            {'name': 'Textured Flow Fade', 'name_en': 'Textured Flow Fade', 'description': 'Фейд із довшим текстурованим верхом.', 'category': 'men', 'master_count': 1650},
            {'name': 'Curly Top Fade', 'name_en': 'Curly Top Fade', 'description': 'Фейд із природними кучерями зверху.', 'category': 'men', 'master_count': 1200},
            {'name': 'Modern Slick Back', 'name_en': 'Modern Slick Back', 'description': 'Волосся назад із блиском.', 'category': 'men', 'master_count': 1400},
            {'name': 'Ultra-Low Buzz Cut', 'name_en': 'Ultra-Low Buzz Cut', 'description': 'Дуже коротка стрижка «майже під нуль».', 'category': 'men', 'master_count': 1100},
            {'name': 'Micro Fringe Crop', 'name_en': 'Micro Fringe Crop', 'description': 'Коротка челка/франж із мінімальною довжиною.', 'category': 'men', 'master_count': 980},
            {'name': 'Disconnected Undercut', 'name_en': 'Disconnected Undercut', 'description': 'Різкий контраст між довжинами.', 'category': 'men', 'master_count': 1750},
            {'name': 'Classic Taper with Side Part', 'name_en': 'Classic Taper with Side Part', 'description': 'Класичний труп із проділом.', 'category': 'men', 'master_count': 1900},
            {'name': 'Textured Quiff', 'name_en': 'Textured Quiff', 'description': 'Об\'єм з передньої частини.', 'category': 'men', 'master_count': 1600},
            {'name': 'Messy Medium Waves', 'name_en': 'Messy Medium Waves', 'description': 'Середня довжина з недбалими хвилями.', 'category': 'men', 'master_count': 1300},
            {'name': 'Brush Up Fade', 'name_en': 'Brush Up Fade', 'description': 'Вертикальний об\'єм вперед з фейдом.', 'category': 'men', 'master_count': 1450},
            {'name': 'Faux Hawk Fade', 'name_en': 'Faux Hawk Fade', 'description': '«Фальшивий» ірокез із фейдом.', 'category': 'men', 'master_count': 1250},
            {'name': 'Hard Part + Fade', 'name_en': 'Hard Part + Fade', 'description': 'Чіткий проділ ножем та фейд.', 'category': 'men', 'master_count': 1550},
            {'name': 'Curtain Bangs for Men', 'name_en': 'Curtain Bangs for Men', 'description': 'Чоловічі «штори» на середніх волоссі.', 'category': 'men', 'master_count': 1150},
            {'name': 'Textured Pompadour', 'name_en': 'Textured Pompadour', 'description': 'Сучасний текстурований помпадур.', 'category': 'men', 'master_count': 1680},
            {'name': 'Long Layered Cut (чол.)', 'name_en': 'Long Layered Cut', 'description': 'Довше волосся з шарами.', 'category': 'men', 'master_count': 1050},
            # Жіночі
            {'name': 'Baroque Bob', 'name_en': 'Baroque Bob', 'description': 'Елегантний боб з об\'ємними хвилями.', 'category': 'women', 'master_count': 2200},
            {'name': 'Cowgirl Cut', 'name_en': 'Cowgirl Cut', 'description': 'Шарувата середня довжина з м\'якими кінчиками.', 'category': 'women', 'master_count': 1850},
            {'name': 'Butterfly Cut', 'name_en': 'Butterfly Cut', 'description': 'Багатошаровий стиль із рухом.', 'category': 'women', 'master_count': 2400},
            {'name': 'Bixie Cut', 'name_en': 'Bixie Cut', 'description': 'Мікс між бобом і піксі.', 'category': 'women', 'master_count': 1950},
            {'name': 'Soft Curtain Bangs', 'name_en': 'Soft Curtain Bangs', 'description': 'Легкі «штори» чубчика.', 'category': 'women', 'master_count': 2100},
            {'name': 'Textured Waves', 'name_en': 'Textured Waves', 'description': 'Природні текстуровані хвилі.', 'category': 'women', 'master_count': 2600},
            {'name': 'Romance Waves', 'name_en': 'Romance Waves', 'description': 'М\'які романтичні хвилі.', 'category': 'women', 'master_count': 2300},
            {'name': "90's Bob", 'name_en': "90's Bob", 'description': 'Боб у стилі 90-х з сучасною обробкою.', 'category': 'women', 'master_count': 1750},
            {'name': 'Long Layered Cut (жін.)', 'name_en': 'Long Layered Cut', 'description': 'Каскад на довге волосся.', 'category': 'women', 'master_count': 2700},
            {'name': 'Sleek Low Pony', 'name_en': 'Sleek Low Pony', 'description': 'Гладка низька хвиля.', 'category': 'women', 'master_count': 2050},
            {'name': 'Half-Up Twisted Bun', 'name_en': 'Half-Up Twisted Bun', 'description': 'Напівпучок із закрутками.', 'category': 'women', 'master_count': 1880},
            {'name': 'Microwave Curls', 'name_en': 'Microwave Curls', 'description': 'Дрібні пружні кучері.', 'category': 'women', 'master_count': 2150},
            {'name': 'Face-Framing Layers', 'name_en': 'Face-Framing Layers', 'description': 'Шари, що обрамляють обличчя.', 'category': 'women', 'master_count': 2450},
            {'name': 'Shaggy Lob', 'name_en': 'Shaggy Lob', 'description': 'Недбалий лоб із шарами.', 'category': 'women', 'master_count': 1980},
            {'name': 'Side-Swept Braids', 'name_en': 'Side-Swept Braids', 'description': 'Коси набік.', 'category': 'women', 'master_count': 1720},
        ]

        for s in styles:
            obj, created = Hairstyle.objects.get_or_create(
                name=s['name'],
                defaults={
                    'name_en': s.get('name_en', s['name']),
                    'description': s['description'],
                    'category': s['category'],
                    'master_count': s['master_count'],
                }
            )
            if created:
                self.stdout.write(f'  + {obj.name}')

        self.stdout.write(self.style.SUCCESS(f'Готово. Всього зачісок: {Hairstyle.objects.count()}'))
