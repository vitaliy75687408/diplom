import urllib.request
from django.core.management.base import BaseCommand
from django.core.files.base import ContentFile
from hairstyles.models import Hairstyle
from styleai.views import STYLE_IMAGE_MAP, POPULAR_STYLE_DESCRIPTIONS

class Command(BaseCommand):
    help = 'Populates the Hairstyle database with default names, descriptions, and downloads images from STYLE_IMAGE_MAP.'

    def handle(self, *args, **kwargs):
        self.stdout.write("Starting to populate hairstyles in the database...")
        for name, url in STYLE_IMAGE_MAP.items():
            hs, created = Hairstyle.objects.get_or_create(name=name)
            
            desc = POPULAR_STYLE_DESCRIPTIONS.get(name, '')
            if desc and not hs.description:
                hs.description = desc
                self.stdout.write(f"Updated description for {name}")
            
            if url and not hs.image:
                try:
                    self.stdout.write(f"Downloading image for {name} from {url}...")
                    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
                    with urllib.request.urlopen(req) as response:
                        content = response.read()
                        filename = f"{name.replace(' ', '_').lower()}.jpg"
                        hs.image.save(filename, ContentFile(content), save=False)
                        self.stdout.write(f"Successfully downloaded image for {name}")
                except Exception as e:
                    self.stderr.write(f"Failed to download image for {name}: {e}")
            
            hs.save()
            
        self.stdout.write(self.style.SUCCESS("Successfully populated hairstyles database!"))
