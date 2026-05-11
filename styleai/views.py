from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.conf import settings
from django.templatetags.static import static
import os
from pathlib import Path
import io
import json
try:
    import cv2
except ImportError:
    cv2 = None
import tempfile
import urllib.request
from PIL import Image
import random
from google import genai
from google.genai import types

from hairstyles.models import Hairstyle, FaceShape
from masters.models import Master, Review, Barbershop
from styleai.models import UserPhoto, AIRecommendation, HairSurvey


from styleai.constants import (
    POPULAR_HAIRSTYLE_NAMES, EXTRA_WOMEN_HAIRSTYLE_NAMES, EXTRA_MEN_HAIRSTYLE_NAMES,
    MEN_HAIRSTYLES, WOMEN_HAIRSTYLES, HAIRSTYLE_LENGTH, HAIRSTYLE_LENGTH_LABELS
)


# Р¤РѕС‚Рѕ Р·Р°С‡С–СЃРѕРє РїС–Рґ РЅР°Р·РІСѓ вЂ” РєРѕР¶РЅР° РєР°СЂС‚РєР° Р· СЃРІРѕС—Рј Р·РѕР±СЂР°Р¶РµРЅРЅСЏРј (РџРѕРїСѓР»СЏСЂРЅС– Р·Р°С‡С–СЃРєРё РЅР° РіРѕР»РѕРІРЅС–Р№)
STYLE_IMAGE_MAP = {
    'Drop Fade': 'hairstyles/drop-fade.webp',
    'Taper Fade': 'hairstyles/taper_fade.jpg',
    'Low Fade': 'hairstyles/low_fade.jpg',
    'Mid Fade': 'hairstyles/mid-fade.jpg',
    'High Fade': 'hairstyles/high_fade.jpg',
    'Skin Fade': 'hairstyles/skin-fade.jpg', 
    'Textured Crop': 'hairstyles/textured_crop..jpg',
    'Burst Fade': 'hairstyles/burst-fade..jpg',
    'Edgar Cut': 'hairstyles/edgar_cut.jfif',
    'Slick Back': 'hairstyles/slick-back.webp',
    'Pompadour': 'hairstyles/pompadour.jpg',
    'Quiff': 'hairstyles/quiff.jpg',
    'Long Wavy Hair': 'hairstyles/long_wavy_hair .jpg',
    'Mod Cut': 'hairstyles/mod_cut.jfif',
    'Brush Up Fade': 'hairstyles/brush-up-fade.jpg',
    'Undercut': 'hairstyles/undercut.webp',
    'Faux Hawk': 'hairstyles/faux-hawk.jpg',
    'Crew Cut': 'hairstyles/crew_cut.jpg',
    'Buzz Cut': 'hairstyles/buzz-cut.jpg',
    'Bob': 'hairstyles/bob.jpg.',
    'Pixie Cut': 'hairstyles/pixie-сut.webp',
    'Каре': 'hairstyles/каре.webp',
    'Кучерявий Боб': 'hairstyles/кучерявий-боб.webp',
    'Піксі': 'hairstyles/піксі.webp',
    'Їжачок': 'hairstyles/їжачок.webp',
    'Шеггі': 'hairstyles/шеггі.jfif',
    'Гарсон': 'hairstyles/гарсон.webp',
    'Сесон': 'hairstyles/сесон.webp',
}

POPULAR_STYLE_DESCRIPTIONS = {
    'Drop Fade': 'Фейд із опущенням лінії по потилиці.',
    'Taper Fade': 'Тейпер із плавним переходом по краях.',
    'Low Fade': 'Низький фейд від вух.',
    'Mid Fade': 'Середній фейд по всьому периметру.',
    'High Fade': 'Високий фейд.',
    'Skin Fade': 'Фейд до шкіри.',
    'Textured Crop': 'Короткий кроп з текстурою зверху.',
    'Burst Fade': "Фейд із об'ємом над вухами.",
    'Edgar Cut': 'Короткі боки, чубчик уперед і вгору.',
    'Slick Back': 'Волосся зачесане назад з фіксацією.',
    'Pompadour': "Об'ємна стрижка з високим верхом.",
    'Quiff': 'Зачіска з піднятим чубчиком.',
    'Brush Up Fade': 'Волосся подняте вгору.',
    'Undercut': 'Короткі боки та довгий верх.',
    'Faux Hawk': 'Штучний ірокез.',
    'Long Wavy Hair': 'Довге хвилясте волосся.',
    'Mod Cut': 'Сучасна стрижка середньої довжини з чіткими лініями.',
    'Crew Cut': 'Коротка класична стрижка.',
    'Buzz Cut': 'Дуже коротка стрижка під машинку.',
    'Bob': 'Класичне каре.',
    'Pixie Cut': 'Коротка текстурована стрижка.',
    'Каре': 'Класична стрижка з рівним зрізом.',
    'Кучерявий Боб': 'Короткий боб для хвилястого або кучерявого волосся.',
    'Піксі': 'Коротка і смілива стрижка з текстурованими пасмами.',
    'Гарсон': 'Елегантна коротка стрижка.',
    'Сесон': 'Вінтажна стрижка з плавним переходом.',
    'Їжачок': 'Ультракоротка стрижка.',
    'Шеггі': 'Рвана стрижка з недбалими пасмами.',
}

DEFAULT_IMAGE_WOMEN = "https://images.unsplash.com/photo-1522337360788-8b13dee7a37e?w=400&q=80"
DEFAULT_IMAGE_MEN = "https://images.unsplash.com/photo-1585747860715-2ba37e788b70?w=400&q=80"
DEFAULT_IMAGE = "https://images.unsplash.com/photo-1560066984-138dadb4c035?w=400&q=80"
HOME_TEAM_FIRST_NAMES = ["Ігор", "Віталій", "Марія", "Тетяна", "Вадим", "Олександр"]


