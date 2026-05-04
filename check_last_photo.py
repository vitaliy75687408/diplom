import os
import sys
import django

# Setup Django environment
sys.path.append(r'c:\Users\User\Desktop\dyplom_2mis')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'styleai_project.settings')
django.setup()

from styleai.models import UserPhoto

last_photo = UserPhoto.objects.all().order_by('-analyzed_at').first()
if last_photo:
    print(f"Last photo ID: {last_photo.id}")
    print(f"Predicted Gender: {last_photo.predicted_gender!r}")
    print(f"Face Shape: {last_photo.face_shape}")
    print(f"Recommendations count: {last_photo.recommendations.count()}")
    for rec in last_photo.recommendations.all():
        print(f"  - {rec.hairstyle.name} (Confidence: {rec.confidence_score})")
else:
    print("No photos found.")
