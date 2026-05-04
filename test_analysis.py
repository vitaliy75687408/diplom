import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'styleai_project.settings')
django.setup()

from styleai.views import analyze_face_shape
from django.conf import settings

# Test image path
img_path = 'test_user_photo.jpg'
if not os.path.exists(img_path):
    # Create a dummy image if not exists
    from PIL import Image
    dummy = Image.new('RGB', (100, 100), color = 'red')
    dummy.save(img_path)

print(f"API Key: {settings.OPENAI_API_KEY[:10]}...")
shape, gender = analyze_face_shape(img_path)
print(f"Result: Shape={shape}, Gender={gender}")
