"""
Скрипт прямого запису зачісок у SQLite БД без запуску Django.
Запускати: python direct_seed_db.py
"""
import sqlite3
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), 'db.sqlite3')

HAIRSTYLES = [
    # (name, category, description)
    # ── Популярні чоловічі ────────────────────────────────────────────────────
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
    # ── Популярні жіночі ─────────────────────────────────────────────────────
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
    # ── Додаткові жіночі ─────────────────────────────────────────────────────
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
    # ── Додаткові чоловічі ───────────────────────────────────────────────────
    ('Caesar Cut',            'men', 'Коротка пряма стрижка з горизонтальним чубчиком вперед.'),
    ('Ivy League',            'men', 'Елегантна академічна стрижка з невеликим чубчиком.'),
    ('Side Part',             'men', 'Класичний проділ збоку — завжди стильно й доречно.'),
    ('Hard Part',             'men', 'Чіткий виголений проділ для максимальної чіткості.'),
    ('Disconnected Undercut', 'men', "Різкий контраст між довгим верхом та виголеними боками."),
    ('Mohawk Fade',           'men', 'Ірокез із фейдом по боках — сміливо та стильно.'),
    ('Comb Over Fade',        'men', "Зачесане волосся з плавним фейдом по боках."),
    ('Mullet',                'men', 'Коротко спереду — довго ззаду. Культовий ретро-стиль.'),
    ('Shaggy Medium',         'men', "Середньої довжини з рваними шарами та недбалою текстурою."),
    ('Messy Bun',             'men', 'Недбало зібраний пучок — casual і стильно.'),
    ('Man Bun',               'men', 'Акуратний чоловічий пучок для довгого волосся.'),
    ('Curtains Hairstyle',    'men', 'Розчесане на дві сторони волосся посередині — стиль 90-х.'),
    ('French Crop',           'men', 'Коротка стрижка з коротким чубчиком та фейдом.'),
    ('Bro Flow',              'men', 'Природне хвилясте волосся середньої довжини.'),
]

print(f'Підключення до БД: {DB_PATH}')
conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

# Отримуємо назви стовпців таблиці hairstyles_hairstyle
cur.execute("PRAGMA table_info(hairstyles_hairstyle)")
cols = [row[1] for row in cur.fetchall()]
print(f'Стовпці таблиці: {cols}')

# Перевіряємо існуючі зачіски
cur.execute("SELECT name, category FROM hairstyles_hairstyle")
existing = {row[0]: row[1] for row in cur.fetchall()}
print(f'Існуючих зачісок у БД: {len(existing)}')

now = datetime.now().isoformat()
created = updated = skipped = 0

for name, category, description in HAIRSTYLES:
    if name not in existing:
        cur.execute(
            "INSERT INTO hairstyles_hairstyle (name, name_en, description, category, master_count, created_at) VALUES (?, ?, ?, ?, ?, ?)",
            (name, '', description, category, 0, now)
        )
        created += 1
        print(f'  ✅ Створено: {name} [{category}]')
    elif existing[name] != category:
        cur.execute(
            "UPDATE hairstyles_hairstyle SET category=? WHERE name=?",
            (category, name)
        )
        updated += 1
        print(f'  🔄 Категорію оновлено: {name} → [{category}]')
    else:
        skipped += 1

conn.commit()
conn.close()

print(f'\n✨ Готово! Створено: {created}, оновлено категорію: {updated}, вже були: {skipped}')
