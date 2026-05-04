"""
Management command: додає ВСІ додаткові зачіски в базу даних.
Ці зачіски НЕ показуються у блоці «Популярні зачіски» на головній,
але доступні для AI-рекомендацій.
"""
from django.core.management.base import BaseCommand
from hairstyles.models import Hairstyle
from styleai.constants import (
    EXTRA_WOMEN_HAIRSTYLE_NAMES, EXTRA_WOMEN_STYLE_DESCRIPTIONS,
    EXTRA_MEN_HAIRSTYLE_NAMES, EXTRA_MEN_STYLE_DESCRIPTIONS,
)

EXTRA_WOMEN_UNSPLASH = {
    'Long Layered Cut':    'https://images.unsplash.com/photo-1519699047748-de8e457a634e?w=400&q=80',
    'Butterfly Cut':       'https://images.unsplash.com/photo-1522337360788-8b13dee7a37e?w=400&q=80',
    'Romance Waves':       'https://images.unsplash.com/photo-1531746020798-e6953c6e8e04?w=400&q=80',
    'Baroque Bob':         'https://images.unsplash.com/photo-1580618672591-eb180b1a973f?w=400&q=80',
    'Microwave Curls':     'https://images.unsplash.com/photo-1560066984-138dadb4c035?w=400&q=80',
    'Soft Curtain Bangs':  'https://images.unsplash.com/photo-1595476108010-b4d1f10cf074?w=400&q=80',
    'Sleek Low Pony':      'https://images.unsplash.com/photo-1620331311520-246422fd82f9?w=400&q=80',
    'Shaggy Lob':          'https://images.unsplash.com/photo-1551150441-3f3828204ef0?w=400&q=80',
    'Bixie Cut':           'https://images.unsplash.com/photo-1532053913054-04df84fce07f?w=400&q=80',
    'Cowgirl Cut':         'https://images.unsplash.com/photo-1518144591331-17a5dd71c477?w=400&q=80',
    'Wolf Cut':            'https://images.unsplash.com/photo-1522337360788-8b13dee7a37e?w=400&q=80',
    'Curtain Bangs Lob':   'https://images.unsplash.com/photo-1595476108010-b4d1f10cf074?w=400&q=80',
    'French Bob':          'https://images.unsplash.com/photo-1551150441-3f3828204ef0?w=400&q=80',
    'Feathered Layers':    'https://images.unsplash.com/photo-1519699047748-de8e457a634e?w=400&q=80',
    'Wispy Bangs':         'https://images.unsplash.com/photo-1531746020798-e6953c6e8e04?w=400&q=80',
}

EXTRA_MEN_UNSPLASH = {
    'Caesar Cut':             'https://images.unsplash.com/photo-1585747860715-2ba37e788b70?w=400&q=80',
    'Ivy League':             'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=400&q=80',
    'Side Part':              'https://images.unsplash.com/photo-1503951914875-452162b0f3f1?w=400&q=80',
    'Hard Part':              'https://images.unsplash.com/photo-1605497788044-5a32c7078486?w=400&q=80',
    'Disconnected Undercut':  'https://images.unsplash.com/photo-1605497787865-e6d4002621ab?w=400&q=80',
    'Mohawk Fade':            'https://images.unsplash.com/photo-1492106087820-71f1a00d2b11?w=400&q=80',
    'Comb Over Fade':         'https://images.unsplash.com/photo-1621605815971-fdf98ee3a1ff?w=400&q=80',
    'Mullet':                 'https://images.unsplash.com/photo-1599351431202-1e0f0137899a?w=400&q=80',
    'Shaggy Medium':          'https://images.unsplash.com/photo-1560066984-138dadb4c035?w=400&q=80',
    'Messy Bun':              'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=400&q=80',
    'Man Bun':                'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=400&q=80',
    'Curtains Hairstyle':     'https://images.unsplash.com/photo-1503951914875-452162b0f3f1?w=400&q=80',
    'French Crop':            'https://images.unsplash.com/photo-1585747860715-2ba37e788b70?w=400&q=80',
    'Bro Flow':               'https://images.unsplash.com/photo-1518144591331-17a5dd71c477?w=400&q=80',
}


class Command(BaseCommand):
    help = 'Додає всі додаткові зачіски у БД (не показуються в «Популярних», доступні для рекомендацій).'

    def handle(self, *args, **kwargs):
        created_total = 0
        updated_total = 0

        # ── Жіночі ──
        self.stdout.write('\n📌 Жіночі зачіски:')
        for name in EXTRA_WOMEN_HAIRSTYLE_NAMES:
            desc = EXTRA_WOMEN_STYLE_DESCRIPTIONS.get(name, '')
            hs, created = Hairstyle.objects.get_or_create(
                name=name,
                defaults={'description': desc, 'category': 'women', 'master_count': 0}
            )
            changed = False
            if not hs.description and desc:
                hs.description = desc; changed = True
            if hs.category != 'women':
                hs.category = 'women'; changed = True
            if changed:
                hs.save(); updated_total += 1
            if created:
                created_total += 1
                self.stdout.write(f'  ✅ Створено: {name}')
            else:
                self.stdout.write(f'  ℹ️  Вже існує: {name}')

        # ── Чоловічі ──
        self.stdout.write('\n📌 Чоловічі зачіски:')
        for name in EXTRA_MEN_HAIRSTYLE_NAMES:
            desc = EXTRA_MEN_STYLE_DESCRIPTIONS.get(name, '')
            hs, created = Hairstyle.objects.get_or_create(
                name=name,
                defaults={'description': desc, 'category': 'men', 'master_count': 0}
            )
            changed = False
            if not hs.description and desc:
                hs.description = desc; changed = True
            if hs.category != 'men':
                hs.category = 'men'; changed = True
            if changed:
                hs.save(); updated_total += 1
            if created:
                created_total += 1
                self.stdout.write(f'  ✅ Створено: {name}')
            else:
                self.stdout.write(f'  ℹ️  Вже існує: {name}')

        self.stdout.write(
            self.style.SUCCESS(
                f'\n✨ Готово! Створено: {created_total}, оновлено: {updated_total} зачісок.'
            )
        )
        self.stdout.write(
            'Ці зачіски НЕ відображаються у блоці «Популярні зачіски», '
            'але система рекомендацій пропонуватиме їх користувачам.\n'
        )
