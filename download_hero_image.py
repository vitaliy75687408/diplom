# -*- coding: utf-8 -*-
"""Завантажує зображення хлопчика у барбера (схоже на Solidol) в static/images/hero-barber.jpg"""
import os
import requests

# Фото: чоловіча зачіска — фейд, текстурований кроп (Unsplash, безкоштовне)
url = "https://unsplash.com/photos/y9xnUFMFGKw/download?force=true&w=600"
static_dir = os.path.join(os.path.dirname(__file__), "static", "images")
os.makedirs(static_dir, exist_ok=True)
path = os.path.join(static_dir, "hero-barber.jpg")

try:
    r = requests.get(url, timeout=20, allow_redirects=True)
    r.raise_for_status()
    with open(path, "wb") as f:
        f.write(r.content)
    print("Зображення збережено: static/images/hero-barber.jpg")
except Exception as e:
    print("Помилка:", e)
