import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bosco.settings')
django.setup()

from hairstyles.models import Hairstyle

names_to_delete = [
    'High Fade', 'Skin Fade', 'Textured Crop', 'Edgar Cut', 
    'Mod Cut', 'Brush Up Fade', 'Undercut', 'Faux Hawk', 
    'Crew Cut', 'Bob', 'Pixie Cut', 'Гарсон', 'Сесон', 'Їжачок'
]

deleted_count, _ = Hairstyle.objects.filter(name__in=names_to_delete).delete()
print(f"Deleted {deleted_count} hairstyles from database.")
