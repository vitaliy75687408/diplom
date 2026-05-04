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

url = "https://images.unsplash.com/photo-1544005313-94ddf0286df2?w=1024&q=85"
res = requests.get(url)
img = Image.open(io.BytesIO(res.content))
img = img.resize((1024, 1024))
img = img.convert('RGBA')

# The original image to edit
img.save("test_opaque.png", format='PNG')

cut_y = int(1024 * 0.35)

# Mask: fully transparent where we want to edit, fully opaque where we want to keep
# According to OpenAI docs: The transparent areas of the mask indicate where the image should be edited
mask = Image.new('RGBA', (1024, 1024), (0, 0, 0, 255)) # Opaque black
for x in range(1024):
    for y in range(cut_y):
        mask.putpixel((x, y), (0, 0, 0, 0)) # Transparent top

mask.save("test_mask.png", format='PNG')

prompt = (
    "Act as an elite digital hairstylist and image editor. Modify the subject's hair to precisely match the target style: "
    "'Drop Fade'. Style specifications: Фейд із опущенням лінії по потилиці. "
    "Crucial Constraints: Restrict all structural and textural modifications strictly to the hair region. "
    "Preserve all inherent facial features, structure, skin texture, eyes, nose, and body elements identically to the original. "
    "Ensure the final result is indistinguishable from a genuine, high-fidelity portrait photograph with photorealistic hair."
)

print("Calling OpenAI with mask...")
with open("test_opaque.png", 'rb') as f_img, open("test_mask.png", 'rb') as f_mask:
    response = client.images.edit(
        model='dall-e-2',
        image=f_img,
        mask=f_mask,
        prompt=prompt,
        size="1024x1024",
        response_format="b64_json",
    )

image_b64 = response.data[0].b64_json
image_bytes = base64.b64decode(image_b64)
with open("out_mask.png", "wb") as f_out:
    f_out.write(image_bytes)

print("Saved out_mask.png successfully")
