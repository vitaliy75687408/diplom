"""
Скрипт: додає ВСІ зачіски (популярні + чоловічі + жіночі) в БД.
Запускати: python seed_hairstyles.py
"""
import os, sys, django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'styleai_project.settings')
sys.path.insert(0, os.path.dirname(__file__))
django.setup()

from hairstyles.models import Hairstyle

# ── Всі зачіски що мають бути в БД ────────────────────────────────────────────
HAIRSTYLES = [
    # Популярні чоловічі
    ('Drop Fade',      'men',   'Фейд із опущенням лінії по потилиці.'),
    ('Taper Fade',     'men',   'Тейпер із плавним переходом по краях.'),
    ('Low Fade',       'men',   'Низький фейд від вух.'),
    ('Mid Fade',       'men',   'Середній фейд по всьому периметру.'),
    ('High Fade',      'men',   'Високий фейд.'),
    ('Skin Fade',      'men',   'Фейд до шкіри.'),
    ('Textured Crop',  'men',   'Короткий кроп з текстурою зверху.'),
    ('Burst Fade',     'men',   "Фейд із об'ємом над вухами."),
    ('Edgar Cut',      'men',   'Короткі боки, чубчик уперед і вгору.'),
    ('Slick Back',     'men',   'Волосся зачесане назад з фіксацією.'),
    ('Pompadour',      'men',   "Об'ємна стрижка з високим верхом."),
    ('Quiff',          'men',   'Зачіска з піднятим чубчиком.'),
    ('Mod Cut',        'men',   'Сучасна стрижка середньої довжини з чіткими лініями.'),
    ('Brush Up Fade',  'men',   'Волосся підняте вгору.'),
    ('Undercut',       'men',   'Короткі боки та довгий верх.'),
    ('Faux Hawk',      'men',   'Штучний ірокез.'),
    ('Crew Cut',       'men',   'Коротка класична стрижка.'),
    ('Buzz Cut',       'men',   'Дуже коротка стрижка під машинку.'),
    # Популярні жіночі/унісекс
    ('Long Wavy Hair', 'women', 'Довге хвилясте волосся.'),
    ('Bob',            'women', 'Класичне каре.'),
    ('Pixie Cut',      'women', 'Коротка текстурована стрижка.'),
    ('Каре',           'women', 'Класична стрижка з рівним зрізом.'),
    ('Кучерявий Боб',  'women', 'Короткий боб для хвилястого або кучерявого волосся.'),
    ('Піксі',          'women', 'Коротка і смілива стрижка з текстурованими пасмами.'),
    ('Гарсон',         'women', 'Елегантна коротка стрижка.'),
    ('Сесон',          'women', 'Вінтажна стрижка з плавним переходом.'),
    ('Їжачок',         'women', 'Ультракоротка стрижка.'),
    ('Шеггі',          'women', 'Рвана стрижка з недбалими пасмами.'),
    # Додаткові жіночі
    ('Long Layered Cut',   'women', "Довге волосся з каскадними шарами для об'єму та руху."),
    ('Butterfly Cut',      'women', 'Романтична багатошарова стрижка, що нагадує крила метелика.'),
    ('Romance Waves',      'women', "М'які хвилі, що надають образу романтичності та легкості."),
    ('Baroque Bob',        'women', "Вишуканий боб із об'ємними завитками у стилі бароко."),
    ('Microwave Curls',    'women', 'Дрібні рівні кучері по всій довжині волосся.'),
    ('Soft Curtain Bangs', 'women', "М'який чубчик із розділом посередині, що обрамляє обличчя."),
    ('Sleek Low Pony',     'women', 'Гладкий низький хвіст — елегантно й лаконічно.'),
    ('Shaggy Lob',         'women', 'Подовжений боб із рваними шарами та легкою текстурою.'),
    ('Bixie Cut',          'women', 'Гібрид боба та піксі: коротко, але з характером.'),
    ('Cowgirl Cut',        'women', 'Вільні довгі хвилі з легкою текстурою в стилі кантрі.'),
    ('Wolf Cut',           'women', "Дика й сексуальна стрижка з об'ємними шарами та рваними кінчиками."),
    ('Curtain Bangs Lob',  'women', 'Подовжений боб із чубчиком-фіранкою, що обрамляє обличчя.'),
    ('French Bob',         'women', 'Короткий паризький боб з прямим чубчиком.'),
    ('Feathered Layers',   'women', "Довге волосся з легкими пір'їстими шарами."),
    ('Wispy Bangs',        'women', "Ніжний тонкий чубчик — витончено й по-жіночому."),
    # Додаткові чоловічі
    ('Caesar Cut',             'men', 'Коротка пряма стрижка з горизонтальним чубчиком вперед.'),
    ('Ivy League',             'men', 'Елегантна академічна стрижка з невеликим чубчиком.'),
    ('Side Part',              'men', 'Класичний проділ збоку — завжди стильно й доречно.'),
    ('Hard Part',              'men', 'Чіткий виголений проділ для максимальної чіткості.'),
    ('Disconnected Undercut',  'men', "Різкий контраст між довгим верхом та виголеними боками."),
    ('Mohawk Fade',            'men', 'Ірокез із фейдом по боках — сміливо та стильно.'),
    ('Comb Over Fade',         'men', "Зачесане волосся з плавним фейдом по боках."),
    ('Mullet',                 'men', 'Коротко спереду — довго ззаду. Культовий ретро-стиль.'),
    ('Shaggy Medium',          'men', "Середньої довжини з рваними шарами та недбалою текстурою."),
    ('Messy Bun',              'men', 'Недбало зібраний пучок — casual і стильно.'),
    ('Man Bun',                'men', 'Акуратний чоловічий пучок для довгого волосся.'),
    ('Curtains Hairstyle',     'men', 'Розчесане на дві сторони волосся посередині — стиль 90-х.'),
    ('French Crop',            'men', 'Коротка стрижка з коротким чубчиком та фейдом.'),
    ('Bro Flow',               'men', 'Природне хвилясте волосся середньої довжини.'),
]

created = updated = skipped = 0

for name, category, description in HAIRSTYLES:
    hs, created_flag = Hairstyle.objects.get_or_create(
        name=name,
        defaults={'category': category, 'description': description, 'master_count': 0}
    )
    if created_flag:
        created += 1
        print(f'  ✅ Створено: {name} [{category}]')
    else:
        changed = False
        if hs.category != category:
            hs.category = category
            changed = True
        if not hs.description:
            hs.description = description
            changed = True
        if changed:
            hs.save()
            updated += 1
            print(f'  🔄 Оновлено: {name} [{category}]')
        else:
            skipped += 1
            print(f'  ·  Є:      {name}')

print(f'\n✨ Готово! Створено: {created}, оновлено: {updated}, вже було: {skipped}')
print(f'   Всього зачісок у БД: {Hairstyle.objects.count()}')

# Перевірка — виводимо чоловічі
men = list(Hairstyle.objects.filter(category='men').values_list('name', flat=True).order_by('name'))
print(f'\nЧоловічих зачісок в БД ({len(men)}):')
for n in men:
    print(f'   • {n}')
