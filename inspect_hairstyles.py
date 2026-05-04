import os
import sys
import django

# Setup Django environment
sys.path.append(r'c:\Users\User\Desktop\dyplom_2mis')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'styleai_project.settings')
django.setup()

from hairstyles.models import Hairstyle

styles = Hairstyle.objects.all()
print(f"Total hairstyles: {styles.count()}")
for s in styles:
    print(f"Name: {s.name!r}, Category: {s.category!r}")