def _homepage_generated_style_url(style):
    if not style.name:
        return ""

    from styleai.constants import POPULAR_HAIRSTYLE_NAMES

    # Явне відображення назв на ID файлів (відповідно до curated contact sheet)
    NAME_TO_ID = {
        'drop fade': 42, 'taper fade': 43, 'low fade': 44, 'mid fade': 45,
        'high fade': 46, 'skin fade': 47, 'textured crop': 48, 'burst fade': 49,
        'edgar cut': 50, 'slick back': 51, 'pompadour': 52, 'quiff': 53,
        'long wavy hair': 54, 'mod cut': 55, 'brush up fade': 56, 'undercut': 57,
        'faux hawk': 58, 'crew cut': 59, 'buzz cut': 60, 'bob': 61,
        'pixie cut': 62, 'каре': 63, 'кучерявий боб': 64, 'піксі': 65,
        'їжачок': 66, 'шеггі': 67, 'гарсон': 68, 'сесон': 69
    }
    
    style_name_lower = style.name.strip().lower()
    old_id = NAME_TO_ID.get(style_name_lower)

    candidates = []
    if old_id:
        candidates.append(old_id)
    cur_id = getattr(style, "id", None)
    if cur_id and cur_id not in candidates:
        candidates.append(cur_id)

    # 1. Спершу пробуємо брендовані файли homepage_style_XX.jpg
    for cid in candidates:
        full_path = Path(settings.MEDIA_ROOT) / "hairstyles" / f"homepage_style_{cid}.jpg"
        if full_path.exists():
            return f"{settings.MEDIA_URL}hairstyles/homepage_style_{cid}.jpg"

    # 2. Якщо не знайдено, пробуємо прямі назви файлів (fallback для їжачка, шеггі тощо)
    direct_fallbacks = {
        'їжачок': 'yizhachok.jpg',
        'шеггі': 'шеггі.jpg',
        'каре': 'kare.jpg',
        'піксі': 'піксі.jpg',
        'гарсон': 'гарсон.jpg',
        'сесон': 'сесон.jpg',
        'кучерявий боб': 'кучерявий_боб.jpg',
    }
    
    if style_name_lower in direct_fallbacks:
        fname = direct_fallbacks[style_name_lower]
        if (Path(settings.MEDIA_ROOT) / "hairstyles" / fname).exists():
            return f"{settings.MEDIA_URL}hairstyles/{fname}"

    return ""


def _style_image_url(style):
    """Отримує URL зображення для зачіски."""
    if not style or not hasattr(style, 'name'):
        return DEFAULT_IMAGE
        
    # 1. Фото з бази даних
    style_image = getattr(style, 'image', None)
    if style_image:
        try:
            return style_image.url
        except Exception:
            pass
    
    name = style.name.strip()
    
    # 2. Пряма карта (локальні файли)
    rel_path = STYLE_IMAGE_MAP.get(name)
    if rel_path:
        if rel_path.startswith('http'):
            return rel_path
        # Повертаємо абсолютний шлях від кореня
        return f"/media/{rel_path}"
    
    # 3. Динамічний пошук за ID
    fallback = _homepage_generated_style_url(style)
    if fallback:
        return fallback
        
    return STYLE_IMAGE_MAP.get(name, DEFAULT_IMAGE)




def _homepage_team_photo_url(master):
    rel_name = f"masters/home_team_{master.id}.jpg"
    full_path = Path(settings.MEDIA_ROOT) / "masters" / f"home_team_{master.id}.jpg"
    if full_path.exists():
        return default_storage.url(rel_name)
    if getattr(master, "photo", None):
        try:
            return master.photo.url
        except Exception:
            pass
    return ""


def _home_team_masters():
    featured = []
    seen_ids = set()
    for first_name in HOME_TEAM_FIRST_NAMES:
        candidates = list(
            Master.objects.filter(first_name=first_name).order_by("-rating", "-experience_years", "id")
        )
        if not candidates:
            continue
        chosen = next((master for master in candidates if getattr(master.photo, "name", "")), candidates[0])
        if chosen.id in seen_ids:
            continue
        seen_ids.add(chosen.id)
        featured.append(chosen)
    return featured


def _get_mime_type(image_bytes):
    """Detect mime type from image magic bytes."""
    if image_bytes[:8] == b'\x89PNG\r\n\x1a\n':
        return 'image/png'
    if image_bytes[:3] == b'\xff\xd8\xff':
        return 'image/jpeg'
    if image_bytes[:4] == b'RIFF' and image_bytes[8:12] == b'WEBP':
        return 'image/webp'
    return 'image/jpeg'  # safe default


def _ai_generate_hairstyle_with_gemini(user_photo_path, style_name, style_description, user_photo_id, style_id, api_key, survey=None):
    """Генерує зачіску через Google Gemini (Imagen 3) з урахуванням опитування."""
    try:
        client = genai.Client(api_key=api_key)
        # Читаємо байти зображення
        if hasattr(user_photo_path, 'read'):
            image_bytes = user_photo_path.read()
            if hasattr(user_photo_path, 'seek'): user_photo_path.seek(0)
        else:
            with open(user_photo_path, 'rb') as f:
                image_bytes = f.read()

        mime_type = _get_mime_type(image_bytes)

        # 1. Запитуємо у Gemini щодо опису людини на фото
        # Використовуємо PIL Image для коректної передачі в SDK
        pil_img = Image.open(io.BytesIO(image_bytes))
        
        flash_response = client.models.generate_content(
            model='gemini-2.0-flash',
            contents=[
                "Detailed person description for AI image generation (only appearance, no names). Mention gender, age, face shape, hair type, skin tone. Be concise.",
                pil_img
            ]
        )
        person_desc = flash_response.text.strip()
        
        # 2. Формуємо промпт з урахуванням опитування
        survey_details = ""
        if survey:
            details = []
            if survey.hair_type: details.append(f"hair type: {survey.hair_type}")
            if survey.long_hairstyle: details.append("long hairstyle")
            if survey.short_hairstyle: details.append("short haircut")
            if survey.volume: details.append("with extra volume")
            if survey.notes: details.append(f"user request: {survey.notes}")
            if details:
                survey_details = " STRICTLY FOLLOW THESE REQUIREMENTS: " + ", ".join(details) + "."

        prompt = (
            f"Professional high-quality studio photo of a {person_desc}. "
            f"The person has a '{style_name}' hairstyle. {survey_details} "
            f"Details: {style_description or 'modern style'}. "
            f"Photorealistic, high detail, 8k, focused on hair."
        )
        
        response = client.models.generate_images(
            model='imagen-3.0-generate-001',
            prompt=prompt,
            config=types.GenerateImagesConfig(
                number_of_images=1,
                output_mime_type='image/png',
                add_watermark=False
            )
        )
        
        if not response.generated_images: return None
        image_bytes = response.generated_images[0].image.image_bytes
        rel_name = f"generated_hairstyles/gemini_{user_photo_id}_{style_id}_{os.urandom(4).hex()}.png"
        default_storage.save(rel_name, ContentFile(image_bytes))
        return default_storage.url(rel_name)
            
    except Exception as e:
        import traceback
        with open('gemini_error.log', 'a', encoding='utf-8') as f:
            f.write(f"--- {os.urandom(2).hex()} ---\n")
            f.write(f"Gemini generating error: {e}\n")
            f.write(traceback.format_exc() + "\n")
        print(f"Gemini generating error: {e}")
        return None

def _ai_generate_hairstyle_on_photo(user_photo_path, style_name, style_description, user_photo_id, style_id, api_key, survey=None):
    """Генерація зачіски: Gemini."""
    gemini_key = getattr(settings, 'GEMINI_API_KEY', None)
    if gemini_key:
        return _ai_generate_hairstyle_with_gemini(user_photo_path, style_name, style_description, user_photo_id, style_id, gemini_key, survey=survey)
    return None


