from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Q
from django.views.decorators.http import require_GET, require_POST
from masters.models import Master, Review, Booking
from hairstyles.models import Hairstyle
from styleai.constants import POPULAR_HAIRSTYLE_NAMES, HAIRSTYLE_LENGTH, HAIRSTYLE_LENGTH_LABELS
from .utils import apply_hair_overlay
from .telegram_bot import send_telegram_message_to_barber, send_telegram_message_to_client, send_telegram_notification_to_admin
try:
    import cv2
except ImportError:
    cv2 = None
import mediapipe as mp
import numpy as np
from django.http import JsonResponse
from datetime import date, timedelta, datetime
from decimal import Decimal

def find_master(request):
    """Пошук майстра/барбера: фільтрація по типах стрижок, місту, ім'ю; прив'язка до послуг (спеціалізацій), портфоліо на картці."""
    masters = Master.objects.prefetch_related('specialties', 'gallery_photos', 'services').all()
    category_labels = {'men': 'Чоловічі', 'women': 'Жіночі', 'unisex': 'Унісекс'}
    qs = Hairstyle.objects.filter(name__in=POPULAR_HAIRSTYLE_NAMES)
    popular_styles = sorted(qs, key=lambda s: POPULAR_HAIRSTYLE_NAMES.index(s.name) if s.name in POPULAR_HAIRSTYLE_NAMES else 999)

    # ── Будуємо групи фільтрів з констант (незалежно від категорії в БД) ──────
    from styleai.constants import MEN_HAIRSTYLES, WOMEN_HAIRSTYLES
    men_names_set   = set(MEN_HAIRSTYLES)
    women_names_set = set(WOMEN_HAIRSTYLES)
    popular_by_name = {s.name: s for s in popular_styles}

    # Чоловічі — у порядку POPULAR_HAIRSTYLE_NAMES, лише ті що є в БД
    men_filter   = [popular_by_name[n] for n in POPULAR_HAIRSTYLE_NAMES if n in men_names_set   and n in popular_by_name]
    women_filter = [popular_by_name[n] for n in POPULAR_HAIRSTYLE_NAMES if n in women_names_set and n in popular_by_name]
    unisex_filter = [s for s in popular_styles if s.name not in men_names_set and s.name not in women_names_set]

    popular_by_category = {'men': men_filter, 'women': women_filter, 'unisex': unisex_filter}
    popular_style_groups = [
        (lbl, lst) for lbl, lst in [
            ('Чоловічі', men_filter),
            ('Жіночі',   women_filter),
            ('Унісекс',  unisex_filter),
        ] if lst
    ]

    # Тільки ті типи стрижок, під які є хоча б один майстер
    style_ids_with_masters = Master.objects.values_list('specialties', flat=True).distinct()
    all_styles = list(Hairstyle.objects.filter(pk__in=style_ids_with_masters).order_by('category', 'name'))
    for s in all_styles:
        length_key = HAIRSTYLE_LENGTH.get(s.name, 'medium')
        s.length_label = HAIRSTYLE_LENGTH_LABELS.get(length_key, 'Середня')
    styles_by_category = {'men': [], 'women': [], 'unisex': []}
    for s in all_styles:
        if s.category in styles_by_category:
            styles_by_category[s.category].append(s)
    # Групи для select: спочатку чоловічі, потім жіночі, потім унісекс
    style_groups = [
        (category_labels[cat], styles_by_category[cat])
        for cat in ('men', 'women', 'unisex')
        if styles_by_category[cat]
    ]

    style_query = request.GET.get('style', '').strip()
    style_id = request.GET.get('style_id', '').strip()
    style_id_int = int(style_id) if style_id and style_id.isdigit() else None
    category_query = request.GET.get('category', '').strip()
    city_query = request.GET.get('city', '').strip()
    if not city_query:
        city_query = request.session.get('selected_city', '').strip()
    name_query = request.GET.get('name', '').strip()

    all_masters_qs = Master.objects.prefetch_related('specialties', 'gallery_photos', 'services')
    if style_id_int:
        masters = masters.filter(specialties__id=style_id_int).distinct()
        if not masters.exists():
            masters = all_masters_qs.all()
    elif style_query:
        # 1) Точний збіг
        matched = all_masters_qs.filter(specialties__name__iexact=style_query).distinct()
        if matched.exists():
            masters = matched
        else:
            # 2) Частковий збіг
            matched = all_masters_qs.filter(specialties__name__icontains=style_query).distinct()
            if matched.exists():
                masters = matched
            else:
                # 3) По кожному слову
                found = None
                for word in [w for w in style_query.split() if len(w) > 2]:
                    matched = all_masters_qs.filter(specialties__name__icontains=word).distinct()
                    if matched.exists():
                        found = matched
                        break
                # 4) Fallback — всі майстри (спеціальності ще не прив'язані)
                masters = found if found is not None else all_masters_qs.all()

    if category_query and category_query in ('men', 'women', 'unisex'):
        masters = masters.filter(specialties__category=category_query).distinct()

    # Пошук за ім'ям або стилем: кожне слово — окремо (будь-яке збігається)
    if name_query:
        words = [w.strip() for w in name_query.split() if w.strip()]
        if words:
            name_q = Q()
            for word in words:
                name_q |= (
                    Q(first_name__icontains=word) |
                    Q(last_name__icontains=word) |
                    Q(specialties__name__icontains=word)
                )
            masters = masters.filter(name_q).distinct()

    # Save style results separately for fallback
    style_masters = masters
    
    # 3. Filter by city or district
    if city_query:
        city_masters = style_masters.filter(
            Q(city__icontains=city_query) | Q(district__icontains=city_query)
        ).distinct()
        
        # If no masters found for this style in this city, 
        # but the user specifically looked for a style, 
        # fallback to all masters in this city.
        if not city_masters.exists() and (style_query or style_id_int):
            masters = Master.objects.prefetch_related('specialties', 'gallery_photos', 'services').filter(
                Q(city__icontains=city_query) | Q(district__icontains=city_query)
            ).distinct()
            context_note = "У вашому місті поки немає майстрів з цією спеціалізацією. Показуємо всіх майстрів міста."
        else:
            masters = city_masters
            context_note = None
    else:
        masters = style_masters
        context_note = None

    context = {
        'masters': masters,
        'context_note': context_note,
        'popular_styles': popular_styles,
        'popular_by_category': popular_by_category,
        'popular_style_groups': popular_style_groups,
        'all_styles': all_styles,
        'styles_by_category': styles_by_category,
        'style_groups': style_groups,
        'category_labels': category_labels,
        'style_query': style_query,
        'style_id': style_id,
        'style_id_int': style_id_int,
        'category_query': category_query,
        'city_query': city_query,
        'name_query': name_query,
    }
    return render(request, 'masters/find_master.html', context)


