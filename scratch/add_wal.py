import glob
import re

models = glob.glob('src/models/*_model.py')
for m in models:
    with open(m, 'r', encoding='utf-8') as f:
        content = f.read()
    
    if 'PRAGMA journal_mode=WAL' not in content:
        content = re.sub(
            r'self\.conn\.row_factory = sqlite3\.Row',
            r'self.conn.row_factory = sqlite3.Row\n            self.conn.execute("PRAGMA journal_mode=WAL;")',
            content
        )
        with open(m, 'w', encoding='utf-8') as f:
            f.write(content)
            print(f'WAL mode injected in {m}')
