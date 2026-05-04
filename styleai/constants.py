# -*- coding: utf-8 -*-
"""Список зачісок для блоку «Популярні зачіски» та підбору (порядок на сайті)."""

# ─── БЛОК «ПОПУЛЯРНІ ЗАЧІСКИ» (відображається на головній сторінці) ─────────
POPULAR_HAIRSTYLE_NAMES = [
    'Drop Fade', 'Taper Fade', 'Low Fade', 'Mid Fade', 'High Fade', 'Skin Fade',
    'Textured Crop', 'Burst Fade', 'Edgar Cut', 'Slick Back', 'Pompadour', 'Quiff',
    'Long Wavy Hair', 'Mod Cut', 'Brush Up Fade', 'Undercut', 'Faux Hawk',
    'Crew Cut', 'Buzz Cut', 'Bob', 'Pixie Cut',
    # Жіночі зачіски в популярних
    'Каре', 'Кучерявий Боб', 'Піксі', 'Гарсон', 'Сесон', 'Їжачок', 'Шеггі',
]

# ─── ДОДАТКОВІ ЗАЧІСКИ (НЕ в блоці «Популярні», але доступні для рекомендацій) ──

EXTRA_WOMEN_HAIRSTYLE_NAMES = [
    'Long Layered Cut', 'Butterfly Cut', 'Romance Waves', 'Baroque Bob',
    'Microwave Curls', 'Soft Curtain Bangs', 'Sleek Low Pony', 'Shaggy Lob',
    'Bixie Cut', 'Cowgirl Cut', 'Wolf Cut', 'Curtain Bangs Lob',
    'French Bob', 'Feathered Layers', 'Wispy Bangs',
]

EXTRA_MEN_HAIRSTYLE_NAMES = [
    'Caesar Cut', 'Ivy League', 'Side Part', 'Hard Part',
    'Disconnected Undercut', 'Mohawk Fade', 'Comb Over Fade',
    'Mullet', 'Shaggy Medium', 'Messy Bun', 'Man Bun',
    'Curtains Hairstyle', 'French Crop', 'Bro Flow',
]

# ─── ЖІНОЧІ та ЧОЛОВІЧІ (для фільтрації рекомендацій) ─────────────────────

WOMEN_HAIRSTYLES = [
    # З популярних
    'Bob', 'Pixie Cut', 'Каре', 'Кучерявий Боб', 'Піксі', 'Гарсон', 'Сесон', 'Їжачок', 'Шеггі',
    'Long Wavy Hair',
    # Додаткові жіночі
    'Long Layered Cut', 'Butterfly Cut', 'Romance Waves', 'Baroque Bob', 'Microwave Curls',
    'Soft Curtain Bangs', 'Sleek Low Pony', 'Shaggy Lob', 'Bixie Cut', 'Cowgirl Cut',
    'Wolf Cut', 'Curtain Bangs Lob', 'French Bob', 'Feathered Layers', 'Wispy Bangs',
]

MEN_HAIRSTYLES = [
    # З популярних (не жіночі)
    name for name in POPULAR_HAIRSTYLE_NAMES if name not in WOMEN_HAIRSTYLES
] + EXTRA_MEN_HAIRSTYLE_NAMES

# ─── ДОВЖИНА ВОЛОССЯ ─────────────────────────────────────────────────────────

HAIRSTYLE_LENGTH = {
    # Популярні чоловічі
    'Drop Fade': 'short', 'Taper Fade': 'short', 'Low Fade': 'short', 'Mid Fade': 'short',
    'High Fade': 'short', 'Skin Fade': 'short', 'Textured Crop': 'short', 'Burst Fade': 'short',
    'Edgar Cut': 'short', 'Crew Cut': 'short', 'Buzz Cut': 'short', 'Pixie Cut': 'short',
    'Slick Back': 'medium', 'Pompadour': 'medium', 'Quiff': 'medium', 'Mod Cut': 'medium',
    'Brush Up Fade': 'medium', 'Undercut': 'medium', 'Faux Hawk': 'medium',
    'Long Wavy Hair': 'long', 'Bob': 'long',
    # Популярні жіночі
    'Каре': 'medium', 'Кучерявий Боб': 'short', 'Піксі': 'short', 'Гарсон': 'short',
    'Сесон': 'medium', 'Їжачок': 'short', 'Шеггі': 'medium',
    # Додаткові жіночі
    'Long Layered Cut': 'long', 'Butterfly Cut': 'long', 'Romance Waves': 'long',
    'Baroque Bob': 'short', 'Microwave Curls': 'short', 'Soft Curtain Bangs': 'medium',
    'Sleek Low Pony': 'long', 'Shaggy Lob': 'medium', 'Bixie Cut': 'short', 'Cowgirl Cut': 'long',
    'Wolf Cut': 'medium', 'Curtain Bangs Lob': 'medium', 'French Bob': 'short',
    'Feathered Layers': 'long', 'Wispy Bangs': 'medium',
    # Додаткові чоловічі
    'Caesar Cut': 'short', 'Ivy League': 'short', 'Side Part': 'medium', 'Hard Part': 'short',
    'Disconnected Undercut': 'medium', 'Mohawk Fade': 'short', 'Comb Over Fade': 'short',
    'Mullet': 'medium', 'Shaggy Medium': 'medium', 'Messy Bun': 'long', 'Man Bun': 'long',
    'Curtains Hairstyle': 'medium', 'French Crop': 'short', 'Bro Flow': 'long',
}

