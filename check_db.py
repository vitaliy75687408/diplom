import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bosco.settings')
django.setup()

from hairstyles.models import Hairstyle, FaceShape

def check_data():
    styles = Hairstyle.objects.all()
    print(f"Total hairstyles: {styles.count()}")
    for s in styles:
        print(f" - {s.name} (ID: {s.id})")
        
    shapes = FaceShape.objects.all()
    print(f"\nTotal shapes: {shapes.count()}")
    for sh in shapes:
        suitable = sh.suitable_hairstyles.all()
        print(f" - {sh.name}: {', '.join([s.name for s in suitable])}")

if __name__ == "__main__":
    check_data()
