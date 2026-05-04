import os
import sys
import django
import urllib.request
from django.core.files.base import ContentFile

# Setup Django
sys.path.append(os.getcwd())
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'styleai_project.settings')
django.setup()

from hairstyles.models import Hairstyle

def download_shaggy_images():
    # Посилання на якісні фото Шеггі з Unsplash
    shaggy_urls = [
        "https://images.unsplash.com/photo-1518144591331-17a5dd71c477?w=800&q=80",
        "https://images.unsplash.com/photo-1595476108010-b4d1f10cf074?w=800&q=80",
    ]
    
    style_name = "Шеггі"
    try:
        hs = Hairstyle.objects.get(name=style_name)
        url = shaggy_urls[0]
        print(f"Downloading image for {style_name} from {url}...")
        
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as response:
            content = response.read()
            filename = "shaggy_new.jpg"
            hs.image.save(filename, ContentFile(content), save=True)
            print(f"Successfully updated image for {style_name}")
            
    except Hairstyle.DoesNotExist:
        print(f"Style {style_name} not found in database.")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    download_shaggy_images()
