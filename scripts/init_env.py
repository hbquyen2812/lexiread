"""Generate secrets without Django or other dependencies. Never prints secrets."""
from pathlib import Path
import secrets
root=Path(__file__).resolve().parent.parent
p=root/'.env'
text=p.read_text(encoding='utf-8-sig') if p.exists() else (root/'.env.example').read_text()
text=text.replace('__GENERATE_SECRET__',secrets.token_urlsafe(60)).replace('__GENERATE_DATABASE_PASSWORD__',secrets.token_hex(24))
p.write_text(text,encoding='utf-8')
try:p.chmod(0o600)
except OSError:pass
print('Ready: .env (secrets not displayed). Existing settings were preserved.')
