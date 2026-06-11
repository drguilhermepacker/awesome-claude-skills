#!/usr/bin/env python3
"""
Fix #8 — lang="en" → lang="pt-BR" in layout.tsx
The App Router root layout still renders <html lang="en">; must be pt-BR for SEO.

Run from the root of the website repo:
  cd ~/website && python3 ~/fix_lang8.py
"""
import os, sys

if not os.path.isdir('src/app'):
    sys.exit("❌  Execute a partir da raiz do repo: cd ~/website && python3 ~/fix_lang8.py")

P = 'src/app/layout.tsx'
with open(P, encoding='utf-8') as f:
    src = f.read()

count = src.count('<html lang="en"')
if count == 0:
    # Check if already fixed or uses a different pattern
    if 'lang="pt-BR"' in src or "lang='pt-BR'" in src:
        print(f"✅  {P} — lang já é pt-BR, nenhuma mudança necessária")
    else:
        print(f"⚠️   {P} — padrão <html lang=\"en\"> não encontrado; verifique manualmente")
    sys.exit(0)

fixed = src.replace('<html lang="en"', '<html lang="pt-BR"')
with open(P, 'w', encoding='utf-8') as f:
    f.write(fixed)

print(f'✅  {P} — {count} ocorrência(s) de lang="en" → lang="pt-BR"')
print("""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Agora rode:
  npm run build

Se passar:
  git add src/app/layout.tsx
  git commit -m "fix: html lang pt-BR (era en)"
  git push
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
""")
