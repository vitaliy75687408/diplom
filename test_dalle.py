import os
from PIL import Image
import tempfile
from openai import OpenAI
import base64
import requests
import io
import django
import sys

# setup django
sys.path.append('c:/Users/User/Desktop/dyplom_2mis')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'styleai_project.settings')
django.setup()

from django.conf import settings

api_key = (getattr(settings, 'OPENAI_API_KEY', None) or getattr(settings, 'OPENAI_IMAGE_API_KEY', None)).strip()
client = OpenAI(api_key=api_key)

# Download test user image
url = "https://images.unsplash.com/photo-1544005313-94ddf0286df2?w=1024&q=85" # just some face
res = requests.get(url)
img = Image.open(io.BytesIO(res.content))
img = img.resize((1024, 1024))
img = img.convert('RGBA')

# Cut top 35%
cut_y = int(1024 * 0.35)
new_img = Image.new('RGBA', (1024, 1024), (0, 0, 0, 0))
bottom_part = img.crop((0, cut_y, 1024, 1024))
new_img.paste(bottom_part, (0, cut_y))

# Save local transparent image for inspection
new_img.save("test_trans.png", format='PNG')

prompt = "Change only the person's hair to this style: Drop Fade. Details: Фейд із опущенням лінії по потилиці. Do not change the face, skin, eyes, nose, or body. Keep the same person. Realistic, natural hairstyle only."

print("Calling OpenAI...")
with open("test_trans.png", 'rb') as f:
    response = client.images.edit(
        model='dall-e-2',
        image=f,
        prompt=prompt,
        size="1024x1024",
        response_format="b64_json",
    )

image_b64 = response.data[0].b64_json
image_bytes = base64.b64decode(image_b64)
with open("out.png", "wb") as f_out:
    f_out.write(image_bytes)

print("Saved out.png successfully")
