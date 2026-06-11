#!/usr/bin/env python3
"""
SEO Audit Fix #3 — drguilherme.com — Junho 2026
Corrige o bug do fix_audit2.py:
  1. Substitui DE VERDADE o bloco FAQPage em layout.tsx (remoção por índice, não regex)
  2. Extração robusta de q/a (aspas escapadas, template literals multilinha)
  3. Verifica CEP/geo aplicados
  4. Imprime ResponsivePicture.tsx + call sites para o fix de width/height

Rodar a partir da raiz do repo: cd ~/website && python3 ~/fix_faq3.py
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
    sys.exit("❌  Execute a partir da raiz do repo: cd ~/website && python3 ~/fix_faq3.py")

LP = 'src/app/layout.tsx'
TL = 'src/lib/translations.ts'

print("\n🔧  Fix #3 — FAQPage real + verificação\n")

# ═══════════════════════════════════════════════════════════════
# 1 — Verificar CEP/geo
# ═══════════════════════════════════════════════════════════════
print("━" * 55)
print("[1] Verificando CEP/geo em layout.tsx…")
lx = rf(LP)
for field, expected in [('postalCode', '89251-702'),
                        ('latitude', '-26.491357919087612'),
                        ('longitude', '-49.08403664232914')]:
    m = re.search(rf'"{field}"\s*:\s*"?([0-9\-\.]+)"?', lx)
    cur = m.group(1) if m else '(não encontrado)'
    ok = '✅' if cur == expected else '❌'
    print(f"  {ok}  {field}: {cur}")

# ═══════════════════════════════════════════════════════════════
# 2 — Extração robusta de q/a de translations.ts
# ═══════════════════════════════════════════════════════════════
print("\n[2] Extraindo TODOS os pares q/a de translations.ts…")
tl = rf(TL)

def unescape(s):
    return s.replace('\\"', '"').replace("\\'", "'").replace('\\`', '`').replace('\\n', ' ')

STRING_PAT = r'''(?:
    "((?:[^"\\]|\\.)*)"     |
    '((?:[^'\\]|\\.)*)'     |
    `((?:[^`\\]|\\.)*)`
)'''

qs, ans = {}, {}
for m in re.finditer(r'\b([qa])(\d+)\s*:\s*' + STRING_PAT, tl, re.VERBOSE | re.DOTALL):
    kind, idx = m.group(1), int(m.group(2))
    val = next((g for g in m.groups()[2:] if g is not None), '')
    val = re.sub(r'\s+', ' ', unescape(val)).strip()
    (qs if kind == 'q' else ans)[idx] = val

indexes = sorted(set(qs) & set(ans))
missing_q = sorted(set(ans) - set(qs))
missing_a = sorted(set(qs) - set(ans))
print(f"  ℹ️   Pares completos: {len(indexes)} → índices {indexes}")
if missing_q: print(f"  ⚠️   Respostas sem pergunta: {missing_q}")
if missing_a: print(f"  ⚠️   Perguntas sem resposta: {missing_a}")

for i in indexes:
    print(f"\n  Q{i}: {qs[i][:90]}")
    print(f"  A{i}: {ans[i][:90]}…")

if len(indexes) < 2:
    sys.exit("\n❌  Extração falhou — envie o conteúdo de src/lib/translations.ts")

# ═══════════════════════════════════════════════════════════════
# 3 — Substituir o bloco FAQPage por índice (sem regex frágil)
# ═══════════════════════════════════════════════════════════════
print(f"\n[3] Substituindo bloco FAQPage com {len(indexes)} perguntas…")

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
# indent the closing brace to match
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
    # Sem bloco existente — inserir antes de </body>
    if '</body>' in lx:
        lx = lx.replace('</body>', '        ' + NEW_BLOCK + '\n      </body>', 1)
        wf(LP, lx, "layout.tsx — FAQPage inserido (novo)")
    else:
        sys.exit("❌  </body> não encontrado em layout.tsx — inserção manual necessária")
else:
    start = lx.rfind('<script', 0, i)
    end = lx.find('/>', i)
    if start == -1 or end == -1:
        sys.exit("❌  Não consegui delimitar o bloco <script> existente — fix manual")
    lx = lx[:start] + NEW_BLOCK + lx[end + 2:]
    wf(LP, lx, f"layout.tsx — FAQPage substituído ({len(indexes)} perguntas)")

# Verificação real: contar Questions no arquivo gravado
n = rf(LP).count('"@type": "Question"')
print(f"  {'✅' if n == len(indexes) else '❌'}  Verificação: {n} perguntas no arquivo gravado")

# ═══════════════════════════════════════════════════════════════
# 4 — Inspecionar ResponsivePicture.tsx + call sites
# ═══════════════════════════════════════════════════════════════
print("\n[4] Conteúdo de ResponsivePicture.tsx (para o fix width/height):")
print("─" * 55)
RP = 'src/components/ResponsivePicture.tsx'
if os.path.exists(RP):
    for n_, line in enumerate(rf(RP).split('\n'), 1):
        print(f"  {n_:3d}  {line}")
else:
    print("  (arquivo não encontrado)")

print("\n  Call sites de <ResponsivePicture:")
for dp, _, files in os.walk('src'):
    if any(x in dp for x in ['node_modules', '.next', '.git']):
        continue
    for fn in files:
        if not fn.endswith(('.tsx', '.jsx')):
            continue
        fp = os.path.join(dp, fn)
        if fp == RP:
            continue
        src_text = rf(fp)
        for m in re.finditer(r'<ResponsivePicture\b[^>]*/?>', src_text, re.DOTALL):
            line = src_text[:m.start()].count('\n') + 1
            print(f"    {fp}:{line}")
            print(f"      {' '.join(m.group(0).split())[:160]}")

print("""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Próximos passos:
  1. Verifique o build ANTES de push:
       npm run build
  2. Se o build passar:
       git add src/app/layout.tsx
       git commit -m "seo: FAQPage completo no schema JSON-LD"
       git push
  3. Cole a saída deste script no chat — vou gerar o fix
     exato do ResponsivePicture com width/height.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
""")