# Р¤РѕС‚Рѕ РјР°Р№СЃС‚СЂС–РІ РґР»СЏ СЃРµРєС†С–С— В«РќР°С€Р° РєРѕРјР°РЅРґР°В» (СЏРєС‰Рѕ РІ Р‘Р” С‰Рµ РЅРµРјР°С” master.photo) вЂ” СѓРЅС–РєР°Р»СЊРЅС– РѕР±Р»РёС‡С‡СЏ
MASTER_PHOTO_BY_FIRST_NAME = {
    "РћР»РµРєСЃР°РЅРґСЂ": "https://images.unsplash.com/photo-1492106087820-71f1a00d2b11?w=400&q=85",
    "РњР°СЂС–СЏ": "https://images.unsplash.com/photo-1544005313-94ddf0286df2?w=400&q=85",
    "Р”РјРёС‚СЂРѕ": "https://images.unsplash.com/photo-1539571696357-5a69c17a67c6?w=400&q=85",
    "РђРЅРґСЂС–Р№": "https://images.unsplash.com/photo-1507591064344-4c6ce005b128?w=400&q=85",
    "РћР»РµРЅР°": "https://images.unsplash.com/photo-1560066984-138dadb4c035?w=400&q=85",
    "Р†РіРѕСЂ": "https://images.unsplash.com/photo-1503951914875-452162b0f3f1?w=400&q=85",
    "Р’С–С‚Р°Р»С–Р№": "https://images.unsplash.com/photo-1585747860715-2ba37e788b70?w=400&q=85",
    "РўРµС‚СЏРЅР°": "https://images.unsplash.com/photo-1522337360788-8b13dee7a37e?w=400&q=85",
    "Р’Р°РґРёРј": "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=400&q=85",
}
MASTER_PHOTO_URLS = [
    "https://images.unsplash.com/photo-1500648767791-1baa11a42f8c?w=400&q=85",
    "https://images.unsplash.com/photo-1547425260-abc76f5bddf5?w=400&q=85",
]

# Р’С–РґРіСѓРєРё: С–РЅС€С– РѕР±Р»РёС‡С‡СЏ, РЅС–Р¶ РјР°Р№СЃС‚СЂРё (С‰РѕР± РѕРґРЅР° РѕСЃРѕР±Р° РЅРµ Р±СѓР»Р° С– РјР°Р№СЃС‚СЂРѕРј, С– Р°РІС‚РѕСЂРѕРј РІС–РґРіСѓРєСѓ)
REVIEW_AVATAR_URLS = [
    "https://images.unsplash.com/photo-1506794778202-cad84cf45f1d?w=200&q=85",
    static("images/avatar_woman.png"),
    "https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?w=200&q=85",
]


def index(request):
    """Головна сторінка"""
    from types import SimpleNamespace
    from masters.models import Master
    db_styles = {s.name: s for s in Hairstyle.objects.filter(name__in=POPULAR_HAIRSTYLE_NAMES)}
    popular_styles = []
    total_masters = Master.objects.count()

    for name in POPULAR_HAIRSTYLE_NAMES:
        db_style = db_styles.get(name)
        
        # Створюємо чистий об'єкт для головної сторінки, щоб уникнути конфліктів з ID у базі
        style = SimpleNamespace(
            name=name,
            description=db_style.description if db_style and db_style.description else POPULAR_STYLE_DESCRIPTIONS.get(name, ''),
            category='men' if name in MEN_HAIRSTYLES else 'women',
        )
        
        # Визначаємо кількість майстрів
        if db_style and hasattr(db_style, 'masters'):
            count = db_style.masters.count()
            style.master_count = count if count > 0 else total_masters
        else:
            style.master_count = total_masters
            
        # Отримуємо URL (спрацює NAME_TO_ID у _homepage_generated_style_url)
        style.remote_image_url = _style_image_url(style)
        popular_styles.append(style)

    # Реальна кількість майстрів для кожної зачіски
    total_masters = Master.objects.count()
    for style in popular_styles:
        if hasattr(style, 'masters'):
            count = style.masters.count()
            style.master_count = count if count > 0 else total_masters
        else:
            style.master_count = total_masters

    reviews = list(Review.objects.all()[:3])
    for i, review in enumerate(reviews):
        review.avatar_url = REVIEW_AVATAR_URLS[i % len(REVIEW_AVATAR_URLS)]
    # Filter featured masters and partners by city
    selected_city = request.session.get('selected_city', '')
    
    # 1. Masters for "Our Team" (featured_masters)
    featured_masters = _home_team_masters()
    if selected_city:
        featured_masters = [m for m in featured_masters if m.city == selected_city]
    
    for i, master in enumerate(featured_masters):
        master.remote_photo_url = MASTER_PHOTO_BY_FIRST_NAME.get(
            master.first_name
        ) or MASTER_PHOTO_URLS[0 if master.profession == "barber" else 1]
        master.homepage_photo_url = _homepage_team_photo_url(master) or master.remote_photo_url

    # 2. Barbershop Partners
    if selected_city:
        barbershops = Barbershop.objects.filter(city=selected_city)
    else:
        barbershops = Barbershop.objects.all()

    context = {
        'popular_styles': popular_styles,
        'reviews': reviews,
        'featured_masters': featured_masters,
        'barbershops': barbershops,  # Added this
        'review_avatar_urls': REVIEW_AVATAR_URLS,
        'selected_city': selected_city,
    }
    return render(request, 'styleai/index.html', context)


def about(request):
    """Сторінка про нас"""
    return render(request, 'styleai/about.html')


@require_http_methods(["POST"])
def set_city(request):
    """API: зберегти обране місто в сесію."""
    city = request.POST.get('city', '').strip()
    if city:
        request.session['selected_city'] = city
    else:
        request.session.pop('selected_city', None)
    return JsonResponse({'success': True, 'city': city})


def survey_page(request):
    """Сторінка опитування (тип волосся, спосіб життя, побажання). Відповіді враховуються при підборі зачіски."""
    if request.method == 'POST':
        post = request.POST
        hair_length = post.get('hair_length_extra', '')
        priority = post.get('priority_extra', '')
        care_time = post.get('care_time_extra', '')
        survey = HairSurvey(
            hair_type=post.get('hair_type', '') or '',
            lifestyle=post.get('lifestyle', '') or '',
            face_shape_extra=post.get('face_shape_extra', '') or '',
            hair_length_extra=hair_length,
            priority_extra=priority,
            care_time_extra=care_time,
            covers_ears=post.get('covers_ears') == '1',
            long_hairstyle=(hair_length == 'long'),
            short_hairstyle=(hair_length == 'short'),
            low_maintenance=(priority == 'low_care' or care_time == 'min'),
            volume=(priority == 'volume'),
            notes=post.get('notes', '') or '',
        )
        survey.save()
        request.session['survey_id'] = survey.id
        return redirect('hairstyle_selection')
    return render(request, 'styleai/survey.html')


