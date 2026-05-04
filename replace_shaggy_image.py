import shutil
import os

src = r"C:\Users\User\.gemini\antigravity\brain\9aefb72b-53ce-4b2e-ab44-251166230fb3\shaggy_woman_hairstyle_1777489375558.png"
dst = r"c:\Users\User\Desktop\dyplom_2mis\media\hairstyles\шеггі.jpg"

if os.path.exists(src):
    shutil.copy2(src, dst)
    print(f"✅ Успішно замінено: {dst}")
    print(f"   Розмір нового файлу: {os.path.getsize(dst):,} байт")
else:
    print(f"❌ Вихідний файл не знайдено: {src}")
