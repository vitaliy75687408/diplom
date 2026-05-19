import urllib.request
from django.core.management.base import BaseCommand
from django.core.files.base import ContentFile
from hairstyles.models import Hairstyle
from styleai.views import STYLE_IMAGE_MAP, POPULAR_STYLE_DESCRIPTIONS, HTTP_STYLE_FALLBACK_MAP
import os
from django.conf import settings

class Command(BaseCommand):
    help = 'Populates the Hairstyle database with default names, descriptions, and copies images from STYLE_IMAGE_MAP.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Перезаписати фото навіть якщо воно вже є',
        )

    def handle(self, *args, **kwargs):
        force = kwargs.get('force', False)
        self.stdout.write("Starting to populate hairstyles in the database...")
        for name, url in STYLE_IMAGE_MAP.items():
            hs, created = Hairstyle.objects.get_or_create(name=name)
            
            desc = POPULAR_STYLE_DESCRIPTIONS.get(name, '')
            if desc and not hs.description:
                hs.description = desc
                self.stdout.write(f"Updated description for {name}")
            
            # Пропускаємо якщо фото вже є і не --force
            if hs.image and not force:
                hs.save()
                continue

            if url:
                try:
                    if url.startswith('http'):
                        req = urllib.request.Request(
                            url,
                            headers={'User-Agent': 'Mozilla/5.0 (compatible; StyleAI/1.0)'}
                        )
                        response = urllib.request.urlopen(req, timeout=15)
                        content = response.read()
                        filename = os.path.basename(url.split('?')[0]) or f"{name.replace(' ', '_')}.jpg"
                        if hs.image:
                            hs.image.delete(save=False)
                        hs.image.save(filename, ContentFile(content), save=False)
                        self.stdout.write(f"Downloaded remote image for {name}")
                    else:
                        # Локальний файл
                        media_path = os.path.join(settings.MEDIA_ROOT, url)
                        if os.path.exists(media_path):
                            with open(media_path, 'rb') as f:
                                content = f.read()
                            filename = os.path.basename(url)
                            if hs.image:
                                hs.image.delete(save=False)
                            hs.image.save(filename, ContentFile(content), save=False)
                            self.stdout.write(f"Copied local image for {name}")
                        else:
                            fallback_url = HTTP_STYLE_FALLBACK_MAP.get(name)
                            if fallback_url:
                                req = urllib.request.Request(
                                    fallback_url,
                                    headers={'User-Agent': 'Mozilla/5.0 (compatible; StyleAI/1.0)'}
                                )
                                response = urllib.request.urlopen(req, timeout=15)
                                content = response.read()
                                filename = os.path.basename(fallback_url.split('?')[0])
                                if hs.image:
                                    hs.image.delete(save=False)
                                hs.image.save(filename, ContentFile(content), save=False)
                                self.stdout.write(f"Used fallback for {name}")
                            else:
                                self.stderr.write(f"Image not found for {name}: {media_path}")
                except Exception as e:
                    self.stderr.write(f"Failed to save image for {name}: {e}")
            
            hs.save()
            
        self.stdout.write(self.style.SUCCESS("Successfully populated hairstyles database!"))