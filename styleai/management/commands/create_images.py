from django.core.management.base import BaseCommand
from PIL import Image, ImageDraw, ImageFont
import os
from django.conf import settings

class Command(BaseCommand):
    help = 'Creates placeholder images for the website'

    def handle(self, *args, **options):
        self.stdout.write('Creating placeholder images...')
        
        # Створюємо директорії
        media_dir = settings.MEDIA_ROOT
        os.makedirs(media_dir / 'hairstyles', exist_ok=True)
        os.makedirs(media_dir / 'masters', exist_ok=True)
        os.makedirs(media_dir / 'user_photos', exist_ok=True)
        
        # Створюємо зображення для зачісок
        hairstyle_images = {
            'undercut': {
                'colors': [(30, 30, 30), (50, 50, 50)],
                'text': 'Undercut',
                'filename': 'undercut.jpg'
            },
            'cascade': {
                'colors': [(255, 220, 177), (255, 200, 150)],
                'text': 'Каскад',
                'filename': 'cascade.jpg'
            },
            'fade': {
                'colors': [(40, 40, 40), (60, 60, 60)],
                'text': 'Fade',
                'filename': 'fade.jpg'
            },
            'bob': {
                'colors': [(101, 67, 33), (120, 80, 40)],
                'text': 'Боб',
                'filename': 'bob.jpg'
            },
        }
        
        for key, data in hairstyle_images.items():
            img = self.create_gradient_image(400, 300, data['colors'])
            draw = ImageDraw.Draw(img)
            
            # Додаємо текст
            try:
                font = ImageFont.truetype("arial.ttf", 40)
            except:
                font = ImageFont.load_default()
            
            bbox = draw.textbbox((0, 0), data['text'], font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            position = ((400 - text_width) // 2, (300 - text_height) // 2)
            
            draw.text(position, data['text'], fill=(255, 255, 255), font=font)
            
            img_path = media_dir / 'hairstyles' / data['filename']
            img.save(img_path, 'JPEG', quality=90)
            self.stdout.write(f'Created: {img_path}')
        
        # Створюємо зображення для майстрів
        master_images = {
            'oleksandr': {
                'colors': [(60, 60, 70), (80, 80, 90)],
                'text': 'Олександр\nКоваль',
                'filename': 'oleksandr_koval.jpg'
            },
            'mariia': {
                'colors': [(200, 180, 160), (220, 200, 180)],
                'text': 'Марія\nПетренко',
                'filename': 'mariia_petrenko.jpg'
            },
            'dmytro': {
                'colors': [(70, 70, 80), (90, 90, 100)],
                'text': 'Дмитро\nШевченко',
                'filename': 'dmytro_shevchenko.jpg'
            },
        }
        
        for key, data in master_images.items():
            img = self.create_gradient_image(400, 500, data['colors'])
            draw = ImageDraw.Draw(img)
            
            try:
                font = ImageFont.truetype("arial.ttf", 35)
            except:
                font = ImageFont.load_default()
            
            lines = data['text'].split('\n')
            total_height = len(lines) * 50
            start_y = (500 - total_height) // 2
            
            for i, line in enumerate(lines):
                bbox = draw.textbbox((0, 0), line, font=font)
                text_width = bbox[2] - bbox[0]
                position = ((400 - text_width) // 2, start_y + i * 50)
                draw.text(position, line, fill=(255, 255, 255), font=font)
            
            img_path = media_dir / 'masters' / data['filename']
            img.save(img_path, 'JPEG', quality=90)
            self.stdout.write(f'Created: {img_path}')
        
        # Hero зображення
        hero_img = self.create_gradient_image(600, 800, [(230, 230, 250), (200, 180, 220)])
        draw = ImageDraw.Draw(hero_img)
        
        try:
            font = ImageFont.truetype("arial.ttf", 50)
        except:
            font = ImageFont.load_default()
        
        text = "Перукар\nта\nКлієнт"
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        position = ((600 - text_width) // 2, (800 - text_height) // 2)
        draw.text(position, text, fill=(100, 100, 120), font=font)
        
        hero_path = settings.STATICFILES_DIRS[0] / 'images' / 'hero-image.jpg'
        os.makedirs(hero_path.parent, exist_ok=True)
        hero_img.save(hero_path, 'JPEG', quality=90)
        self.stdout.write(f'Created: {hero_path}')
        
        self.stdout.write(self.style.SUCCESS('All images created successfully!'))

    def create_gradient_image(self, width, height, colors):
        """Створює зображення з градієнтом"""
        img = Image.new('RGB', (width, height))
        draw = ImageDraw.Draw(img)
        
        if len(colors) == 2:
            # Створюємо градієнт
            for y in range(height):
                ratio = y / height
                r = int(colors[0][0] * (1 - ratio) + colors[1][0] * ratio)
                g = int(colors[0][1] * (1 - ratio) + colors[1][1] * ratio)
                b = int(colors[0][2] * (1 - ratio) + colors[1][2] * ratio)
                draw.line([(0, y), (width, y)], fill=(r, g, b))
        else:
            img.paste(colors[0], [0, 0, width, height])
        
        return img
