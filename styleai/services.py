# -*- coding: utf-8 -*-
"""
Сервісний шар додатку styleai.
Рекомендації зачісок за фото (підбір під форму обличчя тощо).
"""
from hairstyles.models import Hairstyle
from .constants import POPULAR_HAIRSTYLE_NAMES


def get_hairstyles_recommendation(photo):
    """
    Приймає завантажене фото (UploadedFile), повертає рекомендації зачісок.
    Може використовуватися для сторінки upload/result без повного пайплайну API.
    """
    # Підбір з популярних зачісок (ті самі, що на головній та в API)
    qs = Hairstyle.objects.filter(name__in=POPULAR_HAIRSTYLE_NAMES)
    ordered = sorted(
        list(qs),
        key=lambda s: POPULAR_HAIRSTYLE_NAMES.index(s.name) if s.name in POPULAR_HAIRSTYLE_NAMES else 999
    )
    styles = ordered[:6]
    return {
        'styles': styles,
        'count': len(styles),
    }
