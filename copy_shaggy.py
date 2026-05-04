import shutil
import os

src = r"C:\Users\User\.gemini\antigravity\brain\52320146-a046-4534-86ec-57e96ffac0b8\shaggy_hairstyle_1777396336695.png"
dst = r"C:\Users\User\Desktop\dyplom_2mis\media\hairstyles\homepage_style_69.jpg"

if os.path.exists(src):
    shutil.copy2(src, dst)
    print(f"Done! Copied to {dst}")
    print(f"File size: {os.path.getsize(dst):,} bytes")
else:
    print(f"Source file not found: {src}")
