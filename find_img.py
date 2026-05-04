import os
from pathlib import Path

BASE_DIR = Path(r"c:\Users\User\Desktop\dyplom_2mis")

def find_file(name):
    for path in BASE_DIR.rglob(name):
        return path
    return None

target = "homepage_style_42.jpg"
found = find_file(target)
if found:
    print(f"FOUND: {found}")
    print(f"Relative to BASE_DIR: {found.relative_to(BASE_DIR)}")
else:
    print(f"NOT FOUND: {target} in {BASE_DIR}")