def master_detail(request, master_id):
    """Детальна інформація про майстра: портфоліо, прив'язка до послуг, відгуки."""
    master = get_object_or_404(
        Master.objects.prefetch_related('specialties', 'gallery_photos', 'services'),
        id=master_id
    )
    reviews = Review.objects.filter(master=master)
    
    context = {
        'master': master,
        'reviews': reviews,
    }
    return render(request, 'masters/master_detail.html', context)


def analyze_and_find_barber(request):
    """ШІ підбір стрижки та пошук майстра"""
    if request.method == 'POST' and request.FILES.get('photo'):
        try:
            # 1. Ініціалізація ШІ всередині функції (щоб не було помилок при міграціях)
            mp_face_mesh = mp.solutions.face_mesh
            face_mesh = mp_face_mesh.FaceMesh(
                static_image_mode=True,
                max_num_faces=1,
                refine_landmarks=True,
                min_detection_confidence=0.5
            )

            # 2. Обробка зображення
            file = request.FILES['photo']
            image_bytes = np.frombuffer(file.read(), np.uint8)
            image = cv2.imdecode(image_bytes, cv2.IMREAD_COLOR)
            
            if image is None:
                return JsonResponse({'error': 'Не вдалося прочитати зображення'}, status=400)
                
            rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            results = face_mesh.process(rgb_image)

            if not results.multi_face_landmarks:
                return render(request, 'masters/upload.html', {'error': 'Обличчя не знайдено на фото. Спробуйте інше.'})

            # 3. Аналіз форми обличчя
            landmarks = results.multi_face_landmarks[0].landmark
            
            # Розрахунок відстаней (використовуємо індекси точок MediaPipe)
            top_head = np.array([landmarks[10].x, landmarks[10].y])
            bottom_chin = np.array([landmarks[152].x, landmarks[152].y])
            left_cheek = np.array([landmarks[234].x, landmarks[234].y])
            right_cheek = np.array([landmarks[454].x, landmarks[454].y])

            h = np.linalg.norm(top_head - bottom_chin)
            w = np.linalg.norm(left_cheek - right_cheek)
            ratio = h / w

            if ratio > 1.5:
                shape = "Видовжене"
                suggested_styles = ["Side Part", "Classic Scissor Cut"]
            elif ratio < 1.25:
                shape = "Кругле"
                suggested_styles = ["Undercut", "Pompadour", "High Fade"]
            else:
                shape = "Овальне/Квадратне"
                suggested_styles = ["Buzz Cut", "Crew Cut", "Fade"]

            # 4. Пошук майстрів у вашій моделі Master за спеціалізацією
            # Використовуємо Q об'єкт для пошуку збігів у стилях
            query = Q()
            for style in suggested_styles:
                query |= Q(specialties__name__icontains=style)
            
            # Filter by city if selected
            selected_city = request.session.get('selected_city', '').strip()
            if selected_city:
                query &= Q(city__icontains=selected_city)
            
            masters = Master.objects.prefetch_related('specialties', 'gallery_photos', 'services').filter(query).distinct()[:5]

            return render(request, 'masters/result.html', {
                'shape': shape,
                'styles': suggested_styles,
                'masters': masters
            })
            
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    return render(request, 'masters/upload.html')