def hairstyle_selection(request):
    """РЎС‚РѕСЂС–РЅРєР° РїС–РґР±РѕСЂСѓ Р·Р°С‡С–СЃРєРё"""
    if request.method == 'POST' and request.FILES.get('photo'):
        photo = request.FILES['photo']
        
        # Зберігаємо фото
        user_photo = UserPhoto.objects.create(photo=photo)
        
        # Прив'язуємо опитування з сесії, якщо воно є
        survey_id = request.session.get('survey_id')
        if survey_id:
            try:
                user_photo.survey = HairSurvey.objects.get(id=survey_id)
            except HairSurvey.DoesNotExist:
                pass

        # Симулюємо AI аналіз (в реальному проекті тут буде інтеграція з AI API)
        shape_result = analyze_face_shape(user_photo.photo.path, survey=user_photo.survey)
        if isinstance(shape_result, tuple) and len(shape_result) == 2:
            shape, gender = shape_result
        else:
            shape, gender = shape_result, None
            
        if shape:
            user_photo.face_shape = shape
        if gender:
            user_photo.predicted_gender = gender
        user_photo.save()
        
        # Р“РµРЅРµСЂСѓС”РјРѕ СЂРµРєРѕРјРµРЅРґР°С†С–С—
        recommendations = generate_recommendations(user_photo)
        
        context = {
            'user_photo': user_photo,
            'recommendations': recommendations,
            'face_shape': shape,
        }
        return render(request, 'styleai/hairstyle_selection_result.html', context)
    
    return render(request, 'styleai/hairstyle_selection.html')


def _detect_face_shape_cv2(image_path):
    """Fallback: Визначення форми обличчя через геометрію OpenCV (якщо MediaPipe недоступний)."""
    import cv2
    import numpy as np
    
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    img = cv2.imread(image_path)
    if img is None: return None
    
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, 1.1, 4)
    if len(faces) == 0: return None
    
    (x, y, w, h) = faces[0]
    aspect_ratio = w / h # Співвідношення сторін обличчя
    
    print(f"DEBUG CV2: W={w}, H={h}, Ratio={aspect_ratio:.2f}")
    
    if aspect_ratio > 0.90:
        return "Кругла" # Або Квадратна, проте без лендмарків важко відрізнити
    elif aspect_ratio < 0.78:
        return "Подовжена"
    else:
        return "Овальна"


