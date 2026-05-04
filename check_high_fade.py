import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bosco.settings')
django.setup()

from hairstyles.models import Hairstyle

try:
    h = Hairstyle.objects.get(name='High Fade')
    print(f"Name: {h.name}")
    print(f"Image: {h.image}")
    if h.image:
        print(f"Image Path: {h.image.path}")
except Hairstyle.DoesNotExist:
    print("Hairstyle 'High Fade' not found.")
except Exception as e:
    print(f"Error: {e}")
