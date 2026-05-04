import os
import sys
import django

# Setup Django environment
sys.path.append(r'c:\Users\User\Desktop\dyplom_2mis')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'styleai_project.settings')
django.setup()

from styleai.views import _detect_face_shape_mediapipe

test_image = r'c:\Users\User\Desktop\dyplom_2mis\media\user_photos\photo_2025-11-24_18-53-31.jpg'
if os.path.exists(test_image):
    result = _detect_face_shape_mediapipe(test_image)
    print(f"Detected face shape for {os.path.basename(test_image)}: {result}")
else:
    print(f"Test image not found: {test_image}")