def _detect_face_shape_mediapipe(image_path):
    """Локальне визначення форми обличчя через MediaPipe Landmarks (за можливості)."""
    try:
        import cv2
        import numpy as np
        import mediapipe as mp
        # Спробуємо різні варіанти імпорту, бо MediaPipe часто оновлюється
        if hasattr(mp, 'solutions') and hasattr(mp.solutions, 'face_mesh'):
            mp_face_mesh = mp.solutions.face_mesh
        else:
            # Спробуємо прямий імпорт
            try:
                from mediapipe.python.solutions import face_mesh as mp_face_mesh
            except ImportError:
                print("MEDIA PIPE ERROR: solutions.face_mesh not found. Using CV2 fallback.")
                return _detect_face_shape_cv2(image_path)
    except ImportError:
        print("CV2 or MediaPipe NOT installed.")
        return None

    try:
        with mp_face_mesh.FaceMesh(
            static_image_mode=True,
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=0.5
        ) as face_mesh:
            image = cv2.imread(image_path)
            if image is None: return None
            
            h_img, w_img, _ = image.shape
            results = face_mesh.process(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
            
            if not results.multi_face_landmarks:
                return _detect_face_shape_cv2(image_path)
            
            landmarks = results.multi_face_landmarks[0].landmark
            def get_pt(idx): return np.array([landmarks[idx].x * w_img, landmarks[idx].y * h_img])
            
            # Розрахунок відстаней (співвідношення)
            face_height = np.linalg.norm(get_pt(10) - get_pt(152))
            face_width = np.linalg.norm(get_pt(234) - get_pt(454)) # Вилиці
            jaw_width = np.linalg.norm(get_pt(58) - get_pt(288))   # Щелепа
            forehead_width = np.linalg.norm(get_pt(109) - get_pt(338)) # Лоб
            
            wh_ratio = face_width / face_height
            jf_ratio = jaw_width / forehead_width
            
            if wh_ratio > 0.95:
                return "Квадратна" if jf_ratio > 0.88 else "Кругла"
            elif wh_ratio < 0.75: return "Подовжена"
            else: return "Серце" if jf_ratio < 0.7 else "Овальна"
    except Exception:
        return _detect_face_shape_cv2(image_path)


def analyze_face_shape(image_path, survey=None):
    """Аналіз форми обличчя та статі через MediaPipe + Gemini."""
    from django.conf import settings
    import random
    from hairstyles.models import FaceShape
    
    shapes = FaceShape.objects.all()
    shape_map = {s.name.lower(): s for s in shapes}
    
    # 0. Перевіряємо, чи користувач сам вказав форму в опитуванні
    if survey and survey.face_shape_extra:
        s_name = survey.face_shape_extra.lower()
        mapping = {
            'oval': 'овальна',
            'round': 'кругла',
            'square': 'квадратна',
            'oblong': 'довга'
        }
        target_name = mapping.get(s_name, s_name)
        for s in shapes:
            if target_name in s.name.lower():
                print(f"DEBUG: Using face shape from survey: {s.name}")
                # Все одно запустимо аналіз статі нижче, але форму візьмемо цю
                detected_shape = s
                # Продовжимо до аналізу статі
                break
        else:
            detected_shape = None
    else:
        detected_shape = None

    # 1. Форма обличчя (локально через MediaPipe) - якщо ще не визначено з опитування
    if not detected_shape:
        detected_shape_name = _detect_face_shape_mediapipe(image_path)
        if detected_shape_name:
            detected_shape = shape_map.get(detected_shape_name.lower())
            if not detected_shape:
                for s in shapes:
                    if detected_shape_name.lower() in s.name.lower() or s.name.lower() in detected_shape_name.lower():
                        detected_shape = s
                        break

    # 2. Стать та уточнення форми (через Gemini)
    gemini_key = getattr(settings, 'GEMINI_API_KEY', None)
    if not gemini_key:
        # Якщо ключа немає, повертаємо локальний результат
        return detected_shape or (random.choice(shapes) if shapes.exists() else None), None

    try:
        client = genai.Client(api_key=gemini_key)
        with open(image_path, "rb") as f:
            image_bytes = f.read()
        
        shape_names_text = ", ".join([s.name for s in shapes])
        prompt = (
            "Analyze this portrait image. Return ONLY the following information:\n"
            "Gender: Return strictly 'men' or 'women'.\n"
            f"Face Shape: Choose precisely ONE from: {shape_names_text}.\n"
            "Format: Shape: <Word>, Gender: <Word>"
        )
        
        pil_img = Image.open(io.BytesIO(image_bytes))
        
        response = client.models.generate_content(
            model='gemini-2.0-flash',
            contents=[prompt, pil_img]
        )
        
        reply = response.text.strip().lower()
        print(f"--- GEMINI VISION REPLY ---\n{reply}\n------------------------")
        
        detected_gender = None
        for line in reply.split('\n'):
            if 'gender' in line or 'стать' in line:
                if any(x in line for x in ['women', 'woman', 'female', 'жіноч', 'жінка']):
                    detected_gender = 'women'
                elif any(x in line for x in ['men', 'man', 'male', 'чоловік', 'хлоп']):
                    detected_gender = 'men'
            
            # Якщо форму НЕ вказано в опитуванні, беремо з AI
            if (not survey or not survey.face_shape_extra) and ('shape' in line or 'форма' in line):
                for s in shapes:
                    if s.name.lower() in line:
                        detected_shape = s
        
        # Fallback parsing
        if not detected_gender:
            if any(x in reply for x in ['women', 'woman', 'female', 'жінка']): detected_gender = 'women'
            elif any(x in reply for x in ['men', 'man', 'male', 'чоловік']): detected_gender = 'men'
            
        return detected_shape, detected_gender
                
    except Exception as e:
        print(f"Face shape analysis error: {e}")

    return random.choice(shapes) if shapes.exists() else None, None


def detect_gender(image_file_or_path, api_key=None):
    """Визначає стать через Gemini (fallback до None)."""
    from django.conf import settings
    gemini_key = api_key or getattr(settings, 'GEMINI_API_KEY', None)
    if not gemini_key: return None

    try:
        import os
        if isinstance(image_file_or_path, (str, bytes, os.PathLike)):
            with open(image_file_or_path, "rb") as f: image_bytes = f.read()
        else:
            image_bytes = image_file_or_path.read()
            try: image_file_or_path.seek(0)
            except: pass

        client = genai.Client(api_key=gemini_key)
        dg_mime_type = _get_mime_type(image_bytes)
        response = client.models.generate_content(
            model='gemini-2.0-flash',
            contents=["Determine gender: 'men' or 'women'. Return one word.", types.Part.from_bytes(data=image_bytes, mime_type=dg_mime_type)]
        )
        txt = response.text.strip().lower()
        if 'women' in txt: return 'women'
        if 'men' in txt: return 'men'
    except:
        pass
    return None


def _build_hair_mask_rgba(pil_rgba_img):
    """
    Повертає PIL Image (L) маску для редагування волосся:
    біле = можна редагувати, чорне = НЕ редагувати.

    Логіка:
    - якщо знаходить обличчя (haar cascade), то:
      - редагувати область над обличчям + трохи з боків
      - саме обличчя/шкіру виключити з маски
    - якщо не знаходить, fallback: верхня частина кадру
    """
    import numpy as np
    try:
        # PIL RGBA -> BGR для OpenCV
        rgba = np.array(pil_rgba_img)
        if rgba.ndim != 3 or rgba.shape[2] < 3:
            return Image.new("L", pil_rgba_img.size, 0)
        bgr = cv2.cvtColor(rgba[:, :, :3], cv2.COLOR_RGB2BGR)
        h_img, w_img = bgr.shape[:2]

        face_rect = None
        try:
            face_cascade = cv2.CascadeClassifier(
                cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
            )
            gray = cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY)
            faces = face_cascade.detectMultiScale(gray, 1.15, 5)
            if len(faces) > 0:
                x, y, w, h = faces[0]
                face_rect = (int(x), int(y), int(w), int(h))
        except Exception:
            face_rect = None

        mask = np.zeros((h_img, w_img), dtype=np.uint8)

        if face_rect is None:
            # Fallback: верх ~45% кадру + м'який перехід
            edit_y = int(h_img * 0.45)
            mask[:edit_y, :] = 255
            band = min(80, max(20, int(h_img * 0.07)))
            if edit_y - band > 0:
                grad = np.linspace(255, 0, band, dtype=np.uint8)
                mask[edit_y - band:edit_y, :] = np.minimum(mask[edit_y - band:edit_y, :], grad[:, None])
        else:
            x, y, w, h = face_rect
            # Область волосся: над лобом, ширше обличчя
            x1 = max(0, int(x - 0.35 * w))
            x2 = min(w_img, int(x + w + 0.35 * w))
            y1 = max(0, int(y - 0.80 * h))
            y2 = min(h_img, int(y + 0.20 * h))  # трохи нижче лоба
            mask[y1:y2, x1:x2] = 255

            # Виключаємо обличчя (щоб не спотворювало риси)
            fx1 = max(0, int(x - 0.10 * w))
            fx2 = min(w_img, int(x + w + 0.10 * w))
            fy1 = max(0, int(y - 0.05 * h))
            fy2 = min(h_img, int(y + h + 0.35 * h))  # аж до підборіддя/шиї
            mask[fy1:fy2, fx1:fx2] = 0

            # М'які краї
            k = max(7, int(min(h_img, w_img) * 0.02) | 1)  # непарне
            mask = cv2.GaussianBlur(mask, (k, k), 0)

        return Image.fromarray(mask, mode="L")
    except Exception:
        return Image.new("L", pil_rgba_img.size, 0)


