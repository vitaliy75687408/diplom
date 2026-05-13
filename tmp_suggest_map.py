import json
import re
from pathlib import Path
from difflib import SequenceMatcher
root = Path('styleai')
map_file = root / 'style_image_map.json'
mm = json.loads(map_file.read_text(encoding='utf-8'))
media = Path('media/hairstyles')
files = sorted([p.name for p in media.glob('*') if p.is_file()])

def norm(s):
    s = s.lower()
    s = s.replace('_', ' ').replace('-', ' ').replace('ё','е')
    s = re.sub(r'[^a-z0-9а-яіїєґ ]+', ' ', s)
    s = re.sub(r'\s+', ' ', s).strip()
    return s

file_norm = {f: norm(Path(f).stem) for f in files}
print('total files', len(files))
for k,v in mm.items():
    p = Path('media') / v
    if p.exists():
        continue
    key_norm = norm(Path(v).stem)
    best = max(files, key=lambda f: SequenceMatcher(None, key_norm, file_norm[f]).ratio())
    print(f'{k} -> {v} | best candidate: {best} | score={SequenceMatcher(None,key_norm,file_norm[best]).ratio():.2f} | norm={key_norm} | file_norm={file_norm[best]}')
