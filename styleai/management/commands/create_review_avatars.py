from django.core.management.base import BaseCommand
from PIL import Image, ImageDraw
import os
from django.conf import settings
from pathlib import Path


class Command(BaseCommand):
    help = 'Creates avatar images for reviews'

    def handle(self, *args, **options):
        self.stdout.write('Creating review avatars...')
        
        static_dir = Path(settings.STATICFILES_DIRS[0]) if settings.STATICFILES_DIRS else Path(settings.STATIC_ROOT)
        images_dir = static_dir / 'images'
        os.makedirs(images_dir, exist_ok=True)
        
        # Створюємо аватари для різних людей
        avatars = [
            {
                'filename': 'avatar_man1.png',
                'skin_color': (200, 170, 140),
                'hair_color': (50, 40, 35),
                'bg_color': (100, 150, 200),
            },
            {
                'filename': 'avatar_woman1.png',
                'skin_color': (255, 220, 200),
                'hair_color': (120, 80, 60),
                'bg_color': (200, 150, 200),
            },
            {
                'filename': 'avatar_man2.png',
                'skin_color': (180, 150, 120),
                'hair_color': (40, 30, 25),
                'bg_color': (150, 180, 220),
            },
        ]
        
        for avatar_data in avatars:
            img = self.create_avatar(
                avatar_data['skin_color'],
                avatar_data['hair_color'],
                avatar_data['bg_color']
            )
            
            img_path = images_dir / avatar_data['filename']
            img.save(img_path, 'PNG')
            self.stdout.write(f'Created: {img_path}')
        
        self.stdout.write(self.style.SUCCESS('Review avatars created successfully!'))

    def create_avatar(self, skin_color, hair_color, bg_color):
        """Створює круглий аватар"""
        size = 80
        img = Image.new('RGB', (size, size), bg_color)
        draw = ImageDraw.Draw(img)
        
        # Фон - градієнт
        center = size // 2
        radius = size // 2
        
        # Обличчя (круг)
        face_radius = radius - 8
        draw.ellipse(
            [center - face_radius, center - face_radius + 5,
             center + face_radius, center + face_radius + 5],
            fill=skin_color
        )
        
        # Волосся (верхня частина)
        hair_y = center - face_radius + 5
        draw.ellipse(
            [center - face_radius - 3, hair_y - 15,
             center + face_radius + 3, hair_y + 5],
            fill=hair_color
        )
        
        # Очі
        eye_size = 8
        eye_y = center - 5
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
        mouth_y = center + 10
        mouth_width = 12
        draw.ellipse(
            [center - mouth_width // 2, mouth_y - 3,
             center + mouth_width // 2, mouth_y + 3],
            fill=(200, 100, 100)
        )
        
        return img
