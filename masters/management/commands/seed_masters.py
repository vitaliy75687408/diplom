from django.core.management.base import BaseCommand
import os
import django
from django.core.files.base import ContentFile

# This command should be run with Django context: python manage.py seed_masters

class Command(BaseCommand):
    help = 'Seed sample masters with photos (hardcoded).'

    def handle(self, *args, **options):
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'styleai_project.settings')
        import sys
        sys.path.insert(0, os.getcwd())
        django.setup()

        from masters.models import Master
        from masters.models import MasterPhoto

        media_dir = os.path.join(os.getcwd(), 'media', 'masters')
        static_dir = os.path.join(os.getcwd(), 'static', 'images')

        SAMPLE_MASTERS = [
            # (first, last, profession, city, district, experience, rating, photo_filename)
            ('Іван', 'Петренко', 'barber', 'Kyiv', '', 5, 4.8, 'avatar_man1.png'),
            ('Віталій', 'Коваль', 'barber', 'Lviv', '', 7, 4.9, 'avatar_man2.png'),
            ('Марія', 'Шевченко', 'stylist', 'Kyiv', '', 4, 4.7, 'avatar_woman.png'),
            ('Олександр', 'Гончар', 'barber', 'Odesa', '', 6, 4.6, 'avatar_man1.png'),
            ('Тетяна', 'Климчук', 'colorist', 'Lviv', '', 3, 4.5, 'avatar_woman.png'),
        ]

        created = 0
        updated = 0

        for first, last, profession, city, district, exp, rating, photo_name in SAMPLE_MASTERS:
            full_name = f"{first} {last}"
            m, created_flag = Master.objects.get_or_create(first_name=first, last_name=last,
                                                           defaults={'profession': profession,
                                                                     'experience_years': exp,
                                                                     'city': city,
                                                                     'district': district,
                                                                     'rating': rating})
            if created_flag:
                created += 1
                self.stdout.write(f"Created master: {full_name}")
            else:
                updated += 1
                self.stdout.write(f"Found existing: {full_name}")

            # attach photo if none
            if not m.photo:
                # prefer files from media/masters, else static/avatar
                media_path = os.path.join(media_dir, photo_name)
                if os.path.exists(media_path):
                    with open(media_path, 'rb') as f:
                        data = f.read()
                        m.photo.save(photo_name, ContentFile(data), save=True)
                        self.stdout.write(f"  -> Saved photo from media: {photo_name}")
                else:
                    static_path = os.path.join(static_dir, photo_name)
                    if os.path.exists(static_path):
                        with open(static_path, 'rb') as f:
                            data = f.read()
                            m.photo.save(photo_name, ContentFile(data), save=True)
                            self.stdout.write(f"  -> Saved photo from static: {photo_name}")
                    else:
                        self.stdout.write(f"  -> No photo found for {full_name}; leaving blank")

            # add one gallery photo if none
            if m.gallery_photos.count() == 0:
                # try to reuse main photo
                if m.photo:
                    mp = MasterPhoto(master=m)
                    mp.image.save(f"gallery_{m.id}_{photo_name}", ContentFile(m.photo.read()), save=True)
                    self.stdout.write(f"  -> Added gallery photo for {full_name}")

        self.stdout.write(self.style.SUCCESS(f"Done. Created: {created}, existing: {updated}"))
