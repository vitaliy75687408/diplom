# -*- coding: utf-8 -*-
"""
Після того як ви поклали фото в папку incoming_master_photos/,
запустіть:  python manage.py assign_master_photos
Фото будуть прив’язані до майстрів за іменем файлу (див. README в папці).
"""
from django.core.management.base import BaseCommand
from django.core.files import File
from django.conf import settings
from pathlib import Path
from masters.models import Master

# назва файлу (без розширення, латиницею) → ім'я майстра в базі
FILE_NAME_TO_FIRST_NAME = {
    "igor": "Ігор",
    "vitaliy": "Віталій",
    "maria": "Марія",
    "tetyana": "Тетяна",
    "vadym": "Вадим",
    "oleksandr": "Олександр",
    "dmytro": "Дмитро",
    "andriy": "Андрій",
    "olena": "Олена",
    "nataliya": "Наталія",
    "natalia": "Наталія",
    "serhiy": "Сергій",
    "kateryna": "Катерина",
    "maksym": "Максим",
    "yuliya": "Юлія",
    "anna": "Анна",
    "oleh": "Олег",
    "roman": "Роман",
    "irina": "Ірина",
    "sofiya": "Софія",
    "artem": "Артем",
}

ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}


class Command(BaseCommand):
    help = "Прив’язує фото з папки incoming_master_photos до майстрів за іменем файлу"

    def handle(self, *args, **options):
        base_dir = Path(settings.BASE_DIR)
        incoming = base_dir / "incoming_master_photos"
        if not incoming.exists():
            self.stdout.write(
                self.style.WARNING(
                    f"Папки {incoming} немає. Створіть її і покладіть туди фото (див. README.txt)."
                )
            )
            return

        count = 0
        for path in sorted(incoming.iterdir()):
            if not path.is_file() or path.suffix.lower() not in ALLOWED_EXTENSIONS:
                continue
            stem = path.stem.lower().strip()
            first_name = FILE_NAME_TO_FIRST_NAME.get(stem)
            if not first_name:
                self.stdout.write(
                    self.style.WARNING(f"  Пропущено (невідоме ім'я): {path.name}")
                )
                continue

            master = Master.objects.filter(first_name=first_name).first()
            if not master:
                self.stdout.write(
                    self.style.WARNING(
                        f"  Майстра з ім'ям «{first_name}» немає в базі: {path.name}"
                    )
                )
                continue

            try:
                with open(path, "rb") as f:
                    name = f"master_{stem}{path.suffix.lower()}"
                    master.photo.save(name, File(f), save=True)
                count += 1
                self.stdout.write(
                    self.style.SUCCESS(f"  OK: {master.full_name} ← {path.name}")
                )
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f"  Помилка для {path.name}: {e}")
                )

        if count:
            self.stdout.write(
                self.style.SUCCESS(f"Готово. Фото прив’язано для {count} майстрів.")
            )
        else:
            self.stdout.write(
                "Нічого не змінено. Покладіть у папку фото з правильними назвами (див. README)."
            )
