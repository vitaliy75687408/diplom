import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'styleai_project.settings')
django.setup()

from styleai.models import UserPhoto

photos = UserPhoto.objects.order_by('-id')[:5]
print(f"{'ID':<5} | {'Gender':<10} | {'Shape':<15}")
print("-" * 35)
for p in photos:
    shape_name = p.face_shape.name if p.face_shape else "None"
    print(f"{p.id:<5} | {str(p.predicted_gender):<10} | {shape_name:<15}")
