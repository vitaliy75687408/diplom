"""
Data migration: примусово додає зачіски до ВСІХ майстрів.
Використовує add() замість set(), тому існуючі спеціальності не видаляються.
"""
from django.db import migrations

MEN_HAIRSTYLE_NAMES = [
    'Drop Fade', 'Taper Fade', 'Low Fade', 'Mid Fade', 'High Fade', 'Skin Fade',
    'Textured Crop', 'Burst Fade', 'Edgar Cut', 'Slick Back', 'Pompadour', 'Quiff',
    'Mod Cut', 'Brush Up Fade', 'Undercut', 'Faux Hawk', 'Crew Cut', 'Buzz Cut',
]

WOMEN_HAIRSTYLE_NAMES = [
    'Long Wavy Hair', 'Bob', 'Pixie Cut',
    'Каре', 'Кучерявий Боб', 'Піксі', 'Гарсон', 'Сесон', 'Їжачок', 'Шеггі',
]

ALL_POPULAR = MEN_HAIRSTYLE_NAMES + WOMEN_HAIRSTYLE_NAMES


def force_assign_specialties(apps, schema_editor):
    Master = apps.get_model('masters', 'Master')
    Hairstyle = apps.get_model('hairstyles', 'Hairstyle')

    # Завантажуємо всі зачіски одним запитом
    men_styles   = list(Hairstyle.objects.filter(name__in=MEN_HAIRSTYLE_NAMES))
    women_styles = list(Hairstyle.objects.filter(name__in=WOMEN_HAIRSTYLE_NAMES))
    all_styles   = list(Hairstyle.objects.filter(name__in=ALL_POPULAR))

    print(f'\n  Чоловічих зачісок знайдено: {len(men_styles)}')
    print(f'  Жіночих зачісок знайдено: {len(women_styles)}')

    for master in Master.objects.all():
        if master.profession == 'barber':
            styles = men_styles
        elif master.profession == 'stylist':
            styles = women_styles
        elif master.profession == 'colorist':
            styles = all_styles
        else:
            styles = all_styles

        # add() — додає лише відсутні, не видаляє існуючі
        master.specialties.add(*styles)
        print(f'  ✓ {master.first_name} {master.last_name} [{master.profession}]: +{len(styles)} зачісок')

    print(f'\n  [migration 0015] Готово.')


def noop(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('masters', '0014_assign_hairstyle_specialties'),
        ('hairstyles', '0004_seed_hairstyles'),
    ]

    operations = [
        migrations.RunPython(force_assign_specialties, noop),
    ]
