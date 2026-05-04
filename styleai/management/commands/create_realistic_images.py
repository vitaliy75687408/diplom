from django.core.management.base import BaseCommand
from PIL import Image, ImageDraw, ImageFilter
import os
from django.conf import settings
from pathlib import Path


class Command(BaseCommand):
    help = 'Creates realistic images of people with hairstyles and avatars'

    def handle(self, *args, **options):
        self.stdout.write('Creating realistic images...')
        
        media_dir = Path(settings.MEDIA_ROOT)
        static_dir = Path(settings.STATICFILES_DIRS[0]) if settings.STATICFILES_DIRS else Path(settings.STATIC_ROOT)
        
        os.makedirs(media_dir / 'hairstyles', exist_ok=True)
        os.makedirs(static_dir / 'images', exist_ok=True)
        
        # Створюємо зображення зачісок на людях
        hairstyle_images = [
            {
                'filename': 'undercut.jpg',
                'name': 'Undercut',
                'skin_color': (200, 170, 140),
                'hair_color': (40, 30, 25),
                'bg_color': (240, 240, 245),
                'hair_style': 'undercut',  # короткі боки, довгий верх
            },
            {
                'filename': 'cascade.jpg',
                'name': 'Каскад',
                'skin_color': (255, 220, 200),
                'hair_color': (255, 200, 150),
                'bg_color': (250, 245, 255),
                'hair_style': 'cascade',  # довге хвилясте волосся
            },
            {
                'filename': 'fade.jpg',
                'name': 'Fade',
                'skin_color': (180, 150, 120),
                'hair_color': (50, 40, 35),
                'bg_color': (245, 245, 250),
                'hair_style': 'fade',  # плавний перехід
            },
            {
                'filename': 'bob.jpg',
                'name': 'Боб',
                'skin_color': (255, 230, 210),
                'hair_color': (101, 67, 33),
                'bg_color': (255, 250, 255),
                'hair_style': 'bob',  # коротка стрижка до плечей
            },
        ]
        
        for style_data in hairstyle_images:
            img = self.create_person_with_hairstyle(
                style_data['skin_color'],
                style_data['hair_color'],
                style_data['bg_color'],
                style_data['hair_style']
            )
            img_path = media_dir / 'hairstyles' / style_data['filename']
            img.save(img_path, 'JPEG', quality=95)
            self.stdout.write(f'Created hairstyle: {img_path}')
        
        # Створюємо аватари для відгуків
        avatars = [
            {
                'filename': 'avatar_man1.png',
                'skin_color': (200, 170, 140),
                'hair_color': (50, 40, 35),
                'bg_color': (100, 150, 200),
                'gender': 'male',
            },
            {
                'filename': 'avatar_woman1.png',
                'skin_color': (255, 220, 200),
                'hair_color': (120, 80, 60),
                'bg_color': (200, 150, 200),
                'gender': 'female',
            },
            {
                'filename': 'avatar_man2.png',
                'skin_color': (180, 150, 120),
                'hair_color': (40, 30, 25),
                'bg_color': (150, 180, 220),
                'gender': 'male',
            },
        ]
        
        for avatar_data in avatars:
            img = self.create_realistic_avatar(
                avatar_data['skin_color'],
                avatar_data['hair_color'],
                avatar_data['bg_color'],
                avatar_data['gender']
            )
            img_path = static_dir / 'images' / avatar_data['filename']
            img.save(img_path, 'PNG')
            self.stdout.write(f'Created avatar: {img_path}')
        
        self.stdout.write(self.style.SUCCESS('All realistic images created successfully!'))

    def create_person_with_hairstyle(self, skin_color, hair_color, bg_color, hair_style):
        """Створює портрет людини з зачіскою"""
        width, height = 400, 500
        img = Image.new('RGB', (width, height), bg_color)
        draw = ImageDraw.Draw(img)
        
        # Фон - розмитий градієнт
        for y in range(height):
            ratio = y / height
            r = int(bg_color[0] * (1 - ratio) + bg_color[0] * 0.85 * ratio)
            g = int(bg_color[1] * (1 - ratio) + bg_color[1] * 0.85 * ratio)
            b = int(bg_color[2] * (1 - ratio) + bg_color[2] * 0.85 * ratio)
            draw.line([(0, y), (width, y)], fill=(r, g, b))
        
        # Центр обличчя
        face_center_x = width // 2
        face_center_y = height // 2 - 20
        face_width = 200
        face_height = 240
        
        # Обличчя (овал)
        face_left = face_center_x - face_width // 2
        face_top = face_center_y - face_height // 2
        face_right = face_center_x + face_width // 2
        face_bottom = face_center_y + face_height // 2
        
        # Волосся залежно від стилю
        if hair_style == 'undercut':
            # Undercut - короткі боки, довгий верх
            # Боки (короткі)
            draw.ellipse(
                [face_left - 20, face_top + 30, face_left + 30, face_top + 120],
                fill=(hair_color[0] - 20, hair_color[1] - 20, hair_color[2] - 20)
            )
            draw.ellipse(
                [face_right - 30, face_top + 30, face_right + 20, face_top + 120],
                fill=(hair_color[0] - 20, hair_color[1] - 20, hair_color[2] - 20)
            )
            # Верх (довгий, зачесаний назад)
            draw.ellipse(
                [face_center_x - face_width // 2 - 15, face_top - 50,
                 face_center_x + face_width // 2 + 15, face_top + 40],
                fill=hair_color
            )
        elif hair_style == 'cascade':
            # Каскад - довге хвилясте волосся
            hair_y = face_top - 60
            # Основний об'єм волосся
            draw.ellipse(
                [face_center_x - face_width // 2 - 20, hair_y,
                 face_center_x + face_width // 2 + 20, face_bottom + 50],
                fill=hair_color
            )
            # Хвилі
            for i in range(3):
                wave_y = face_center_y + i * 30
                draw.arc(
                    [face_center_x - 60, wave_y - 15, face_center_x + 60, wave_y + 15],
                    start=0, end=180, fill=(hair_color[0] - 30, hair_color[1] - 30, hair_color[2] - 30),
                    width=25
                )
        elif hair_style == 'fade':
            # Fade - плавний перехід
            # Низ (короткий)
            draw.ellipse(
                [face_left - 15, face_top + 50, face_left + 25, face_top + 140],
                fill=(hair_color[0] - 30, hair_color[1] - 30, hair_color[2] - 30)
            )
            draw.ellipse(
                [face_right - 25, face_top + 50, face_right + 15, face_top + 140],
                fill=(hair_color[0] - 30, hair_color[1] - 30, hair_color[2] - 30)
            )
            # Середня частина
            draw.ellipse(
                [face_left - 10, face_top + 20, face_left + 20, face_top + 100],
                fill=(hair_color[0] - 15, hair_color[1] - 15, hair_color[2] - 15)
            )
            draw.ellipse(
                [face_right - 20, face_top + 20, face_right + 10, face_top + 100],
                fill=(hair_color[0] - 15, hair_color[1] - 15, hair_color[2] - 15)
            )
            # Верх
            draw.ellipse(
                [face_center_x - face_width // 2 - 10, face_top - 30,
                 face_center_x + face_width // 2 + 10, face_top + 50],
                fill=hair_color
            )
        elif hair_style == 'bob':
            # Боб - коротка стрижка до плечей
            hair_y = face_top - 40
            # Волосся
            draw.ellipse(
                [face_center_x - face_width // 2 - 15, hair_y,
                 face_center_x + face_width // 2 + 15, face_center_y + 60],
                fill=hair_color
            )
            # Прямі кінчики
            draw.rectangle(
                [face_left - 20, face_center_y + 50, face_right + 20, face_center_y + 70],
                fill=hair_color
            )
        
        # Основний овал обличчя
        draw.ellipse(
            [face_left, face_top, face_right, face_bottom],
            fill=skin_color,
            outline=(skin_color[0] - 25, skin_color[1] - 25, skin_color[2] - 25),
            width=3
        )
        
        # Очі
        eye_y = face_center_y - 20
        eye_size = 30
        eye_spacing = 55
        
        # Ліве око
        draw.ellipse(
            [face_center_x - eye_spacing - eye_size, eye_y - eye_size // 2,
             face_center_x - eye_spacing + eye_size, eye_y + eye_size // 2],
            fill=(60, 40, 30)
        )
        draw.ellipse(
            [face_center_x - eye_spacing - eye_size // 2, eye_y - eye_size // 3,
             face_center_x - eye_spacing + eye_size // 2, eye_y + eye_size // 3],
            fill=(255, 255, 255)
        )
        draw.ellipse(
            [face_center_x - eye_spacing - eye_size // 3, eye_y - eye_size // 5,
             face_center_x - eye_spacing + eye_size // 3, eye_y + eye_size // 5],
            fill=(30, 20, 10)
        )
        
        # Праве око
        draw.ellipse(
            [face_center_x + eye_spacing - eye_size, eye_y - eye_size // 2,
             face_center_x + eye_spacing + eye_size, eye_y + eye_size // 2],
            fill=(60, 40, 30)
        )
        draw.ellipse(
            [face_center_x + eye_spacing - eye_size // 2, eye_y - eye_size // 3,
             face_center_x + eye_spacing + eye_size // 2, eye_y + eye_size // 3],
            fill=(255, 255, 255)
        )
        draw.ellipse(
            [face_center_x + eye_spacing - eye_size // 3, eye_y - eye_size // 5,
             face_center_x + eye_spacing + eye_size // 3, eye_y + eye_size // 5],
            fill=(30, 20, 10)
        )
        
        # Брови
        brow_y = eye_y - 30
        brow_width = 40
        draw.ellipse(
            [face_center_x - eye_spacing - brow_width // 2, brow_y - 4,
             face_center_x - eye_spacing + brow_width // 2, brow_y + 4],
            fill=hair_color
        )
        draw.ellipse(
            [face_center_x + eye_spacing - brow_width // 2, brow_y - 4,
             face_center_x + eye_spacing + brow_width // 2, brow_y + 4],
            fill=hair_color
        )
        
        # Ніс
        nose_y = face_center_y + 20
        nose_width = 20
        draw.ellipse(
            [face_center_x - nose_width // 2, nose_y - 20,
             face_center_x + nose_width // 2, nose_y + 20],
            fill=(skin_color[0] - 20, skin_color[1] - 20, skin_color[2] - 20),
            outline=(skin_color[0] - 30, skin_color[1] - 30, skin_color[2] - 30)
        )
        
        # Рот
        mouth_y = face_center_y + 70
        mouth_width = 50
        draw.ellipse(
            [face_center_x - mouth_width // 2, mouth_y - 10,
             face_center_x + mouth_width // 2, mouth_y + 10],
            fill=(220, 120, 120)
        )
        
        # Тіні на обличчі
        draw.ellipse(
            [face_left + 30, face_top + 30, face_right - 30, face_bottom - 30],
            fill=(skin_color[0] - 15, skin_color[1] - 15, skin_color[2] - 15),
            outline=None
        )
        
        # Легке розмиття
        img = img.filter(ImageFilter.GaussianBlur(radius=0.8))
        
        return img

    def create_realistic_avatar(self, skin_color, hair_color, bg_color, gender):
        """Створює реалістичний круглий аватар"""
        size = 80
        img = Image.new('RGB', (size, size), bg_color)
        draw = ImageDraw.Draw(img)
        
        center = size // 2
        radius = size // 2
        
        # Обличчя (круг)
        face_radius = radius - 5
        draw.ellipse(
            [center - face_radius, center - face_radius + 3,
             center + face_radius, center + face_radius + 3],
            fill=skin_color
        )
        
        # Волосся
        if gender == 'female':
            # Жіноче волосся - довше
            draw.ellipse(
                [center - face_radius - 2, center - face_radius - 8,
                 center + face_radius + 2, center + face_radius - 5],
                fill=hair_color
            )
        else:
            # Чоловіче волосся - коротше
            draw.ellipse(
                [center - face_radius - 2, center - face_radius - 12,
                 center + face_radius + 2, center - face_radius + 8],
                fill=hair_color
            )
        
        # Очі
        eye_size = 10
        eye_y = center - 3
        eye_spacing = 12
        
        # Ліве око
        draw.ellipse(
            [center - eye_spacing - eye_size // 2, eye_y - eye_size // 2,
             center - eye_spacing + eye_size // 2, eye_y + eye_size // 2],
            fill=(60, 40, 30)
        )
        draw.ellipse(
            [center - eye_spacing - eye_size // 3, eye_y - eye_size // 3,
             center - eye_spacing + eye_size // 3, eye_y + eye_size // 3],
            fill=(255, 255, 255)
        )
        
        # Праве око
        draw.ellipse(
            [center + eye_spacing - eye_size // 2, eye_y - eye_size // 2,
             center + eye_spacing + eye_size // 2, eye_y + eye_size // 2],
            fill=(60, 40, 30)
        )
        draw.ellipse(
            [center + eye_spacing - eye_size // 3, eye_y - eye_size // 3,
             center + eye_spacing + eye_size // 3, eye_y + eye_size // 3],
            fill=(255, 255, 255)
        )
        
        # Рот
        mouth_y = center + 12
        mouth_width = 14
        draw.ellipse(
            [center - mouth_width // 2, mouth_y - 3,
             center + mouth_width // 2, mouth_y + 3],
            fill=(200, 100, 100)
        )
        
        return img
