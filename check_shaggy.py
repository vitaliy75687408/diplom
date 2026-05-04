import os
import sys
import django

# Setup Django
sys.path.append(os.getcwd())
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'styleai_project.settings')
django.setup()

from hairstyles.models import Hairstyle

styles = Hairstyle.objects.filter(name__icontains='шеггі')
print(f"Found {styles.count()} styles matching 'шеггі':")
for s in styles:
    print(f"ID: {s.id}, Name: {s.name}, Image: {s.image.name if s.image else 'None'}")
