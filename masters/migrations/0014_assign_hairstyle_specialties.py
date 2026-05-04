"""
Data migration: прив'язує всіх існуючих майстрів до популярних зачісок.
- Барбери → чоловічі зачіски
- Стилісти → жіночі + унісекс зачіски
- Колористи → всі зачіски
- Якщо profession не задано → всі популярні зачіски
"""
from django.db import migrations

# Розподіл зачісок по типу майстра
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


def assign_specialties(apps, schema_editor):
    Master = apps.get_model('masters', 'Master')
    Hairstyle = apps.get_model('hairstyles', 'Hairstyle')

    men_styles = list(Hairstyle.objects.filter(name__in=MEN_HAIRSTYLE_NAMES))
    women_styles = list(Hairstyle.objects.filter(name__in=WOMEN_HAIRSTYLE_NAMES))
    all_styles = list(Hairstyle.objects.filter(name__in=ALL_POPULAR))

    assigned = 0
    for master in Master.objects.all():
        # Якщо у майстра вже є спеціалізації — не чіпаємо
        if master.specialties.exists():
            continue

        if master.profession == 'barber':
            styles = men_styles
        elif master.profession == 'stylist':
            styles = women_styles
        elif master.profession == 'colorist':
            styles = all_styles
        else:
            styles = all_styles

        master.specialties.set(styles)
        assigned += 1
        print(f'  → {master.first_name} {master.last_name} [{master.profession}]: {len(styles)} зачісок')

    print(f'\n  [migration] Прив\'язано зачіски до {assigned} майстрів.')


def unassign_specialties(apps, schema_editor):
    pass  # не скасовуємо при rollback


class Migration(migrations.Migration):

    dependencies = [
        ('masters', '0013_master_level'),
        ('hairstyles', '0004_seed_hairstyles'),
    ]

    operations = [
        migrations.RunPython(assign_specialties, unassign_specialties),
    ]
