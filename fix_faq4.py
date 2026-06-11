#!/usr/bin/env python3
"""
SEO Audit Fix #4 — drguilherme.com — Junho 2026
Corrige os problemas do fix #3:
  1. Extrai q/a APENAS da seção PT de translations.ts (o #3 pegou a seção ES)
  2. Substitui o bloco FAQPage (atualmente em espanhol) pelo português
  3. ADICIONA o bloco "geo" (GeoCoordinates) ao schema — não existia
  4. Imprime o contexto dos call sites de ResponsivePicture (verificação CLS)

Rodar a partir da raiz do repo: cd ~/website && python3 ~/fix_faq4.py
"""
import os, re, sys, json

def rf(path):
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()

def wf(path, content, label=None):
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"  ✅  {label or path}")

if not os.path.isdir('src/app'):
    sys.exit("❌  Execute a partir da raiz do repo: cd ~/website && python3 ~/fix_faq4.py")

LP = 'src/app/layout.tsx'
TL = 'src/lib/translations.ts'

print("\n🔧  Fix #4 — FAQPage em PORTUGUÊS + geo\n")

# ═══════════════════════════════════════════════════════════════
# 1 — Isolar a seção PT de translations.ts
# ═══════════════════════════════════════════════════════════════
print("━" * 55)
print("[1] Isolando seção PT de translations.ts…")
tl = rf(TL)

lang_marks = [(m.start(), m.group(1))
              for m in re.finditer(r'\b(pt|en|es|de|fr|it)\s*:\s*\{', tl)]
print(f"  ℹ️   Seções de idioma encontradas: {[l for _, l in lang_marks]}")

pt_start = next((pos for pos, lang in lang_marks if lang == 'pt'), None)
if pt_start is None:
    sys.exit("❌  Seção 'pt:' não encontrada — envie o início de translations.ts")

pt_end = next((pos for pos, lang in lang_marks if pos > pt_start), len(tl))
pt_section = tl[pt_start:pt_end]
print(f"  ✅  Seção PT: caracteres {pt_start}–{pt_end}")

# ═══════════════════════════════════════════════════════════════
# 2 — Extrair q/a da seção PT
# ═══════════════════════════════════════════════════════════════
print("\n[2] Extraindo q/a da seção PT…")

def unescape(s):
    return s.replace('\\"', '"').replace("\\'", "'").replace('\\`', '`').replace('\\n', ' ')

STRING_PAT = r'''(?:
    "((?:[^"\\]|\\.)*)"     |
    '((?:[^'\\]|\\.)*)'     |
    `((?:[^`\\]|\\.)*)`
)'''

qs, ans = {}, {}
for m in re.finditer(r'\b([qa])(\d+)\s*:\s*' + STRING_PAT, pt_section, re.VERBOSE | re.DOTALL):
    kind, idx = m.group(1), int(m.group(2))
    val = next((g for g in m.groups()[2:] if g is not None), '')
    val = re.sub(r'\s+', ' ', unescape(val)).strip()
    target = qs if kind == 'q' else ans
    if idx not in target:          # primeira ocorrência vence (segurança extra)
        target[idx] = val

indexes = sorted(set(qs) & set(ans))
print(f"  ℹ️   Pares completos: {len(indexes)} → índices {indexes}")
for i in indexes:
    print(f"\n  Q{i}: {qs[i][:90]}")
    print(f"  A{i}: {ans[i][:90]}…")

if not indexes:
    sys.exit("\n❌  Nenhum par PT encontrado — envie a seção 'pt' de translations.ts")

# sanity check: deve ser português, não espanhol
sample = ' '.join(qs.values())
if '¿' in sample or 'Cómo' in sample:
    sys.exit("\n❌  Extração ainda parece espanhol — envie a seção 'pt' de translations.ts")

# ═══════════════════════════════════════════════════════════════
# 3 — Substituir bloco FAQPage (atualmente ES) pelo PT
# ═══════════════════════════════════════════════════════════════
print(f"\n[3] Substituindo FAQPage com {len(indexes)} perguntas em PT…")

entities = [{
    "@type": "Question",
    "name": qs[i],
    "acceptedAnswer": {"@type": "Answer", "text": ans[i]}
} for i in indexes]

faq_obj = {
    "@context": "https://schema.org",
    "@type": "FAQPage",
    "mainEntity": entities
}
faq_json = json.dumps(faq_obj, ensure_ascii=False, indent=12)
faq_json = faq_json.replace('\n}', '\n          }')