HAIRSTYLE_LENGTH_LABELS = {'short': 'Коротка', 'medium': 'Середня', 'long': 'Довга'}

# ─── ОПИСИ ДОДАТКОВИХ ЖІНОЧИХ ЗАЧІСОК ────────────────────────────────────────

EXTRA_WOMEN_STYLE_DESCRIPTIONS = {
    'Long Layered Cut':   "Довге волосся з каскадними шарами для об'єму та руху.",
    'Butterfly Cut':      'Романтична багатошарова стрижка, що нагадує крила метелика.',
    'Romance Waves':      "М'які хвилі, що надають образу романтичності та легкості.",
    'Baroque Bob':        "Вишуканий боб із об'ємними завитками у стилі бароко.",
    'Microwave Curls':    'Дрібні рівні кучері по всій довжині волосся.',
    'Soft Curtain Bangs': "М'який чубчик із розділом посередині, що обрамляє обличчя.",
    'Sleek Low Pony':     'Гладкий низький хвіст — елегантно й лаконічно.',
    'Shaggy Lob':         'Подовжений боб із рваними шарами та легкою текстурою.',
    'Bixie Cut':          'Гібрид боба та піксі: коротко, але з характером.',
    'Cowgirl Cut':        'Вільні довгі хвилі з легкою текстурою в стилі кантрі.',
    'Wolf Cut':           "Дика й сексуальна стрижка з об'ємними шарами та рваними кінчиками.",
    'Curtain Bangs Lob':  'Подовжений боб із чубчиком-фіранкою, що обрамляє обличчя.',
    'French Bob':         'Короткий паризький боб з прямим чубчиком.',
    'Feathered Layers':   'Довге волосся з легкими пір\'їстими шарами.',
    'Wispy Bangs':        "Ніжний тонкий чубчик — витончено й по-жіночому.",
}

# ─── ОПИСИ ДОДАТКОВИХ ЧОЛОВІЧИХ ЗАЧІСОК ─────────────────────────────────────

EXTRA_MEN_STYLE_DESCRIPTIONS = {
    'Caesar Cut':              'Коротка пряма стрижка з горизонтальним чубчиком вперед.',
    'Ivy League':              'Елегантна академічна стрижка з невеликим чубчиком.',
    'Side Part':               'Класичний проділ збоку — завжди стильно й доречно.',
    'Hard Part':               'Чіткий виголений проділ для максимальної чіткості.',
    'Disconnected Undercut':   "Різкий контраст між довгим верхом та виголеними боками.",
    'Mohawk Fade':             'Ірокез із фейдом по боках — сміливо та стильно.',
    'Comb Over Fade':          "Зачесане волосся з плавним фейдом по боках.",
    'Mullet':                  'Коротко спереду — довго ззаду. Культовий ретро-стиль.',
    'Shaggy Medium':           "Середньої довжини з рваними шарами та недбалою текстурою.",
    'Messy Bun':               'Недбало зібраний пучок — casual і стильно.',
    'Man Bun':                 'Акуратний чоловічий пучок для довгого волосся.',
    'Curtains Hairstyle':      'Розчесане на дві сторони волосся посередині — 90-х стиль.',
    'French Crop':             'Коротка стрижка з коротким чубчиком та фейдом.',
    'Bro Flow':                'Природне хвилясте волосся середньої довжини.',
}