def process_look(request):
    if request.method == 'POST':
        selected_style_name = request.POST.get('style_name')
        if not selected_style_name:
            return JsonResponse({'error': 'style_name required'}, status=400)
        style = get_object_or_404(Hairstyle, name=selected_style_name)
        masters_qs = Master.objects.prefetch_related('specialties', 'gallery_photos', 'services').filter(specialties__name=selected_style_name)
        
        selected_city = request.session.get('selected_city', '').strip()
        if selected_city:
            masters_qs = masters_qs.filter(city__icontains=selected_city)
            
        masters = masters_qs.distinct()[:12]
        return render(request, 'masters/result.html', {
            'shape': getattr(style, 'category', ''),
            'styles': [selected_style_name],
            'masters': masters,
        })


# --- Запис до майстра: кроки (тип стрижки → майстри → дата/час → підтвердження) ---

def booking_page(request):
    """Сторінка запису: крок 1 — вибір типу стрижки. Далі JS підтягує майстрів, слоты, відправляє форму."""
    qs = Hairstyle.objects.filter(name__in=POPULAR_HAIRSTYLE_NAMES)
    popular_styles = sorted(
        list(qs),
        key=lambda s: POPULAR_HAIRSTYLE_NAMES.index(s.name) if s.name in POPULAR_HAIRSTYLE_NAMES else 999
    )
    pre_select_master_id = request.GET.get('master_id', '')
    context = {
        'popular_styles': popular_styles,
        'pre_select_master_id': pre_select_master_id,
    }
    return render(request, 'masters/booking.html', context)


@require_GET
def booking_api_styles(request):
    """API: список зачісок для модалки запису. Якщо передано master_id — лише зачіски цього майстра (його спеціалізації)."""
    master_id = request.GET.get('master_id')
    if master_id:
        try:
            master = Master.objects.prefetch_related('specialties').get(pk=master_id)
            styles_qs = master.specialties.all().order_by('name')
            out = [{'id': s.id, 'name': s.name} for s in styles_qs]
            return JsonResponse({'styles': out})
        except Master.DoesNotExist:
            pass
    # Тільки популярні зачіски, під які є хоча б один майстер
    style_ids_with_masters = Master.objects.values_list('specialties', flat=True).distinct()
    qs = Hairstyle.objects.filter(
        name__in=POPULAR_HAIRSTYLE_NAMES,
        pk__in=style_ids_with_masters
    )
    ordered = sorted(
        list(qs),
        key=lambda s: POPULAR_HAIRSTYLE_NAMES.index(s.name) if s.name in POPULAR_HAIRSTYLE_NAMES else 999
    )
    out = [{'id': s.id, 'name': s.name} for s in ordered]
    return JsonResponse({'styles': out})


