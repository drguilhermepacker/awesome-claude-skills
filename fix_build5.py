#!/usr/bin/env python3
"""
Fix #5 — corrige os 2 erros de build:
  1. artigos/[slug]/page.tsx — params.slug → variável já await-ada (Next 15 async params)
  2. eslint.config.mjs — import 'eslint-config-next/core-web-vitals' → '...core-web-vitals.js'

Rodar a partir da raiz do repo: cd ~/website && python3 ~/fix_build5.py
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
    sys.exit("❌  Execute a partir da raiz do repo: cd ~/website && python3 ~/fix_build5.py")

print("\n🔧  Fix #5 — erros de build\n")

# ═══════════════════════════════════════════════════════════════
# 1 — params.slug no jsonLd (Next 15: params é Promise)
# ═══════════════════════════════════════════════════════════════
P = 'src/app/artigos/[slug]/page.tsx'
print("━" * 55)
print(f"[1] {P} — async params…")
sp = rf(P)

fixed = False

# Caso A: const { slug } = await params  (possivelmente com rename)
m = re.search(r'const\s*\{\s*slug\s*(?::\s*(\w+))?\s*[^}]*\}\s*=\s*await\s+params', sp)
if m:
    var = m.group(1) or 'slug'
    sp2 = sp.replace('${params.slug}', '${' + var + '}')
    if sp2 != sp:
        wf(P, sp2, f"params.slug → {var} (destructure com await encontrado)")
        fixed = True
    else:
        print("  ℹ️   Nenhum ${params.slug} para substituir")
        fixed = True

# Caso B: const algo = await params
if not fixed:
    m = re.search(r'const\s+(\w+)\s*=\s*await\s+params\b', sp)
    if m:
        var = m.group(1)
        sp2 = sp.replace('${params.slug}', '${' + var + '.slug}')
        if sp2 != sp:
            wf(P, sp2, f"params.slug → {var}.slug")
            fixed = True

# Caso C: não há await params no componente — adicionar
if not fixed:
    # localizar a função default export da página
    m = re.search(
        r'(export\s+default\s+(?:async\s+)?function\s+\w+\s*\([^)]*\)\s*\{)',
        sp)
    if m:
        header = m.group(1)
        new_header = header
        if 'async' not in header:
            new_header = header.replace('export default function',
                                        'export default async function')
        insert = new_header + '\n  const { slug } = await params\n'
        sp2 = sp.replace(header, insert, 1)
        sp2 = sp2.replace('${params.slug}', '${slug}')
        wf(P, sp2, "await params adicionado no componente + params.slug → slug")
        fixed = True

if not fixed:
    print("  ❌  Não consegui aplicar automaticamente.")
    print("      Linhas 80–140 do arquivo para fix manual:\n")
    for n_, line in enumerate(sp.split('\n')[79:140], 80):
        print(f"  {n_:4d}  {line}")

# Verificação
final = rf(P)
remaining = final.count('${params.slug}')
print(f"  {'✅' if remaining == 0 else '❌'}  Verificação: {remaining} ocorrência(s) de ${{params.slug}} restante(s)")

# ═══════════════════════════════════════════════════════════════
# 2 — eslint.config.mjs import path
# ═══════════════════════════════════════════════════════════════
print("\n[2] eslint.config.mjs — import path…")
E = 'eslint.config.mjs'
if os.path.exists(E):
    e = rf(E)
    if 'core-web-vitals.js' in e:
        print("  ℹ️   Já corrigido")
    else:
        e2 = re.sub(r"(eslint-config-next/core-web-vitals)(['\"])", r"\1.js\2", e)
        if e2 != e:
            wf(E, e2, "eslint.config.mjs — extensão .js adicionada ao import")
        else:
            print("  ⚠️   Padrão não encontrado — conteúdo do arquivo:")
            print(e)
else:
    print("  ℹ️   eslint.config.mjs não existe — nada a fazer")

print("""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Agora rode:
  npm run build

Se passar:
  git add -A
  git commit -m "seo: FAQPage PT + geo; fix async params e eslint config"
  git push
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
""")
