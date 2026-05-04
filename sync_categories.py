import os
import sys
import django

# Setup Django environment
sys.path.append(r'c:\Users\User\Desktop\dyplom_2mis')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'styleai_project.settings')
django.setup()

from hairstyles.models import Hairstyle
from styleai.constants import WOMEN_HAIRSTYLES, MEN_HAIRSTYLES

def sync_categories():
    women_names = [n.strip().lower() for n in WOMEN_HAIRSTYLES]
    men_names = [n.strip().lower() for n in MEN_HAIRSTYLES]
    
    styles = Hairstyle.objects.all()
    updated_count = 0
    for s in styles:
        name_lower = s.name.strip().lower()
        new_cat = None
        if name_lower in women_names:
            new_cat = 'women'
        elif name_lower in men_names:
            new_cat = 'men'
        
        if new_cat and s.category != new_cat:
            print(f"Updating {s.name!r}: {s.category} -> {new_cat}")
            s.category = new_cat
            s.save()
            updated_count += 1
            
    print(f"Finished! Updated {updated_count} styles.")

if __name__ == '__main__':
    sync_categories()
