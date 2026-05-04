from django.core.management.base import BaseCommand
from core.models import Master
from django.core.files import File
import os
from django.conf import settings

class Command(BaseCommand):
    help = 'Populates the database with sample masters and images'

    def handle(self, *args, **kwargs):
        # Define sample data with corresponding local image filenames
        # Ensure these files exist in media/masters/ BEFORE running this
        masters_data = [
            {'name': 'Олександр Коваль', 'rating': 4.9, 'specialty': 'Барбер-стиліст', 'experience': '8 років досвіду', 'clients_count': 1240, 'tags': 'Класичні стрижки, Fade, Борода', 'image_file': 'master2.jpg'},
            {'name': 'Марія Петренко', 'rating': 5.0, 'specialty': 'Стиліст-колорист', 'experience': '12 років досвіду', 'clients_count': 2890, 'tags': 'Жіночі стрижки, Фарбування, Укладки', 'image_file': 'master3.jpg'},
            {'name': 'Ігор Сидоренко', 'rating': 4.8, 'specialty': 'Топ-стиліст', 'experience': '10 років досвіду', 'clients_count': 1850, 'tags': 'Креативні стрижки, Текстури, Unisex', 'image_file': 'master5.jpg'},
        ]

        # Path where we manually placed the downloaded images for seeding
        # For simplicity, we assume they are in MEDIA_ROOT/temp_seeds/ or just check media/masters directly
        # But to attach them properly to ImageField, we usually open them.
        
        # Let's assume we downloaded them to a temporary folder or the root for the script to find.
        # simpler: User will copy images to media/masters manually? No, I should automate.
        # I will attempt to open files from 'media/masters' assuming they were downloaded there, 
        # but ImageField might rename them if we just re-save. 
        
        # Better strategy: Check if Master exists, update image if missing.
        
        base_path = settings.MEDIA_ROOT / 'masters'

        for data in masters_data:
            defaults = {
                'rating': data['rating'],
                'experience': data['experience'],
                'tags': data['tags'],
                'specialty': data.get('specialty', ''),
                'clients_count': data.get('clients_count', 0),
            }
            master, created = Master.objects.get_or_create(
                name=data['name'],
                defaults=defaults
            )
            if not created:
                for k, v in defaults.items():
                    setattr(master, k, v)
                master.save()
            image_path = base_path / data['image_file']
            if os.path.exists(image_path):
                # We open it and save it. Django will handle duplicate naming by appending hash if needed, 
                # but we want to replace. For simplicity in this script, just save it.
                # To really replace without creating master1_new.jpg, we might need to delete old one first.
                # But simple re-save is enough for visual change.
                with open(image_path, 'rb') as f:
                    master.photo.save(data['image_file'], File(f), save=True)
                self.stdout.write(self.style.SUCCESS(f'Updated photo for: {master.name}'))
            
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created master: {master.name}'))
            else:
                self.stdout.write(f'Updated master: {master.name}')