NEW_BLOCK = (
    '<script\n'
    '          type="application/ld+json"\n'
    '          dangerouslySetInnerHTML={{ __html: JSON.stringify(' +
    faq_json +
    ') }}\n'
    '        />'
)

lx = rf(LP)
i = lx.find('"FAQPage"')
if i == -1:
    if '</body>' in lx:
        lx = lx.replace('</body>', '        ' + NEW_BLOCK + '\n      </body>', 1)
        wf(LP, lx, "layout.tsx — FAQPage inserido")
    else:
        sys.exit("❌  </body> não encontrado")
else:
    start = lx.rfind('<script', 0, i)
    end = lx.find('/>', i)
    if start == -1 or end == -1:
        sys.exit("❌  Não consegui delimitar o bloco existente")
    lx = lx[:start] + NEW_BLOCK + lx[end + 2:]
    wf(LP, lx, f"layout.tsx — FAQPage substituído ({len(indexes)} perguntas PT)")

saved = rf(LP)
n = saved.count('"@type": "Question"')
is_pt = '¿' not in saved
print(f"  {'✅' if n == len(indexes) else '❌'}  Verificação: {n} perguntas gravadas")
print(f"  {'✅' if is_pt else '❌'}  Verificação: sem texto em espanhol no arquivo")

# ═══════════════════════════════════════════════════════════════
# 4 — Adicionar bloco geo (GeoCoordinates) ao schema
# ═══════════════════════════════════════════════════════════════
print("\n[4] Adicionando geo (GeoCoordinates)…")
lx = rf(LP)

if '"geo"' in lx or 'GeoCoordinates' in lx:
    print("  ℹ️   geo já presente — verificando valores…")
    lx = re.sub(r'("latitude"\s*:\s*)-?[0-9\.]+', r'\g<1>-26.491357919087612', lx)
    lx = re.sub(r'("longitude"\s*:\s*)-?[0-9\.]+', r'\g<1>-49.08403664232914', lx)
    wf(LP, lx, "layout.tsx — geo valores confirmados")
else:
    GEO = ('''  "geo": {
    "@type": "GeoCoordinates",
    "latitude": -26.491357919087612,
    "longitude": -49.08403664232914
  },
''')
    # Inserir logo após o fechamento do objeto "address"
    m = re.search(r'"addressCountry"\s*:\s*"BR"\s*\n?\s*\},?\n', lx)
    if m:
        # detectar indentação do bloco address
        addr_line = lx.rfind('"address"', 0, m.start())
        indent = ''
        if addr_line != -1:
            line_start = lx.rfind('\n', 0, addr_line) + 1
            indent = lx[line_start:addr_line]
        GEO_IND = (
            f'{indent}"geo": {{\n'
            f'{indent}  "@type": "GeoCoordinates",\n'
            f'{indent}  "latitude": -26.491357919087612,\n'
            f'{indent}  "longitude": -49.08403664232914\n'
            f'{indent}}},\n'
        )
        lx = lx[:m.end()] + GEO_IND + lx[m.end():]
        wf(LP, lx, "layout.tsx — geo adicionado após address")
    else:
        print("  ❌  Não localizei o fechamento do bloco address — adicione manualmente:")
        print(GEO)

n_geo = rf(LP).count('GeoCoordinates')
print(f"  {'✅' if n_geo >= 1 else '❌'}  Verificação: {n_geo} bloco(s) GeoCoordinates")

# ═══════════════════════════════════════════════════════════════
# 5 — Contexto dos call sites ResponsivePicture (verificação CLS)
# ═══════════════════════════════════════════════════════════════
print("\n[5] Contexto dos call sites ResponsivePicture (containers pai):")
SITES = [('src/components/Hero.tsx', 205),
         ('src/components/Blog.tsx', 36),
         ('src/components/About.tsx', 122)]
for fp, line in SITES:
    if not os.path.exists(fp):
        continue
    lines = rf(fp).split('\n')
    lo, hi = max(0, line - 16), min(len(lines), line + 4)
    print(f"\n  ── {fp} (linhas {lo+1}–{hi}) " + "─" * 20)
    for j in range(lo, hi):
        print(f"  {j+1:4d}  {lines[j]}")

print("""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Próximos passos:
  1. npm run build        ← verificar build ANTES de push
  2. Se passar:
       git add src/app/layout.tsx
       git commit -m "seo: FAQPage em PT + GeoCoordinates no schema"
       git push
  3. Cole a saída no chat — confirmo o CLS dos containers.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
""")
