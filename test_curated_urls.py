import os
import django
from pathlib import Path

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'styleai_project.settings')
django.setup()

from hairstyles.models import Hairstyle
from styleai.views import _homepage_generated_style_url
from django.conf import settings

def test_urls():
    print(f"MEDIA_ROOT: {settings.MEDIA_ROOT}")
    styles = Hairstyle.objects.all()
    print(f"Checking {styles.count()} styles...")
    
    found = 0
    for s in styles:
        url = _homepage_generated_style_url(s)
        if url:
            print(f" [+] {s.name}: {url}")
            found += 1
        else:
            # Debug why it failed
            from styleai.constants import POPULAR_HAIRSTYLE_NAMES
            try:
                idx = POPULAR_HAIRSTYLE_NAMES.index(s.name)
                old_id = None
                if idx < 21: old_id = 42 + idx
                elif idx == 21: old_id = 63
                elif idx == 22: old_id = 64
                elif idx == 23: old_id = 65
                elif idx == 24: old_id = 66
                elif idx == 25: old_id = 67
                
                if old_id:
                    path = Path(settings.MEDIA_ROOT) / "hairstyles" / f"homepage_style_{old_id}.jpg"
                    print(f" [-] {s.name}: Not found at {path}")
                else:
                    print(f" [-] {s.name}: No old_id for index {idx}")
            except ValueError:
                print(f" [-] {s.name}: Name not in POPULAR_HAIRSTYLE_NAMES")
                
    print(f"\nSummary: Found {found} / {styles.count()} curated images.")

if __name__ == "__main__":
    test_urls()
