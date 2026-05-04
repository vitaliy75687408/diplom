import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'styleai_project.settings')
django.setup()

from hairstyles.models import Hairstyle
from styleai.constants import POPULAR_HAIRSTYLE_NAMES

for name in POPULAR_HAIRSTYLE_NAMES:
    s = Hairstyle.objects.filter(name=name).first()
    print(f"{name}: {s.id if s else 'NOT FOUND'}")
