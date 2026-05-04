import shutil
import os

src = r'C:\Users\User\.gemini\antigravity\brain\3cd332d5-f3a4-4ad6-a459-da06f78bc7aa\drop_fade_hairstyle_1777828851745.png'
dest1 = r'c:\Users\User\Desktop\dyplom_2mis\media\hairstyles\homepage_style_42.jpg'
dest2 = r'c:\Users\User\Desktop\dyplom_2mis\media\hairstyles\drop_fade.jpg'
dest3 = r'c:\Users\User\Desktop\dyplom_2mis\media\hairstyles\homepage_style_backup_curated_sources\homepage_style_42.jpg'

for d in [dest1, dest2, dest3]:
    print(f"Copying to {d}")
    shutil.copy2(src, d)