@require_GET
def booking_api_masters(request):
    """API: майстри, які роблять обрану зачіску (style_id) АБО пошук одного майстра за ID."""
    style_id = request.GET.get('style_id')
    master_id = request.GET.get('master_id')

    if master_id:
        masters = Master.objects.filter(pk=master_id)
    elif style_id:
        style = get_object_or_404(Hairstyle, pk=style_id)
        masters_qs = Master.objects.filter(specialties=style)
        
        selected_city = request.session.get('selected_city', '').strip()
        if selected_city:
            masters_qs = masters_qs.filter(city__icontains=selected_city)
            
        masters = masters_qs.distinct().order_by('-rating', '-experience_years')
        if not masters.exists() and style.name:
            words = [w.strip() for w in style.name.split() if len(w.strip()) > 2]
            for word in words:
                masters_qs = Master.objects.filter(specialties__name__icontains=word)
                if selected_city:
                    masters_qs = masters_qs.filter(city__icontains=selected_city)
                masters = masters_qs.distinct().order_by('-rating', '-experience_years')
                if masters.exists():
                    break
    else:
        return JsonResponse({'error': 'style_id or master_id required'}, status=400)
    out = [
        {
            'id': m.id,
            'name': m.full_name,
            'profession': m.get_profession_display(),
            'rating': str(m.rating),
            'experience_years': m.experience_years,
            'location': m.location,
            'price': str(m.default_price) if m.default_price is not None else None,
            'photo_url': m.photo.url if m.photo else None,
        }
        for m in masters
    ]
    return JsonResponse({'masters': out})


# Робочий день: 9:00–18:00, слоти по 1 годині
BOOKING_WORK_START = 9
BOOKING_WORK_END = 18
BOOKING_SLOT_MINUTES = 60


@require_GET
def booking_api_slots(request):
    """API: вільні слоты на обрану дату для обраного майстра."""
    master_id = request.GET.get('master_id')
    day = request.GET.get('date')  # YYYY-MM-DD
    if not master_id or not day:
        return JsonResponse({'error': 'master_id and date required'}, status=400)
    master = get_object_or_404(Master, pk=master_id)
    try:
        d = date.fromisoformat(day)
    except ValueError:
        return JsonResponse({'error': 'invalid date'}, status=400)
    today = date.today()
    if d < today:
        return JsonResponse({'slots': []})
    # Усі слоты дня
    if d == today:
        current_hour = datetime.now().hour
        all_slots = [
            f'{h:02d}:00' for h in range(BOOKING_WORK_START, BOOKING_WORK_END)
            if h > current_hour
        ]
    else:
        all_slots = [
            f'{h:02d}:00' for h in range(BOOKING_WORK_START, BOOKING_WORK_END)
        ]

    # Зайняті
    booked = list(
        Booking.objects.filter(
            master=master, date=d
        ).exclude(status='cancelled').values_list('time_slot', flat=True)
    )
    free = [s for s in all_slots if s not in booked]
    return JsonResponse({'slots': free})


@require_GET
def booking_api_dates(request):
    """API: список дат для календаря (наступні 14 днів)."""
    master_id = request.GET.get('master_id')
    if not master_id:
        return JsonResponse({'error': 'master_id required'}, status=400)
    today = date.today()
    dates = [today + timedelta(days=i) for i in range(14)]
    out = [d.isoformat() for d in dates]
    return JsonResponse({'dates': out})


