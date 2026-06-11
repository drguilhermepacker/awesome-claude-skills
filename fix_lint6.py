#!/usr/bin/env python3
"""
Fix #6 — erros de lint que agora quebram o build:
  1. <a href="/"> → <Link href="/"> nas 3 landing pages (+ import)
  2. EvidenceSources.tsx — aspas literais em texto JSX → &quot;
  3. Warnings de variáveis não usadas (reel, FAQ) — prefixo _ para silenciar

Rodar a partir da raiz do repo: cd ~/website && python3 ~/fix_lint6.py
"""
import os, re, sys

def rf(path):
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()

def wf(path, content, label=None):
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"  ✅  {label or path}")

if not os.path.isdir('src/app'):
    sys.exit("❌  Execute a partir da raiz do repo: cd ~/website && python3 ~/fix_lint6.py")

print("\n🔧  Fix #6 — erros de lint\n")

# ═══════════════════════════════════════════════════════════════
# 1 — <a href="/"> → <Link> nas landing pages
# ═══════════════════════════════════════════════════════════════
print("━" * 55)
print('[1] <a href="/"> → <Link> nas landing pages…')

PAGES = [
    'src/app/medico-de-familia/page.tsx',
    'src/app/telemedicina/page.tsx',
    'src/app/visita-domiciliar-jaragua-do-sul/page.tsx',
]

for p in PAGES:
    if not os.path.exists(p):
        print(f"  ⚠️   {p} não existe")
        continue
    s = rf(p)
    orig = s

    # Substituir âncoras internas de linha única
    s = re.sub(r'<a href="/"([^>]*)>([^<]*)</a>', r'<Link href="/"\1>\2</Link>', s)

    # Garantir o import
    if '<Link' in s and "from 'next/link'" not in s and 'from "next/link"' not in s:
        m = re.search(r"^import .*$", s, re.MULTILINE)
        if m:
            s = s[:m.end()] + "\nimport Link from 'next/link'" + s[m.end():]
        else:
            s = "import Link from 'next/link'\n" + s

    if s != orig:
        n = orig.count('<a href="/"')
        wf(p, s, f"{p} — {n} âncora(s) → <Link>")
    else:
        print(f"  ℹ️   {p} — nada a mudar")

# ═══════════════════════════════════════════════════════════════
# 2 — EvidenceSources.tsx — aspas em texto JSX
# ═══════════════════════════════════════════════════════════════
print("\n[2] EvidenceSources.tsx — aspas não escapadas…")
EV = 'src/components/EvidenceSources.tsx'
if os.path.exists(EV):
    s = rf(EV)
    lines = s.split('\n')
    idx = 113  # linha 114 (0-based)
    if idx < len(lines):
        line = lines[idx]
        print(f"  Linha 114 antes: {line.strip()[:120]}")
        # Escapar aspas apenas em segmentos de texto JSX (entre > e <)
        fixed_line = re.sub(
            r'>([^<>]*)<',
            lambda m: '>' + m.group(1).replace('"', '&quot;') + '<',
            line)
        # Caso a linha seja texto puro sem tags (continuação de JSX text)
        if fixed_line == line and '"' in line and '=' not in line:
            fixed_line = line.replace('"', '&quot;')
        if fixed_line != line:
            lines[idx] = fixed_line
            wf(EV, '\n'.join(lines), "EvidenceSources.tsx — aspas escapadas (&quot;)")
            print(f"  Linha 114 depois: {fixed_line.strip()[:120]}")
        else:
            print("  ⚠️   Não consegui corrigir automaticamente — contexto (linhas 110–118):")
            for j in range(109, min(118, len(lines))):
                print(f"  {j+1:4d}  {lines[j]}")
else:
    print("  ⚠️   arquivo não encontrado")

# ═══════════════════════════════════════════════════════════════
# 3 — Warnings: variáveis não usadas (não quebram o build, mas limpa)
# ═══════════════════════════════════════════════════════════════
print("\n[3] Warnings de variáveis não usadas…")
for fp, var in [('src/app/reel/page.tsx', 'useTime'),
                ('src/components/FAQ.tsx', 'GREEN_SHADES')]:
    if not os.path.exists(fp):
        continue
    s = rf(fp)
    s2 = re.sub(rf'\bconst\s+{var}\b', f'const _{var}', s, count=1)
    if s2 != s:
        wf(fp, s2, f"{fp} — {var} → _{var}")
    else:
        print(f"  ℹ️   {fp} — padrão não encontrado (warning não-fatal, ok ignorar)")

print("""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
⚠️   IMPORTANTE: o último push (f273513) vai FALHAR na Vercel
    porque os erros de lint agora quebram o build.

Rode agora:
  npm run build

Se passar:
  git add -A
  git commit -m "fix: Link em vez de <a>, aspas escapadas, lint warnings"
  git push
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
""")