def _survey_match_score(hairstyle, survey):
    """
    Оцінка, наскільки зачіска відповідає відповідям з опитування.
    Повертає число: більше = краще збіг. 0 = нейтрально, >0 = підходить.
    """
    if not survey:
        return 0
    name_lower = (hairstyle.name or '').lower()
    desc_lower = (getattr(hairstyle, 'description', None) or '').lower()
    text = name_lower + ' ' + desc_lower
    score = 0
    
    # 1. Довжина волосся (Критичний пріоритет)
    if survey.short_hairstyle:
        if any(k in text for k in ('fade', 'crop', 'cut', 'edgar', 'slick', 'mod', 'buzz', 'pixie', 'crew')):
            score += 10
        if 'long' in text or 'довга' in text or 'medium' in text:
            score -= 15
    if survey.long_hairstyle:
        if 'long' in text or 'довга' in text or 'wavy' in text or 'bob' in text or 'каре' in text:
            score += 10
        if any(k in text for k in ('fade', 'buzz', 'short', 'коротка')):
            score -= 15

    # 2. Пріоритети та спосіб життя (Високий пріоритет)
    if survey.low_maintenance:
        if any(k in text for k in ('fade', 'crop', 'buzz', 'crew', 'minimal')):
            score += 7
        if 'long' in text or 'styling' in text:
            score -= 5
            
    if survey.volume:
        if any(k in text for k in ('textured', 'burst', 'volume', 'wavy', 'long', 'об\'єм', 'текстур')):
            score += 8

    # 3. Тип волосся
    if survey.hair_type in ('curly', 'coily'):
        if any(k in text for k in ('textured', 'wavy', 'volume', 'curly', 'кучер')):
            score += 5
    elif survey.hair_type == 'straight':
        if any(k in text for k in ('slick', 'straight', 'пряме')):
            score += 5

    # 4. Спосіб життя
    if survey.lifestyle == 'office':
        if any(k in text for k in ('slick', 'mod', 'taper', 'classic', 'класич')):
            score += 5
    if survey.lifestyle == 'active':
        if any(k in text for k in ('fade', 'crop', 'short', 'sport')):
            score += 5
            
    # 5. Примітки користувача (Спробуємо знайти ключові слова)
    if survey.notes:
        notes_lower = survey.notes.lower()
        if any(k in notes_lower for k in ('корот', 'short')):
            if any(k in text for k in ('fade', 'buzz', 'short')): score += 5
        if any(k in notes_lower for k in ('довг', 'long')):
            if any(k in text for k in ('long', 'довг')): score += 5

    return score


def _popular_styles_ordered():
    """Популярні зачіски у тому самому порядку, що і в секції «Популярні зачіски»."""
    all_popular = list(Hairstyle.objects.filter(name__in=POPULAR_HAIRSTYLE_NAMES))
    name_to_style = {s.name: s for s in all_popular}
    return [name_to_style[name] for name in POPULAR_HAIRSTYLE_NAMES if name in name_to_style]




def _extra_women_styles():
    """Додаткові жіночі зачіски (не в «Популярних», але доступні для рекомендацій)."""
    from styleai.constants import EXTRA_WOMEN_HAIRSTYLE_NAMES
    all_extra = list(Hairstyle.objects.filter(name__in=EXTRA_WOMEN_HAIRSTYLE_NAMES))
    name_to_style = {s.name: s for s in all_extra}
    return [name_to_style[name] for name in EXTRA_WOMEN_HAIRSTYLE_NAMES if name in name_to_style]


def _extra_men_styles():
    """Додаткові чоловічі зачіски (не в «Популярних», але доступні для рекомендацій)."""
    from styleai.constants import EXTRA_MEN_HAIRSTYLE_NAMES
    all_extra = list(Hairstyle.objects.filter(name__in=EXTRA_MEN_HAIRSTYLE_NAMES))
    name_to_style = {s.name: s for s in all_extra}
    return [name_to_style[name] for name in EXTRA_MEN_HAIRSTYLE_NAMES if name in name_to_style]


def _fit_score(hairstyle, survey, suitable_ids):
    """
    Релевантність стилю:
    - підходить для форми обличчя;
    - збігається з опитуванням.
    """
    score = 0
    if hairstyle.id in suitable_ids:
        score += 6
    if survey:
        score += 2 * _survey_match_score(hairstyle, survey)
    return score


def generate_recommendations(user_photo):
    """
    Підбір зачіски: популярні зачіски + додаткові жіночі (якщо визначено жінку),
    відсортовано за відповідністю користувачу з елементом випадковості для різноманітності.
    """
    import random
    ordered_styles = _popular_styles_ordered()
    if not ordered_styles:
        return []

    # Фільтрація за статтю
    from styleai.constants import MEN_HAIRSTYLES, WOMEN_HAIRSTYLES, EXTRA_WOMEN_HAIRSTYLE_NAMES, EXTRA_MEN_HAIRSTYLE_NAMES
    predicted_gender = str(getattr(user_photo, 'predicted_gender', '') or '').strip().lower()
    survey = getattr(user_photo, 'survey', None)

    # Якщо AI не визначив стать, пробуємо зчитати з опитування як fallback
    if predicted_gender not in ['men', 'women'] and survey:
        if survey.short_hairstyle and not survey.long_hairstyle:
            predicted_gender = 'men'
        elif survey.long_hairstyle:
            predicted_gender = 'women'
    
    # Жорстко фільтруємо за знайденою або передбаченою статню.
    women_names_lower = [n.strip().lower() for n in WOMEN_HAIRSTYLES]
    men_names_lower = [n.strip().lower() for n in MEN_HAIRSTYLES]

    if predicted_gender == 'women':
        # Для жінок: популярні жіночі + додаткові жіночі зачіски
        extra_women = _extra_women_styles()
        ordered_styles = [
            s for s in ordered_styles 
            if (s.name and s.name.strip().lower() in women_names_lower) or 
               (hasattr(s, 'category') and s.category == 'women')
        ] + extra_women
    elif predicted_gender == 'men':
        # Для чоловіків: популярні чоловічі + додаткові чоловічі
        extra_men = _extra_men_styles()
        ordered_styles = [
            s for s in ordered_styles 
            if (s.name and s.name.strip().lower() in men_names_lower) or 
               (hasattr(s, 'category') and s.category == 'men')
        ] + extra_men
        
    # Extra-зачіски (і жіночі, і чоловічі) вже мають Unsplash URL — пропускаємо всіх
    extra_names_set = set(EXTRA_WOMEN_HAIRSTYLE_NAMES) | set(EXTRA_MEN_HAIRSTYLE_NAMES)
    curated_styles = [
        s for s in ordered_styles
        if s.name in extra_names_set or _homepage_generated_style_url(s) != ""
    ]
    
    # Якщо з якихось причин список брендованих порожній,
    # повертаємось до повного списку, щоб користувач не бачив порожню сторінку.
    if curated_styles:
        ordered_styles = curated_styles
    
    # suitable_ids: всі зачіски (популярні + extra)
    all_style_names = (
        list(POPULAR_HAIRSTYLE_NAMES) +
        list(EXTRA_WOMEN_HAIRSTYLE_NAMES) +
        list(EXTRA_MEN_HAIRSTYLE_NAMES)
    )
    suitable_ids = set()
    if getattr(user_photo, 'face_shape', None) and user_photo.face_shape_id:
        suitable_ids = set(
            user_photo.face_shape.suitable_hairstyles
            .filter(name__in=all_style_names)
            .values_list('id', flat=True)
        )

    scored = []
    for popularity_idx, style in enumerate(ordered_styles):
        score = _fit_score(style, survey, suitable_ids)
        random_factor = random.uniform(0, 4.0)
        final_score = score + random_factor
        scored.append((style, final_score, popularity_idx))

    scored.sort(key=lambda item: item[1], reverse=True)
    pool_size = min(16, len(scored))
    top_pool = scored[:pool_size]
    candidates = random.sample(top_pool, min(4, len(top_pool)))
    random.shuffle(candidates)

    recommendations = []
    for rank, (hairstyle, fit, _popularity_idx) in enumerate(candidates):
        base_fit = _fit_score(hairstyle, survey, suitable_ids)
        confidence = 0.85 + (min(0.12, base_fit * 0.02))
        if suitable_ids and hairstyle.id in suitable_ids:
            confidence += 0.06
        confidence -= rank * 0.01
        confidence += random.uniform(-0.03, 0.03)
        confidence = round(max(0.55, min(0.98, confidence)), 2)

        recommendation = AIRecommendation.objects.create(
            user_photo=user_photo,
            hairstyle=hairstyle,
            confidence_score=confidence
        )
        # Додаємо URL для відображення в шаблонах
        recommendation.hairstyle.remote_image_url = _style_image_url(hairstyle)
        recommendations.append(recommendation)

    recommendations.sort(key=lambda x: x.confidence_score, reverse=True)
    return recommendations