@require_POST
def booking_create(request):
    """Створення запису: master_id, hairstyle_id, date, time_slot, client_name, client_phone."""
    master_id = request.POST.get('master_id')
    hairstyle_id = request.POST.get('hairstyle_id')
    day = request.POST.get('date')
    time_slot = request.POST.get('time_slot')
    client_name = (request.POST.get('client_name') or '').strip()
    client_phone = (request.POST.get('client_phone') or '').strip()
    client_chat_id = request.POST.get('client_chat_id')
    service_id = request.POST.get('service_id')
    
    # hairstyle_id is optional if service_id is provided
    if not all([master_id, day, time_slot, client_name, client_phone]) or (not hairstyle_id and not service_id):
        return JsonResponse({'success': False, 'error': 'Заповніть усі поля'}, status=400)
    
    master = get_object_or_404(Master, pk=master_id)
    hairstyle = None
    if hairstyle_id:
        hairstyle = get_object_or_404(Hairstyle, pk=hairstyle_id)
        if not master.specialties.filter(pk=hairstyle.pk).exists():
            return JsonResponse({'success': False, 'error': 'Обраний майстер не надає цю стрижку'}, status=400)
    try:
        d = date.fromisoformat(day)
    except ValueError:
        return JsonResponse({'success': False, 'error': 'Невірна дата'}, status=400)
        
    today = date.today()
    if d < today:
        return JsonResponse({'success': False, 'error': 'Обрана дата вже минула'}, status=400)
        
    # Check current day hours
    if d == today:
        current_hour = datetime.now().hour
        try:
            slot_hour = int(time_slot.split(':')[0])
            if slot_hour <= current_hour:
                return JsonResponse({'success': False, 'error': 'Цей час вже минув'}, status=400)
        except (ValueError, IndexError):
            pass

    # Перевірка, що слот вільний
    if Booking.objects.filter(master=master, date=d, time_slot=time_slot).exclude(status='cancelled').exists():
        return JsonResponse({'success': False, 'error': 'Цей час вже зайнятий'}, status=400)
    price = master.default_price
    from masters.models import Service
    service = None
    if service_id:
        service = Service.objects.filter(pk=service_id).first()

    booking = Booking.objects.create(
        master=master,
        service=service,
        hairstyle=hairstyle,
        client_name=client_name,
        client_phone=client_phone,
        date=d,
        time_slot=time_slot,
        price=price,
        status='pending',
        client_chat_id=client_chat_id if client_chat_id else None,
    )
    
    # --- Повідомлення барберу ---
    barber_message = f"""💈 У вас новий запис!

👤 Клієнт: {client_name}
📞 Телефон: {client_phone}
✂️ Послуга: {service.name if service else (hairstyle.name if hairstyle else "Стрижка")}
📅 Дата: {d.strftime("%d.%m.%Y")}
⏰ Час: {time_slot}
💰 Ціна: {price} грн
"""
    send_telegram_message_to_barber(master, barber_message)

    # --- Повідомлення клієнту ---
    if client_chat_id:
        service_name = service.name if service else (hairstyle.name if hairstyle else "Стрижка")
        client_message = f"""✅ Твій запис підтверджено!

💈 Майстер: {master.full_name}
✂️ Послуга: {service_name}
📅 Дата: {d.strftime("%d.%m.%Y")}
⏰ Час: {time_slot}
"""
        send_telegram_message_to_client(client_chat_id, client_message)
    
    # --- Повідомлення адміністратору (власнику / групі барберів) ---
    admin_message = f"""💈 У вас новий запис!
    
👤 Клієнт: {client_name}
📞 Телефон: {client_phone}
✂️ Послуга: {service.name if service else (hairstyle.name if hairstyle else "Стрижка")}
📅 Дата: {d.strftime("%d.%m.%Y")}
⏰ Час: {time_slot}
💰 Ціна: {price} грн
"""
    send_telegram_notification_to_admin(admin_message)

    msg = f'Запис створено. {master.full_name} очікує вас {d.strftime("%d.%m.%Y")} о {time_slot}.'
    if service:
        msg = f'Запис на {service.name.lower()} до майстра {master.full_name} створено на {d.strftime("%d.%m.%Y")} о {time_slot}.'

    return JsonResponse({
        'success': True,
        'booking_id': booking.id,
        'message': msg,
    })