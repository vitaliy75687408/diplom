import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

def _read_key(env_key, env_var_name):
    # This imitates settings.py _read_key
    val = (os.environ.get(env_key) or '').strip()
    if val: return val
    for _p in (BASE_DIR / 'config.env', BASE_DIR / 'env.txt', BASE_DIR / '.env'):
        if _p.exists():
            print(f"Reading from {_p}")
            with open(_p, encoding='utf-8') as f:
                for line in f:
                    line = line.strip().strip('\ufeff')
                    if line.startswith(env_var_name + '='):
                        return line.split('=', 1)[1].strip().strip('"').strip("'")
            break
    return 'NOT_FOUND'

print(f"GEMINI_API_KEY: {_read_key('GEMINI_API_KEY', 'GEMINI_API_KEY')[:8]}...")
print(f"OPENAI_API_KEY: {_read_key('OPENAI_API_KEY', 'OPENAI_API_KEY')[:8]}...")
