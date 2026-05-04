import urllib.request
import os
from django.core.management.base import BaseCommand
from django.conf import settings
from pathlib import Path


class Command(BaseCommand):
    help = 'Downloads and replaces the shaggy/bad hairstyle images with correct ones from Unsplash'

    REPLACEMENTS = {
        # filename: url
        'homepage_style_69.jpg': 'https://images.unsplash.com/photo-1518144591331-17a5dd71c477?w=800&q=80',
        # Also fix any other problematic files
        'homepage_style_67.jpg': 'https://images.unsplash.com/photo-1606756790138-26168bfaae9c?w=800&q=80',  # Їжачок
        'homepage_style_66.jpg': 'https://images.unsplash.com/photo-1620331311520-246422fd82f9?w=800&q=80',  # Сесон
        'homepage_style_65.jpg': 'https://images.unsplash.com/photo-1551150441-3f3828204ef0?w=800&q=80',    # Гарсон
        'homepage_style_64.jpg': 'https://images.unsplash.com/photo-1542596594-649edbc13630?w=800&q=80',   # Кучерявий Боб
        'homepage_style_63.jpg': 'https://images.unsplash.com/photo-1605980776566-0486c3ac7617?w=800&q=80', # Піксі
    }

    def handle(self, *args, **kwargs):
        hairstyles_dir = Path(settings.MEDIA_ROOT) / 'hairstyles'
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}

        for filename, url in self.REPLACEMENTS.items():
            dest_path = hairstyles_dir / filename
            self.stdout.write(f'Downloading {filename} from {url}...')
            try:
                req = urllib.request.Request(url, headers=headers)
                with urllib.request.urlopen(req, timeout=30) as response:
                    content = response.read()
                with open(dest_path, 'wb') as f:
                    f.write(content)
                self.stdout.write(self.style.SUCCESS(f'  ✓ Saved {filename} ({len(content)//1024} KB)'))
            except Exception as e:
                self.stderr.write(f'  ✗ Failed for {filename}: {e}')

        self.stdout.write(self.style.SUCCESS('\nDone! Refresh the homepage to see the updated images.'))
