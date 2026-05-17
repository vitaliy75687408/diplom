"""
Management command: assign_master_photos
Запуск: python manage.py assign_master_photos
"""

from django.core.management.base import BaseCommand
from masters.models import Master


PHOTO_MAP = {
    ('Олександр', 'Коваленко'):  'oleksandr_kovalchuk.png',
    ('Максим',    'Ткаченко'):   'master2.jpg',
    ('Ігор',      'Мельник'):    'home_team_107.jpg',
    ('Катерина',  'Кравченко'):  'avatar_woman_8xQkcdd.png',
    ('Дмитро',    'Шевченко'):   'master3.jpg',
    ('Артем',     'Мороз'):      'home_team_105.jpg',
    ('Роман',     'Федоренко'):  'home_team_122.jpg',
    ('Віталій',   'Гриценко'):   'home_team_123.jpg',
    ('Анна',      'Шевчук'):     'home_team_130.jpg',
    ('Юрій',      'Лисенко'):    'home_team_138.jpg',
    ('Андрій',    'Бондаренко'): 'andriy_oliynyk.png',
    ('Назар',     'Тарасенко'):  'andriy_tkachenko.png',
    ('Станіслав', 'Козак'):      'denys_tkachenko.png',
    ('Олександр', 'Олійник'):    'oleksandr_oliynyk.png',
    ('Андрій',    'Олійник'):    'master5.jpg',
    ('Андрій',    'Ткаченко'):   'work_105.jpg',
    ('Денис',     'Ткаченко'):   'work_106.jpg',
}


class Command(BaseCommand):
    help = 'Призначає фото майстрам з папки media/masters/'

    def handle(self, *args, **kwargs):
        updated = 0
        skipped = 0

        for (first_name, last_name), filename in PHOTO_MAP.items():
            try:
                master = Master.objects.get(
                    first_name=first_name,
                    last_name=last_name
                )
                master.photo = f'masters/{filename}'
                master.save(update_fields=['photo'])
                self.stdout.write(
                    self.style.SUCCESS(f'✅ {first_name} {last_name} → {filename}')
                )
                updated += 1
            except Master.DoesNotExist:
                self.stdout.write(
                    self.style.WARNING(f'⚠️  Майстра не знайдено: {first_name} {last_name}')
                )
                skipped += 1
            except Master.MultipleObjectsReturned:
                self.stdout.write(
                    self.style.WARNING(f'⚠️  Кілька майстрів: {first_name} {last_name} — пропускаємо')
                )
                skipped += 1

        self.stdout.write('')
        self.stdout.write(f'Готово: оновлено {updated}, пропущено {skipped}')