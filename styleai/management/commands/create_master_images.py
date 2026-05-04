from django.core.management.base import BaseCommand
from PIL import Image, ImageDraw, ImageFilter
import os
from django.conf import settings
import random


class Command(BaseCommand):
    help = 'Creates realistic placeholder images for masters'

    def handle(self, *args, **options):
        self.stdout.write('Creating master images...')
        
        media_dir = settings.MEDIA_ROOT
        os.makedirs(media_dir / 'masters', exist_ok=True)
        
        # Створюємо зображення для кожного майстра
        masters_data = [
            {
                'filename': 'oleksandr_koval.jpg',
                'skin_color': (180, 150, 120),
                'hair_color': (40, 30, 25),
                'bg_color': (240, 240, 245),
                'name': 'Олександр',
            },
            {
                'filename': 'mariia_petrenko.jpg',
                'skin_color': (255, 220, 200),
                'hair_color': (120, 80, 60),
                'bg_color': (250, 245, 255),
                'name': 'Марія',
            },
            {
                'filename': 'dmytro_shevchenko.jpg',
                'skin_color': (200, 170, 140),
                'hair_color': (50, 40, 35),
                'bg_color': (245, 245, 250),
                'name': 'Дмитро',
            },
        ]
        
        for master_data in masters_data:
            img = self.create_portrait_image(
                master_data['skin_color'],
                master_data['hair_color'],
                master_data['bg_color'],
                master_data['name']
            )
            
            img_path = media_dir / 'masters' / master_data['filename']
            img.save(img_path, 'JPEG', quality=95)
            self.stdout.write(f'Created: {img_path}')
        
        self.stdout.write(self.style.SUCCESS('Master images created successfully!'))

    def create_portrait_image(self, skin_color, hair_color, bg_color, name):
        """Створює портретне зображення"""
        width, height = 400, 500
        img = Image.new('RGB', (width, height), bg_color)
        draw = ImageDraw.Draw(img)
        
        # Центр обличчя
        face_center_x = width // 2
        face_center_y = height // 2 - 30
        face_width = 180
        face_height = 220
        
        # Фон - розмитий градієнт
        for y in range(height):
            ratio = y / height
            r = int(bg_color[0] * (1 - ratio) + bg_color[0] * 0.9 * ratio)
            g = int(bg_color[1] * (1 - ratio) + bg_color[1] * 0.9 * ratio)
            b = int(bg_color[2] * (1 - ratio) + bg_color[2] * 0.9 * ratio)
            draw.line([(0, y), (width, y)], fill=(r, g, b))
        
        # Волосся (верхня частина)
        hair_y = face_center_y - face_height // 2 - 40
        hair_points = [
            (face_center_x - face_width // 2 - 10, hair_y),
            (face_center_x - face_width // 2 - 5, hair_y - 30),
            (face_center_x + face_width // 2 + 5, hair_y - 30),
            (face_center_x + face_width // 2 + 10, hair_y),
        ]
        draw.ellipse(
            [face_center_x - face_width // 2 - 15, hair_y - 35,
             face_center_x + face_width // 2 + 15, hair_y + 20],
            fill=hair_color
        )
        
        # Обличчя (овал)
        face_left = face_center_x - face_width // 2
        face_top = face_center_y - face_height // 2
        face_right = face_center_x + face_width // 2
        face_bottom = face_center_y + face_height // 2
        
        # Основний овал обличчя
        draw.ellipse(
            [face_left, face_top, face_right, face_bottom],
            fill=skin_color,
            outline=(skin_color[0] - 20, skin_color[1] - 20, skin_color[2] - 20),
            width=2
        )
        
        # Очі
        eye_y = face_center_y - 30
        eye_size = 25
        eye_spacing = 50
        
        # Ліве око
        draw.ellipse(
            [face_center_x - eye_spacing - eye_size, eye_y - eye_size // 2,
             face_center_x - eye_spacing + eye_size, eye_y + eye_size // 2],
            fill=(60, 40, 30)
        )
        draw.ellipse(
            [face_center_x - eye_spacing - eye_size // 2, eye_y - eye_size // 4,
             face_center_x - eye_spacing + eye_size // 2, eye_y + eye_size // 4],
            fill=(255, 255, 255)
        )
        draw.ellipse(
            [face_center_x - eye_spacing - eye_size // 3, eye_y - eye_size // 6,
             face_center_x - eye_spacing + eye_size // 3, eye_y + eye_size // 6],
            fill=(30, 20, 10)
        )
        
        # Праве око
        draw.ellipse(
            [face_center_x + eye_spacing - eye_size, eye_y - eye_size // 2,
             face_center_x + eye_spacing + eye_size, eye_y + eye_size // 2],
            fill=(60, 40, 30)
        )
        draw.ellipse(
            [face_center_x + eye_spacing - eye_size // 2, eye_y - eye_size // 4,
             face_center_x + eye_spacing + eye_size // 2, eye_y + eye_size // 4],
            fill=(255, 255, 255)
        )
        draw.ellipse(
            [face_center_x + eye_spacing - eye_size // 3, eye_y - eye_size // 6,
             face_center_x + eye_spacing + eye_size // 3, eye_y + eye_size // 6],
            fill=(30, 20, 10)
        )
        
        # Ніс
        nose_y = face_center_y + 10
        nose_width = 15
        draw.ellipse(
            [face_center_x - nose_width // 2, nose_y - 15,
             face_center_x + nose_width // 2, nose_y + 15],
            fill=(skin_color[0] - 15, skin_color[1] - 15, skin_color[2] - 15),
            outline=(skin_color[0] - 25, skin_color[1] - 25, skin_color[2] - 25)
        )
        
        # Рот
        mouth_y = face_center_y + 50
        mouth_width = 40
        draw.ellipse(
            [face_center_x - mouth_width // 2, mouth_y - 8,
             face_center_x + mouth_width // 2, mouth_y + 8],
            fill=(200, 100, 100)
        )
        
        # Брови
        brow_y = eye_y - 25
        brow_width = 35
        draw.ellipse(
            [face_center_x - eye_spacing - brow_width // 2, brow_y - 3,
             face_center_x - eye_spacing + brow_width // 2, brow_y + 3],
            fill=hair_color
        )
        draw.ellipse(
            [face_center_x + eye_spacing - brow_width // 2, brow_y - 3,
             face_center_x + eye_spacing + brow_width // 2, brow_y + 3],
            fill=hair_color
        )
        
        # Тінь на обличчі
        draw.ellipse(
            [face_left + 20, face_top + 20, face_right - 20, face_bottom - 20],
            fill=(skin_color[0] - 10, skin_color[1] - 10, skin_color[2] - 10),
            outline=None
        )
        
        # Додаємо легке розмиття для більш реалістичного вигляду
        img = img.filter(ImageFilter.GaussianBlur(radius=0.5))
        
        return img
