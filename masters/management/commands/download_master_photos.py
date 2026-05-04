# -*- coding: utf-8 -*-
"""
Завантажує фото всіх майстрів з інтернету (Unsplash) і зберігає в Master.photo.

Запуск: python manage.py download_master_photos
Опція --force: перезаписати фото навіть якщо воно вже є.
"""
import io
import urllib.request
from pathlib import Path

from django.core.management.base import BaseCommand
from django.core.files import File
from django.conf import settings

from masters.models import Master


# Якісні професійні портрети (барбери/стилісти) — w=600, q=90 для чітких фото.
# Чоловіки: студийні портрети, охайний вигляд, різні обличчя.
_MALE_URLS = [
    "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=600&q=90",   # чол., коротка стрижка, професійний
    "https://images.unsplash.com/photo-1500648767791-1baa11a42f8c?w=600&q=90",   # чол., усміхнений
    "https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?w=600&q=90",   # чол., борода, стильний
    "https://images.unsplash.com/photo-1506794778202-cad84cf45f1d?w=600&q=90",   # чол., світлий фон
    "https://images.unsplash.com/photo-1585747860715-2ba37e788b70?w=600&q=90",   # чол., діловий вигляд
    "https://images.unsplash.com/photo-1507591064344-4c6ce005b128?w=600&q=90",   # чол., охайна зачіска
    "https://images.unsplash.com/photo-1539571696357-5a69c17a67c6?w=600&q=90",   # чол., барбер-стиль
    "https://images.unsplash.com/photo-1492106087820-71f1a00d2b11?w=600&q=90",   # чол., класичний портрет
    "https://images.unsplash.com/photo-1503951914875-452162b0f3f1?w=600&q=90",   # чол., стильна стрижка
    "https://images.unsplash.com/photo-1506794778202-cad84cf45f1d?w=600&q=90",   # чол., нейтральний фон
    "https://images.unsplash.com/photo-1500648767791-1baa11a42f8c?w=600&q=90",   # чол., портрет
]
# Жінки: професійні портрети стилістів/колористів, гарне освітлення.
_FEMALE_URLS = [
    "https://images.unsplash.com/photo-1544005313-94ddf0286df2?w=600&q=90",   # жін., світле волосся
    "https://images.unsplash.com/photo-1522337360788-8b13dee7a37e?w=600&q=90", # жін., професійний вигляд
    "https://images.unsplash.com/photo-1580489944761-15a19d654956?w=600&q=90", # жін., руде волосся
    "https://images.unsplash.com/photo-1517841905240-472988babdf9?w=600&q=90", # жін., усміхнена
    "https://images.unsplash.com/photo-1560066984-138dadb4c035?w=600&q=90",   # жін., темне волосся
    "https://images.unsplash.com/photo-1547425260-abc76f5bddf5?w=600&q=90",   # жін., елегантна
    "https://images.unsplash.com/photo-1573496350642-e2b252859cdc?w=600&q=90", # жін., діловий стиль
    "https://images.unsplash.com/photo-1438761681033-6461ffad8d80?w=600&q=90", # жін., натуральний вигляд
    "https://images.unsplash.com/photo-1438761681033-6461ffad8d80?w=600&q=90", # жін., портрет
    "https://images.unsplash.com/photo-1494790108377-be9c29b29330?w=600&q=90", # жін., руда, яскрава
]
# Прив'язка за іменем: кожен майстер — унікальне фото (чол. / жін. за іменем).
PHOTO_URL_BY_FIRST_NAME = {
    "Олександр": _MALE_URLS[0],
    "Марія": _FEMALE_URLS[0],
    "Дмитро": _MALE_URLS[1],
    "Андрій": _MALE_URLS[2],
    "Олена": _FEMALE_URLS[1],
    "Ігор": _MALE_URLS[3],
    "Віталій": _MALE_URLS[4],
    "Тетяна": _FEMALE_URLS[2],
    "Вадим": _MALE_URLS[5],
    "Наталія": _FEMALE_URLS[3],
    "Сергій": _MALE_URLS[0],   # примусово чоловіче фото (барбер)
    "Катерина": _FEMALE_URLS[4],
    "Максим": _MALE_URLS[7],
    "Юлія": _FEMALE_URLS[5],
    "Анна": _FEMALE_URLS[6],
    "Олег": _MALE_URLS[8],
    "Роман": _MALE_URLS[1],   # примусово чоловіче фото (барбер)
    "Ірина": _FEMALE_URLS[7],
    "Софія": _FEMALE_URLS[8],
    "Артем": _MALE_URLS[10],
}
# Запасні (теж якісні портрети)
FALLBACK_MALE_POOL = [
    "https://images.unsplash.com/photo-1506794778202-cad84cf45f1d?w=600&q=90",
    "https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?w=600&q=90",
    "https://images.unsplash.com/photo-1539571696357-5a69c17a67c6?w=600&q=90",
]
FALLBACK_FEMALE_POOL = [
    "https://images.unsplash.com/photo-1547425260-abc76f5bddf5?w=600&q=90",
    "https://images.unsplash.com/photo-1573496350642-e2b252859cdc?w=600&q=90",
    "https://images.unsplash.com/photo-1580489944761-15a19d654956?w=600&q=90",
    "https://images.unsplash.com/photo-1517841905240-472988babdf9?w=600&q=90",
]


