import os
import sys
import django

# Setup Django environment
sys.path.append(r'c:\Users\User\Desktop\dyplom_2mis')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'styleai_project.settings')
django.setup()

from django.conf import settings

api_key = (getattr(settings, 'OPENAI_IMAGE_API_KEY', None) or getattr(settings, 'OPENAI_API_KEY', None) or '').strip()
print(f"API Key start: {api_key[:10]}...")
print(f"Is OpenRouter: {api_key.startswith('sk-or-v1-')}")
print(f"Model used: {getattr(settings, 'OPENAI_IMAGE_EDIT_MODEL', 'dall-e-2')}")
