import json
from pathlib import Path
root = Path('styleai')
map_file = root / 'style_image_map.json'
mm = json.loads(map_file.read_text(encoding='utf-8'))
media = Path('media/hairstyles')
missing = []
for k, v in mm.items():
    if not (media / v).exists():
        missing.append((k, v))
print('total map entries', len(mm))
print('missing count', len(missing))
for k, v in missing:
    print(f'{k} -> {v}')
