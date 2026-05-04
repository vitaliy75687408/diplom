from django.core.management.base import BaseCommand
from django.core.files import File
from pathlib import Path
from django.conf import settings
from hairstyles.models import Hairstyle, FaceShape
from masters.models import Master, Review


class Command(BaseCommand):
    help = 'Creates sample data for the StyleAI application'

    def handle(self, *args, **options):
        self.stdout.write('Creating sample data...')
        
        # Create Face Shapes
        face_shapes_data = [
            {'name': 'Овальна', 'description': 'Універсальна форма, підходить для більшості зачісок'},
            {'name': 'Кругла', 'description': 'Потребує зачісок, які додають довжину'},
            {'name': 'Квадратна', 'description': 'Потребує м\'яких ліній та об\'єму'},
            {'name': 'Довга', 'description': 'Потребує зачісок, які додають ширину'},
        ]
        
        face_shapes = {}
        for shape_data in face_shapes_data:
            shape, created = FaceShape.objects.get_or_create(
                name=shape_data['name'],
                defaults=shape_data
            )
            face_shapes[shape_data['name']] = shape
            if created:
                self.stdout.write(f'Created face shape: {shape.name}')
        
        # Create Hairstyles
        hairstyles_data = [
            {
                'name': 'Undercut',
                'name_en': 'Undercut',
                'description': 'Класичний чоловічий стиль',
                'category': 'men',
                'master_count': 2340,
                'image_file': 'undercut.jpg',
            },
            {
                'name': 'Каскад',
                'name_en': 'Cascade',
                'description': 'Багатошарова жіноча стрижка',
                'category': 'women',
                'master_count': 3120,
                'image_file': 'cascade.jpg',
            },
            {
                'name': 'Fade',
                'name_en': 'Fade',
                'description': 'Плавний перехід довжини',
                'category': 'men',
                'master_count': 1890,
                'image_file': 'fade.jpg',
            },
            {
                'name': 'Боб',
                'name_en': 'Bob',
                'description': 'Елегантна коротка стрижка',
                'category': 'women',
                'master_count': 2670,
                'image_file': 'bob.jpg',
            },
        ]
        
        hairstyles = {}
        media_dir = Path(settings.MEDIA_ROOT)
        for style_data in hairstyles_data:
            image_file = style_data.pop('image_file', None)
            style, created = Hairstyle.objects.get_or_create(
                name=style_data['name'],
                defaults=style_data
            )
            # Додаємо зображення якщо воно існує
            if created and image_file:
                image_path = media_dir / 'hairstyles' / image_file
                if image_path.exists():
                    with open(image_path, 'rb') as f:
                        style.image.save(image_file, File(f), save=True)
            hairstyles[style_data['name']] = style
            if created:
                self.stdout.write(f'Created hairstyle: {style.name}')
        
        # Create Masters (без фото — фото можна додати в адмінці)
        masters_data = [
            {'first_name': 'Олександр', 'last_name': 'Коваль', 'profession': 'barber', 'experience_years': 8, 'city': 'Київ', 'district': 'Печерськ', 'rating': 4.9, 'specialties': ['Undercut', 'Fade']},
            {'first_name': 'Марія', 'last_name': 'Петренко', 'profession': 'stylist', 'experience_years': 10, 'city': 'Львів', 'district': 'Центр', 'rating': 5.0, 'specialties': ['Каскад', 'Боб']},
            {'first_name': 'Дмитро', 'last_name': 'Шевченко', 'profession': 'barber', 'experience_years': 6, 'city': 'Одеса', 'district': 'Аркадія', 'rating': 4.8, 'specialties': ['Fade']},
            {'first_name': 'Андрій', 'last_name': 'Мельник', 'profession': 'barber', 'experience_years': 5, 'city': 'Київ', 'district': 'Шевченківський', 'rating': 4.7, 'specialties': ['Undercut', 'Fade']},
            {'first_name': 'Олена', 'last_name': 'Кравченко', 'profession': 'stylist', 'experience_years': 7, 'city': 'Харків', 'district': 'Центр', 'rating': 4.9, 'specialties': ['Каскад', 'Боб']},
            {'first_name': 'Ігор', 'last_name': 'Бондаренко', 'profession': 'barber', 'experience_years': 12, 'city': 'Дніпро', 'district': '', 'rating': 5.0, 'specialties': ['Fade', 'Undercut']},
            {'first_name': 'Наталія', 'last_name': 'Ткаченко', 'profession': 'stylist', 'experience_years': 9, 'city': 'Львів', 'district': 'Франківський', 'rating': 4.8, 'specialties': ['Боб', 'Каскад']},
            {'first_name': 'Сергій', 'last_name': 'Кравцов', 'profession': 'barber', 'experience_years': 4, 'city': 'Запоріжжя', 'district': '', 'rating': 4.6, 'specialties': ['Fade']},
            {'first_name': 'Катерина', 'last_name': 'Оніщенко', 'profession': 'colorist', 'experience_years': 6, 'city': 'Київ', 'district': 'Подільський', 'rating': 4.9, 'specialties': ['Каскад', 'Боб']},
            {'first_name': 'Максим', 'last_name': 'Лисенко', 'profession': 'barber', 'experience_years': 3, 'city': 'Вінниця', 'district': '', 'rating': 4.5, 'specialties': ['Undercut']},
            {'first_name': 'Юлія', 'last_name': 'Савченко', 'profession': 'stylist', 'experience_years': 8, 'city': 'Одеса', 'district': 'Приморський', 'rating': 4.9, 'specialties': ['Боб']},
            {'first_name': 'Віталій', 'last_name': 'Павленко', 'profession': 'barber', 'experience_years': 11, 'city': 'Київ', 'district': 'Оболонь', 'rating': 5.0, 'specialties': ['Fade', 'Undercut']},
            {'first_name': 'Анна', 'last_name': 'Коваленко', 'profession': 'stylist', 'experience_years': 5, 'city': 'Львів', 'district': 'Личаківський', 'rating': 4.7, 'specialties': ['Каскад']},
            {'first_name': 'Олег', 'last_name': 'Сидоренко', 'profession': 'barber', 'experience_years': 7, 'city': 'Харків', 'district': 'Салтівка', 'rating': 4.8, 'specialties': ['Fade', 'Undercut']},
            {'first_name': 'Тетяна', 'last_name': 'Гриценко', 'profession': 'colorist', 'experience_years': 10, 'city': 'Дніпро', 'district': 'Центр', 'rating': 5.0, 'specialties': ['Каскад', 'Боб']},
            {'first_name': 'Роман', 'last_name': 'Федоренко', 'profession': 'barber', 'experience_years': 4, 'city': 'Івано-Франківськ', 'district': '', 'rating': 4.6, 'specialties': ['Undercut']},
            {'first_name': 'Ірина', 'last_name': 'Марченко', 'profession': 'stylist', 'experience_years': 6, 'city': 'Чернігів', 'district': '', 'rating': 4.8, 'specialties': ['Боб', 'Каскад']},
            {'first_name': 'Вадим', 'last_name': 'Клименко', 'profession': 'barber', 'experience_years': 9, 'city': 'Київ', 'district': 'Солом’янський', 'rating': 4.9, 'specialties': ['Fade']},
            {'first_name': 'Софія', 'last_name': 'Захарченко', 'profession': 'stylist', 'experience_years': 4, 'city': 'Полтава', 'district': '', 'rating': 4.5, 'specialties': ['Каскад']},
            {'first_name': 'Артем', 'last_name': 'Руденко', 'profession': 'barber', 'experience_years': 5, 'city': 'Львів', 'district': 'Сихів', 'rating': 4.7, 'specialties': ['Undercut', 'Fade']},
        ]
        
        for master_data in masters_data:
            specialties = master_data.pop('specialties')
            master, created = Master.objects.get_or_create(
                first_name=master_data['first_name'],
                last_name=master_data['last_name'],
                defaults=master_data
            )
            if created:
                for specialty_name in specialties:
                    if specialty_name in hairstyles:
                        master.specialties.add(hairstyles[specialty_name])
                self.stdout.write(f'Created master: {master.full_name}')
        
        # Create Reviews
        reviews_data = [
            {
                'master': 'Олександр Коваль',
                'author_name': 'Андрій М.',
                'rating': 5,
                'text': 'АІ підбір зачіски допіг знайти ідеальний стиль! Раніше завжди сумнівався, але тепер впевнений у своєму виборі. Майстер зробив все ідеально!',
            },
            {
                'master': 'Марія Петренко',
                'author_name': 'Олена К.',
                'rating': 5,
                'text': 'Чудовий сервіс! Знайшла свого майстра за лічені хвилини. Зачіска перевершила всі очікування. Рекомендую всім подругам!',
            },
            {
                'master': 'Дмитро Шевченко',
                'author_name': 'Максим П.',
                'rating': 5,
                'text': 'Технологія дійсно працюе! Al точно визначив, яка зачіска мені підходить. Барбер виявився професіоналом. Дуже задоволений!',
            },
        ]
        
        for review_data in reviews_data:
            master_name = review_data.pop('master')
            master = Master.objects.filter(
                first_name=master_name.split()[0],
                last_name=master_name.split()[1]
            ).first()
            if master:
                review_data['master'] = master
                review, created = Review.objects.get_or_create(
                    master=master,
                    author_name=review_data['author_name'],
                    defaults=review_data
                )
                if created:
                    self.stdout.write(f'Created review from {review.author_name}')
        
        self.stdout.write(self.style.SUCCESS('Sample data created successfully!'))