class Command(BaseCommand):
    help = "Завантажує фото майстрів з інтернету (Unsplash) і зберігає в Master.photo"

    def add_arguments(self, parser):
        parser.add_argument(
            "--force",
            action="store_true",
            help="Перезаписати фото навіть якщо воно вже є",
        )

    def handle(self, *args, **options):
        force = options["force"]
        masters = Master.objects.all()
        if not masters.exists():
            self.stdout.write(self.style.WARNING("У базі немає майстрів."))
            return

        count = 0
        used_urls = set()
        male_fallback_idx = [0]  # mutable so we can advance
        female_fallback_idx = [0]

        male_only_urls = set(_MALE_URLS + FALLBACK_MALE_POOL)
        female_only_urls = set(_FEMALE_URLS + FALLBACK_FEMALE_POOL)

        for master in masters:
            if master.photo and not force:
                self.stdout.write(f"  Пропущено (вже є фото): {master.full_name}")
                continue

            # Барбери — тільки чоловічі фото. Стилісти/колористи — за іменем або за статтю.
            is_barber = master.profession == "barber"
            url = PHOTO_URL_BY_FIRST_NAME.get(master.first_name)
            if is_barber and url and url in female_only_urls:
                url = None  # барберу не даємо жіноче фото
            if not url:
                if is_barber or master.profession != "colorist":
                    pool = FALLBACK_MALE_POOL
                    idx = male_fallback_idx[0]
                    url = pool[idx % len(pool)]
                    male_fallback_idx[0] += 1
                else:
                    pool = FALLBACK_FEMALE_POOL
                    idx = female_fallback_idx[0]
                    url = pool[idx % len(pool)]
                    female_fallback_idx[0] += 1
            # Якщо це фото вже призначено — беремо інше з потрібного пулу (для барбера тільки чол.)
            if url in used_urls:
                search_pool = list(_MALE_URLS + FALLBACK_MALE_POOL) if is_barber else list(_MALE_URLS + _FEMALE_URLS + FALLBACK_MALE_POOL + FALLBACK_FEMALE_POOL)
                for u in search_pool:
                    if u not in used_urls:
                        if is_barber and u not in male_only_urls:
                            continue
                        url = u
                        break
            used_urls.add(url)

            data = None
            try:
                req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (compatible; StyleAI/1.0)"})
                with urllib.request.urlopen(req, timeout=15) as resp:
                    data = resp.read()
            except Exception as e:
                if is_barber:
                    for fallback_url in _MALE_URLS + FALLBACK_MALE_POOL:
                        if fallback_url in used_urls:
                            continue
                        try:
                            req = urllib.request.Request(fallback_url, headers={"User-Agent": "Mozilla/5.0 (compatible; StyleAI/1.0)"})
                            with urllib.request.urlopen(req, timeout=15) as resp:
                                data = resp.read()
                                url = fallback_url
                                used_urls.add(fallback_url)
                                break
                        except Exception:
                            pass
                if data is None:
                    self.stdout.write(self.style.ERROR(f"  Помилка завантаження для {master.full_name}: {e}"))
                    continue

            if not data:
                self.stdout.write(self.style.ERROR(f"  Порожня відповідь для {master.full_name}"))
                continue

            ext = ".jpg"
            if b"png" in data[:50].lower():
                ext = ".png"
            safe_name = "".join(c for c in master.first_name if c.isalnum() or c in " _-") or "master"
            filename = f"{safe_name}_{master.id}{ext}"

            try:
                if master.photo:
                    master.photo.delete(save=False)
                master.photo.save(filename, File(io.BytesIO(data)), save=True)
                count += 1
                self.stdout.write(self.style.SUCCESS(f"  OK: {master.full_name}"))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"  Помилка збереження для {master.full_name}: {e}"))

        self.stdout.write(self.style.SUCCESS(f"Готово. Фото оновлено для {count} майстрів."))
