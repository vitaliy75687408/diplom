import os
import sys
import django
import io
from PIL import Image

# Setup Django
sys.path.append(os.getcwd())
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'styleai_project.settings')
django.setup()

from django.conf import settings
from google import genai
from google.genai import types

def test_gemini_inline_image():
    api_key = getattr(settings, 'GEMINI_API_KEY', None)
    if not api_key:
        print("Error: GEMINI_API_KEY not found in settings.")
        return

    client = genai.Client(api_key=api_key)
    img = Image.new('RGB', (100, 100), color=(73, 109, 137))
    
    print(f"Testing Gemini 2.0 Flash with key {api_key[:8]}...")
    try:
        response = client.models.generate_content(
            model='gemini-2.0-flash',
            contents=["Say 'API is working'", img]
        )
        print("Success!")
        print(f"Response: {response.text}")
    except Exception as e:
        print(f"Failed: {e}")

if __name__ == "__main__":
    test_gemini_inline_image()
