"""
Сервісний шар проєкту StyleAI.
Тут можна виносити бізнес-логіку з views.
"""
# hairstyles/services.py
from django.conf import settings
from google import genai
from google.genai import types

def get_hairstyles_recommendation(image_file):
    """Використовує native Gemini для швидкого аналізу фото."""
    
    gemini_key = getattr(settings, 'GEMINI_API_KEY', None)
    if not gemini_key:
        return "Помилка: API ключ Gemini не налаштований у .env"

    try:
        raw_bytes = image_file.read()
        try: image_file.seek(0)
        except: pass
        
        client = genai.Client(api_key=gemini_key)
        mime_type = 'image/jpeg'
        if raw_bytes[:8] == b'\x89PNG\r\n\x1a\n':
            mime_type = 'image/png'
        elif raw_bytes[:3] == b'\xff\xd8\xff':
            mime_type = 'image/jpeg'
        response = client.models.generate_content(
            model='gemini-2.0-flash',
            contents=[
                "Яка форма обличчя на фото? Порекомендуй 3 стрижки та ключові слова для пошуку майстра. Поверни українською мовою.",
                types.Part.from_bytes(data=raw_bytes, mime_type=mime_type)
            ]
        )
        return response.text
    except Exception as e:
        return f"Помилка аналізу: {e}"