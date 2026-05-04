import os
from pathlib import Path
import django
from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'styleai_project.settings')
django.setup()

def check():
    path = Path(settings.MEDIA_ROOT) / "hairstyles" / "homepage_style_66.jpg"
    print(f"Checking path: {path}")
    print(f"Exists: {path.exists()}")
    if not path.exists():
        # Try to find it
        print("Searching for the file...")
        for root, dirs, files in os.walk(settings.BASE_DIR):
            if "homepage_style_66.jpg" in files:
                print(f"FOUND AT: {os.path.join(root, 'homepage_style_66.jpg')}")

if __name__ == "__main__":
    check()
