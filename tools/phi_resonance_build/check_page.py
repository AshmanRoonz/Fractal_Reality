"""Syntax-check a built page's script and confirm every $('id') it uses exists.

Usage: python check_page.py <page.html> [work_dir]   (work_dir: where the script is written for
node --check; by default the system's temporary folder)
Exits with 1 when the script fails node --check, an id it looks up is missing, or an id is used twice.
"""
import io, os, re, subprocess, sys, tempfile
page = sys.argv[1]
scratch = sys.argv[2] if len(sys.argv) > 2 else tempfile.gettempdir()
s = io.open(page, encoding='utf-8').read()
m = re.search(r'<script>(.*)</script>', s, re.S)
js = os.path.join(scratch, 'phi_resonance_page_check.js')
io.open(js, 'w', encoding='utf-8').write(m.group(1))
ids = re.findall(r"\$\('([A-Za-z0-9_]+)'\)", m.group(1))
made = set(re.findall(r"\.id = '([A-Za-z0-9_]+)'", m.group(1)))  # elements the script makes itself
body = s[:s.index('<script>')]
missing = sorted(set(i for i in ids if ('id="' + i + '"') not in body and i not in made))
print('missing ids:', missing)
dup = sorted(set(i for i in re.findall(r'id="([^"]+)"', body) if body.count('id="' + i + '"') > 1))
print('duplicate ids:', dup)
r = subprocess.run(['node', '--check', js], capture_output=True, text=True)
print('node --check:', r.returncode, r.stderr[:400])
print('gold 215 left:', s.count('255,215,0') + s.count('255, 215, 0'))
print('em dashes:', s.count('—'))
if missing or dup or r.returncode:
    sys.exit(1)
