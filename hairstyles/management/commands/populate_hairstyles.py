import urllib.request
from django.core.management.base import BaseCommand
from django.core.files.base import ContentFile
from hairstyles.models import Hairstyle
from styleai.views import STYLE_IMAGE_MAP, POPULAR_STYLE_DESCRIPTIONS
import os
from django.conf import settings

class Command(BaseCommand):
    help = 'Populates the Hairstyle database with default names, descriptions, and copies images from STYLE_IMAGE_MAP.'

    def handle(self, *args, **kwargs):
        self.stdout.write("Starting to populate hairstyles in the database...")
        for name, url in STYLE_IMAGE_MAP.items():
            hs, created = Hairstyle.objects.get_or_create(name=name)
            
            desc = POPULAR_STYLE_DESCRIPTIONS.get(name, '')
            if desc and not hs.description:
                hs.description = desc
                self.stdout.write(f"Updated description for {name}")
            
            if url and not hs.image:
                # Assume url is a relative path like 'hairstyles/filename.jpg'
                # Convert to absolute path in media directory
                media_path = os.path.join(settings.MEDIA_ROOT, url)
                if os.path.exists(media_path):
                    try:
                        with open(media_path, 'rb') as f:
                            content = f.read()
                            filename = os.path.basename(url)
                            hs.image.save(filename, ContentFile(content), save=False)
                            self.stdout.write(f"Successfully copied image for {name} from {media_path}")
                    except Exception as e:
                        self.stderr.write(f"Failed to copy image for {name}: {e}")
                else:
                    self.stderr.write(f"Image file not found for {name}: {media_path}")
            
            hs.save()
            
        self.stdout.write(self.style.SUCCESS("Successfully populated hairstyles database!"))