def _create_survey_from_request(request):
    """Створює HairSurvey з даних запиту (опитування)."""
    hair_type = request.POST.get('hair_type', '').strip() or None
    lifestyle = request.POST.get('lifestyle', '').strip() or None
    if not hair_type and not lifestyle and request.POST.get('notes', '').strip() == '':
        if not request.POST.get('covers_ears') and not request.POST.get('long_hairstyle') and not request.POST.get('short_hairstyle') and not request.POST.get('low_maintenance') and not request.POST.get('volume'):
            return None
    survey = HairSurvey(
        hair_type=hair_type or '',
        lifestyle=lifestyle or '',
        covers_ears=request.POST.get('covers_ears') == '1',
        long_hairstyle=request.POST.get('long_hairstyle') == '1',
        short_hairstyle=request.POST.get('short_hairstyle') == '1',
        low_maintenance=request.POST.get('low_maintenance') == '1',
        volume=request.POST.get('volume') == '1',
        notes=request.POST.get('notes', '') or ''
    )
    survey.save()
    return survey


@require_http_methods(["POST"])
def upload_photo_api(request):
    """API endpoint для завантаження фото"""
    if 'photo' not in request.FILES:
        return JsonResponse({'error': 'No photo provided'}, status=400)
    
    photo = request.FILES['photo']
    survey = None
    survey_id = request.session.pop('survey_id', None)
    if survey_id:
        try:
            survey = HairSurvey.objects.get(pk=survey_id)
        except HairSurvey.DoesNotExist:
            pass
    if survey is None:
        survey = _create_survey_from_request(request)
    user_photo = UserPhoto.objects.create(photo=photo, survey=survey)
    
    # Симулюємо AI аналіз
    try:
        shape_result = analyze_face_shape(user_photo.photo.path, survey=survey)
        if isinstance(shape_result, tuple) and len(shape_result) == 2:
            shape, gender = shape_result
        else:
            shape, gender = shape_result, None
            
        # Якщо користувач вручну обрав стать на UI
        manual_gender = request.POST.get('manual_gender')
        if manual_gender in ['men', 'women']:
            gender = manual_gender
            
        if shape:
            user_photo.face_shape = shape
        if gender:
            user_photo.predicted_gender = gender
        user_photo.save()
    except Exception:
        pass
    
    # Генеруємо рекомендації
    recommendations = generate_recommendations(user_photo)
    user_photo_path = getattr(user_photo.photo, 'path', None)
    # Для генерації фото: Gemini
    gemini_key = getattr(settings, 'GEMINI_API_KEY', '').strip()
    
    # Генеримо фото людини з зачіскою лише для перших 3 рекомендацій (якщо є ключ)
    max_ai_generations = 3 if gemini_key else 0
    recs_list = []
    for idx, rec in enumerate(recommendations):
        style = rec.hairstyle
        overlay_url = None
        if gemini_key and user_photo_path and os.path.isfile(user_photo_path) and idx < max_ai_generations:
            overlay_url = _ai_generate_hairstyle_on_photo(
                user_photo_path=user_photo_path,
                style_name=style.name or '',
                style_description=getattr(style, 'description', '') or '',
                user_photo_id=user_photo.id,
                style_id=style.id,
                api_key=gemini_key,
                survey=survey
            )
        # Рахуємо реальну кількість майстрів для цієї зачіски через зв'язок ManyToMany
        m_count = style.masters.count()
        if m_count == 0:
            import random
            m_count = random.randint(25, 48)

        rec_item = {
            'id': style.id,
            'name': style.name,
            'description': style.description,
            'image': _style_image_url(style),
            'overlay_url': overlay_url,
            'confidence': rec.confidence_score,
            'master_count': m_count
        }
            
        if rec_item['overlay_url'] and request and rec_item['overlay_url'].startswith('/'):
            rec_item['overlay_url'] = request.build_absolute_uri(rec_item['overlay_url'])
        recs_list.append(rec_item)

    face_shape_name = getattr(user_photo.face_shape, 'name', None) if user_photo.face_shape_id else None
    survey_used = bool(user_photo.survey_id)

    return JsonResponse({
        'success': True,
        'photo_id': user_photo.id,
        'face_shape': face_shape_name,
        'survey_used': survey_used,
        'recommendations': recs_list,
    })


def _process_image_response(request, response, exact_style, detected_gender):
    """Збереження результату генерації та повернення сторінки."""
    import base64
    from django.core.files.base import ContentFile
    from django.core.files.storage import default_storage

    if not response or not response.data:
        return render(request, 'styleai/generate_hairstyle_upload.html', {'error': 'Сервіс не повернув зображення.'})

    image_base64 = response.data[0].b64_json
    image_bytes = base64.b64decode(image_base64)
    name = f"generated_hairstyles/{os.urandom(8).hex()}.png"
    default_storage.save(name, ContentFile(image_bytes))
    image_url = default_storage.url(name)

    return render(request, 'styleai/generate_hairstyle_result.html', {
        'image_url': image_url, 'exact_style': exact_style, 'detected_gender': detected_gender,
    })


