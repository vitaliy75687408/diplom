import os
import shutil
from pathlib import Path

def restore_images():
    base_dir = Path(r"c:\Users\User\Desktop\dyplom_2mis")
    src_dir = base_dir / "media" / "hairstyles" / "homepage_style_backup_curated_sources"
    dest_dir = base_dir / "media" / "hairstyles"
    
    if not src_dir.exists():
        print(f"Directory not found: {src_dir}")
        return
        
    for file_path in src_dir.glob("*.jpg"):
        dest_path = dest_dir / file_path.name
        print(f"Restoring {file_path.name}...")
        shutil.copy2(file_path, dest_path)
        
    print("Done restoring images!")

if __name__ == "__main__":
    restore_images()
