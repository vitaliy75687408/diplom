from django.core.management.base import BaseCommand
from django.core.files import File
from pathlib import Path
from django.conf import settings
from hairstyles.models import Hairstyle
from masters.models import Master


class Command(BaseCommand):
    help = 'Updates existing records with images'

    def handle(self, *args, **options):
        self.stdout.write('Updating records with images...')
        
        media_dir = Path(settings.MEDIA_ROOT)
        
        # Оновлюємо зачіски
        hairstyle_images = {
            'Undercut': 'undercut.jpg',
            'Каскад': 'cascade.jpg',
            'Fade': 'fade.jpg',
            'Боб': 'bob.jpg',
        }
        
        for name, image_file in hairstyle_images.items():
            try:
                style = Hairstyle.objects.get(name=name)
                image_path = media_dir / 'hairstyles' / image_file
                if image_path.exists():
                    with open(image_path, 'rb') as f:
                        style.image.save(image_file, File(f), save=True)
                    self.stdout.write(f'Updated hairstyle: {name}')
            except Hairstyle.DoesNotExist:
                self.stdout.write(f'Hairstyle not found: {name}')
        
        # Оновлюємо майстрів
        master_images = {
            ('Олександр', 'Коваль'): 'oleksandr_koval.jpg',
            ('Марія', 'Петренко'): 'mariia_petrenko.jpg',
            ('Дмитро', 'Шевченко'): 'dmytro_shevchenko.jpg',
        }
        
        for (first_name, last_name), image_file in master_images.items():
            try:
                master = Master.objects.get(first_name=first_name, last_name=last_name)
                image_path = media_dir / 'masters' / image_file
                if image_path.exists():
                    with open(image_path, 'rb') as f:
                        master.photo.save(image_file, File(f), save=True)
                    self.stdout.write(f'Updated master: {master.full_name}')
            except Master.DoesNotExist:
                self.stdout.write(f'Master not found: {first_name} {last_name}')
        
        self.stdout.write(self.style.SUCCESS('Images updated successfully!'))