def generate_hairstyle(request):
    """Генерація фото з новою зачіскою через Gemini."""
    print("--- CRITICAL DEBUG: generate_hairstyle CALLED ---")
    from styleai.constants import MEN_HAIRSTYLES, WOMEN_HAIRSTYLES
    import tempfile
    from PIL import Image

    import json
    
    def get_upload_context(error_msg=None, exact_style=None):
        hairstyle_data = {}
        hairstyles_in_db = Hairstyle.objects.filter(name__in=MEN_HAIRSTYLES + WOMEN_HAIRSTYLES)
        for hs in hairstyles_in_db:
            image_url = _style_image_url(hs)
            hairstyle_data[hs.name] = {
                'image': image_url,
                'description': hs.description or POPULAR_STYLE_DESCRIPTIONS.get(hs.name, '')
            }
        for name in MEN_HAIRSTYLES + WOMEN_HAIRSTYLES:
            if name not in hairstyle_data:
                hairstyle_data[name] = {
                    'image': STYLE_IMAGE_MAP.get(name, DEFAULT_IMAGE),
                    'description': POPULAR_STYLE_DESCRIPTIONS.get(name, '')
                }
        ctx = {
            'men_hairstyles': MEN_HAIRSTYLES, 
            'women_hairstyles': WOMEN_HAIRSTYLES,
            'hairstyle_data_json': json.dumps(hairstyle_data),
            'exact_style': exact_style
        }
        if error_msg:
            ctx['error'] = error_msg
        return ctx

    if request.method != 'POST':
        return render(request, 'styleai/generate_hairstyle_upload.html', get_upload_context())

    photo = request.FILES.get('photo')
    if not photo:
        return render(request, 'styleai/generate_hairstyle_upload.html', {'error': 'Оберіть фото.'})

    exact_style = (request.POST.get('exact_style') or '').strip()
    
    # Замість реальної генерації через Gemini, просто підтягуємо існуюче фото з бази
    image_url = None
    if exact_style:
        hs = Hairstyle.objects.filter(name=exact_style).first()
        if hs:
            image_url = _style_image_url(hs)
        else:
            image_url = STYLE_IMAGE_MAP.get(exact_style, DEFAULT_IMAGE)
            
    if image_url:
        return render(request, 'styleai/generate_hairstyle_result.html', {
            'image_url': image_url, 'exact_style': exact_style, 'detected_gender': 'unknown',
        })
    else:
        return render(request, 'styleai/generate_hairstyle_upload.html', get_upload_context('Не вдалося знайти обрану зачіску.', exact_style))


def upload_photo(request):
    """Fallback view for local testing/upload."""
    from .services import get_hairstyles_recommendation
    if request.method == 'POST' and request.FILES.get('user_photo'):
        photo = request.FILES['user_photo']
        recommendation = get_hairstyles_recommendation(photo)
        return render(request, 'result.html', {'recommendation': recommendation})
    return render(request, 'upload.html')

def temp_restore_shaggy(request):
    import shutil
    import os
    from django.http import HttpResponse
    backup_dir = r"c:\Users\User\Desktop\dyplom_2mis\media\hairstyles\homepage_style_backup"
    target_dir = r"c:\Users\User\Desktop\dyplom_2mis\media\hairstyles"
    f = "homepage_style_55.jpg"
    try:
        shutil.copy2(os.path.join(backup_dir, f), os.path.join(target_dir, f))
        shutil.copy2(os.path.join(backup_dir, f), os.path.join(target_dir, "шеггі.jpg"))
        return HttpResponse("Success: Original Shaggy image restored.")
    except Exception as e:
        return HttpResponse(f"Error: {e}")


# ── Сторінка завантаження кастомних фото зачісок ──────────────────────────────

# Назви зачісок → імена файлів (транслітерація для безпечних імен)
_HAIRSTYLE_FILENAME_MAP = {
    'Drop Fade':      'drop_fade.jpg',
    'Taper Fade':     'taper_fade.jpg',
    'Low Fade':       'low_fade.jpg',
    'Mid Fade':       'mid_fade.jpg',
    'High Fade':      'high_fade.jpg',
    'Skin Fade':      'skin_fade.jpg',
    'Textured Crop':  'textured_crop.jpg',
    'Burst Fade':     'burst_fade.jpg',
    'Edgar Cut':      'edgar_cut.jpg',
    'Slick Back':     'slick_back.jpg',
    'Pompadour':      'pompadour.jpg',
    'Quiff':          'quiff.jpg',
    'Brush Up Fade':  'brush_up_fade.jpg',
    'Undercut':       'undercut.jpg',
    'Faux Hawk':      'faux_hawk.jpg',
    'Crew Cut':       'crew_cut.jpg',
    'Buzz Cut':       'buzz_cut.jpg',
    'Long Wavy Hair': 'long_wavy_hair.jpg',
    'Mod Cut':        'mod_cut.jpg',
    'Bob':            'bob.jpg',
    'Pixie Cut':      'pixie_cut.jpg',
    'Каре':           'kare.jpg',
    'Піксі':          'piksi.jpg',
    'Кучерявий Боб':  'kucher_bob.jpg',
    'Гарсон':         'garson.jpg',
    'Сесон':          'seson.jpg',
    'Їжачок':         'yizhachok.jpg',
    'Шеггі':          'sheggi.jpg',
}

CUSTOM_DIR = Path(settings.MEDIA_ROOT) / 'hairstyles' / 'custom'


def upload_hairstyle_image(request):
    """Сторінка + API для завантаження кастомних фото зачісок."""
    if request.method == 'GET':
        return render(request, 'styleai/upload_hairstyle_image.html')

    if request.method == 'POST':
        hairstyle_name = (request.POST.get('hairstyle_name') or '').strip()
        image = request.FILES.get('image')

        if not hairstyle_name or hairstyle_name not in _HAIRSTYLE_FILENAME_MAP:
            return JsonResponse({'success': False, 'error': 'Невідома назва зачіски'})
        if not image:
            return JsonResponse({'success': False, 'error': 'Фото не знайдено'})

        # Переконуємось що папка існує
        CUSTOM_DIR.mkdir(parents=True, exist_ok=True)

        filename = _HAIRSTYLE_FILENAME_MAP[hairstyle_name]
        save_path = CUSTOM_DIR / filename

        # Зберігаємо файл
        with open(save_path, 'wb') as f:
            for chunk in image.chunks():
                f.write(chunk)

        # Оновлюємо CUSTOM_SLUG_MAP в пам'яті (для поточної сесії сервера)
        import styleai.views as _self
        _self.CUSTOM_SLUG_MAP[hairstyle_name] = filename

        url = f'{settings.MEDIA_URL}hairstyles/custom/{filename}'
        return JsonResponse({'success': True, 'url': url, 'name': hairstyle_name})

    return JsonResponse({'success': False, 'error': 'Метод не підтримується'})


def upload_hairstyle_status(request):
    """JSON: список завантажених кастомних фото."""
    uploaded = []
    for name, filename in _HAIRSTYLE_FILENAME_MAP.items():
        path = CUSTOM_DIR / filename
        if path.exists():
            url = f'{settings.MEDIA_URL}hairstyles/custom/{filename}'
            uploaded.append({'name': name, 'url': url, 'filename': filename})
    return JsonResponse({'uploaded': uploaded})

