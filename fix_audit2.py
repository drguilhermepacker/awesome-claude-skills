#!/usr/bin/env python3
"""
SEO Audit Fix #2 — drguilherme.com — Junho 2026
Tarefas:
  1. CEP 89251-702 + coordenadas confirmadas
  2. FAQPage completo (9 perguntas de translations.ts)
  3. MedicalWebPage + BreadcrumbList em artigos/[slug]/page.tsx
  4. Relatório de <img> sem width/height

Rodar a partir da raiz do repo: cd ~/website && python3 ~/fix_audit2.py
"""
import os, re, sys, json, textwrap

def rf(path):
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()

def wf(path, content, label=None):
    d = os.path.dirname(path)
    if d:
        os.makedirs(d, exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"  ✅  {label or path}")

if not os.path.isdir('src/app'):
    sys.exit("❌  Execute a partir da raiz do repo: cd ~/website && python3 ~/fix_audit2.py")

print("\n🔧  Fix Audit #2 — drguilherme.com\n")
LP = 'src/app/layout.tsx'

# ═══════════════════════════════════════════════════════════════
# 1 — CEP 89251-702 e coordenadas confirmadas
# ═══════════════════════════════════════════════════════════════
print("━" * 55)
print("[1] CEP 89251-702 e coordenadas confirmadas…")
lx = rf(LP)

orig = lx
lx = re.sub(r'("postalCode"\s*:\s*")[^"]*"', r'\g<1>89251-702"', lx)
lx = re.sub(r'("latitude"\s*:\s*)[0-9\-\.]+', r'\g<1>-26.491357919087612', lx)
lx = re.sub(r'("longitude"\s*:\s*)[0-9\-\.]+', r'\g<1>-49.08403664232914', lx)

if lx != orig:
    wf(LP, lx, "layout.tsx — CEP e geo atualizados")
else:
    print("  ℹ️   Sem mudanças (campos já corretos ou não encontrados)")

# ═══════════════════════════════════════════════════════════════
# 2 — FAQPage — extrair 9 perguntas de translations.ts
# ═══════════════════════════════════════════════════════════════
print("\n[2] FAQPage schema — extraindo perguntas de translations.ts…")
TL = 'src/lib/translations.ts'

if not os.path.exists(TL):
    print(f"  ❌  {TL} não encontrado — pulando FAQPage")
else:
    tl = rf(TL)
    pairs = []

    # Pattern A: q1: "...", a1: "..."  (também com backtick ou aspas simples)
    for i in range(1, 10):
        qm = re.search(rf'\bq{i}\s*:\s*["`\']([^`"\']+)["`\']', tl)
        am = re.search(rf'\ba{i}\s*:\s*["`\']([^`"\']+)["`\']', tl)
        if qm and am:
            pairs.append((qm.group(1).strip(), am.group(1).strip()))

    if len(pairs) < 2:
        # Pattern B: {question: "...", answer: "..."}
        qs = re.findall(r'question\s*:\s*["`\']([^`"\']+)["`\']', tl)
        ans = re.findall(r'answer\s*:\s*["`\']([^`"\']+)["`\']', tl)
        pairs = list(zip(qs, ans))

    if len(pairs) < 2:
        # Pattern C: { q: "...", a: "..." } inside array
        qs = re.findall(r'\bq\s*:\s*["`\']([^`"\']+)["`\']', tl)
        ans = re.findall(r'\ba\s*:\s*["`\']([^`"\']+)["`\']', tl)
        pairs = list(zip(qs, ans))

    print(f"  ℹ️   {len(pairs)} par(es) FAQ encontrado(s) em translations.ts")

    if len(pairs) >= 2:
        # Build mainEntity array as Python list then serialize
        entities = []
        for q, a in pairs:
            entities.append({
                "@type": "Question",
                "name": q,
                "acceptedAnswer": {
                    "@type": "Answer",
                    "text": a
                }
            })

        # Serialize to JSON with 14-space indent for nice JSX embedding
        entities_json = json.dumps(entities, ensure_ascii=False, indent=14)
        # trim leading [
        entities_json = entities_json[1:-1].rstrip()

        FAQ_SCRIPT = (
            '        <script\n'
            '          type="application/ld+json"\n'
            '          dangerouslySetInnerHTML={{ __html: JSON.stringify({\n'
            '            "@context": "https://schema.org",\n'
            '            "@type": "FAQPage",\n'
            '            "mainEntity": [' +
            entities_json +
            '\n            ]\n'
            '          }) }}\n'
            '        />'
        )

        lx = rf(LP)
        # Replace existing FAQPage block (greedy match from <script to />
        # The block starts with <script and contains "FAQPage" and ends with />
        new_lx = re.sub(
            r'<script\s[^>]*dangerouslySetInnerHTML[^/]*/>\s*(?=\s*[\n\r])',
            lambda m: FAQ_SCRIPT + '\n' if '"FAQPage"' in m.group(0) else m.group(0),
            lx
        )
        # If that didn't work (no existing FAQPage to replace), insert before </body>
        if '"FAQPage"' not in new_lx:
            if '"FAQPage"' in lx:
                # Existing FAQPage but regex didn't match — try multiline approach
                new_lx = re.sub(
                    r'<script[^>]*>\s*\{\{[^}]*"FAQPage"[\s\S]*?\}\}\s*/?>',
                    FAQ_SCRIPT,
                    lx, flags=re.DOTALL
                )
            if '"FAQPage"' not in new_lx:
                # Still not there: insert before closing </body>
                new_lx = lx.replace('</body>', FAQ_SCRIPT + '\n      </body>', 1)
                if new_lx == lx:
                    # No </body> either — insert before last </html>
                    new_lx = lx + '\n' + FAQ_SCRIPT

        wf(LP, new_lx, f"layout.tsx — FAQPage com {len(pairs)} perguntas")
    else:
        print("  ❌  Menos de 2 pares encontrados — verificar translations.ts manualmente")
        print("      Estruturas suportadas:")
        print("        q1: 'pergunta', a1: 'resposta', ...")
        print("        { question: '...', answer: '...' }")

# ═══════════════════════════════════════════════════════════════
# 3 — MedicalWebPage + BreadcrumbList em artigos/[slug]/page.tsx
# ═══════════════════════════════════════════════════════════════
print("\n[3] Schema de artigos — artigos/[slug]/page.tsx…")
SLUG_PATH = 'src/app/artigos/[slug]/page.tsx'

if not os.path.exists(SLUG_PATH):
    print(f"  ⚠️   {SLUG_PATH} não encontrado — criando template completo…")
    ARTICLE_PAGE = '''\
import type { Metadata } from 'next'
import { notFound } from 'next/navigation'
import { getPostBySlug, getAllPosts } from '@/lib/posts'

interface Props {
  params: { slug: string }
}

export async function generateStaticParams() {
  const posts = getAllPosts()
  return posts.map((p) => ({ slug: p.slug }))
}

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const post = getPostBySlug(params.slug)
  if (!post) return {}
  return {
    title: `${post.title} | Dr. Guilherme Packer`,
    description: post.excerpt ?? post.title,
    alternates: {
      canonical: `https://drguilherme.com/artigos/${params.slug}/`,
    },
    openGraph: {
      title: post.title,
      description: post.excerpt ?? post.title,
      url: `https://drguilherme.com/artigos/${params.slug}/`,
      type: 'article',
      publishedTime: post.date,
    },
  }
}

export default function ArtigoPage({ params }: Props) {
  const post = getPostBySlug(params.slug)
  if (!post) notFound()

  const jsonLd = {
    '@context': 'https://schema.org',
    '@graph': [
      {
        '@type': 'MedicalWebPage',
        '@id': `https://drguilherme.com/artigos/${params.slug}/#webpage`,
        url: `https://drguilherme.com/artigos/${params.slug}/`,
        name: post.title,
        description: post.excerpt ?? post.title,
        inLanguage: 'pt-BR',
        author: { '@id': 'https://drguilherme.com/#physician' },
        publisher: { '@id': 'https://drguilherme.com/#physician' },
        reviewedBy: { '@id': 'https://drguilherme.com/#physician' },
        datePublished: post.date,
        dateModified: post.date,
      },
      {
        '@type': 'BreadcrumbList',
        itemListElement: [
          { '@type': 'ListItem', position: 1, name: 'Início', item: 'https://drguilherme.com/' },
          { '@type': 'ListItem', position: 2, name: 'Artigos', item: 'https://drguilherme.com/artigos/' },
          { '@type': 'ListItem', position: 3, name: post.title },
        ],
      },
    ],
  }

  return (
    <>
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(jsonLd) }}
      />
      <nav aria-label="Breadcrumb" className="max-w-3xl mx-auto px-6 pt-8 text-sm text-gray-500">
        <ol className="flex items-center gap-2">
          <li><a href="/" className="hover:underline text-green-700">Início</a></li>
          <li aria-hidden="true">/</li>
          <li><a href="/artigos/" className="hover:underline text-green-700">Artigos</a></li>
          <li aria-hidden="true">/</li>
          <li aria-current="page">{post.title}</li>
        </ol>
      </nav>
      <main className="max-w-3xl mx-auto px-6 py-10">
        <h1 className="text-3xl font-bold text-gray-900 mb-4 leading-tight">{post.title}</h1>
        <p className="text-sm text-gray-400 mb-8">{post.date}</p>
        <article
          className="prose prose-gray max-w-none"
          dangerouslySetInnerHTML={{ __html: post.contentHtml }}
        />
      </main>
    </>
  )
}
'''
    wf(SLUG_PATH, ARTICLE_PAGE, f"{SLUG_PATH} — criado com MedicalWebPage + BreadcrumbList")
else:
    sp = rf(SLUG_PATH)
    if 'MedicalWebPage' in sp:
        print("  ℹ️   MedicalWebPage já presente")
    else:
        # Detect what variable holds the post data
        post_var = 'post'
        slug_expr = 'params.slug'
        # Check if page uses 'data', 'article', etc.
        for v in ['post', 'article', 'data']:
            if re.search(rf'\b{v}\b.*title', sp):
                post_var = v
                break

        JSON_LD_CONST = f"""
  const jsonLd = {{
    '@context': 'https://schema.org',
    '@graph': [
      {{
        '@type': 'MedicalWebPage',
        '@id': `https://drguilherme.com/artigos/${{{slug_expr}}}/#webpage`,
        url: `https://drguilherme.com/artigos/${{{slug_expr}}}/`,
        name: {post_var}.title,
        description: {post_var}.excerpt ?? {post_var}.title,
        inLanguage: 'pt-BR',
        author: {{ '@id': 'https://drguilherme.com/#physician' }},
        publisher: {{ '@id': 'https://drguilherme.com/#physician' }},
        reviewedBy: {{ '@id': 'https://drguilherme.com/#physician' }},
        datePublished: {post_var}.date,
        dateModified: {post_var}.date,
      }},
      {{
        '@type': 'BreadcrumbList',
        itemListElement: [
          {{ '@type': 'ListItem', position: 1, name: 'Início', item: 'https://drguilherme.com/' }},
          {{ '@type': 'ListItem', position: 2, name: 'Artigos', item: 'https://drguilherme.com/artigos/' }},
          {{ '@type': 'ListItem', position: 3, name: {post_var}.title }},
        ],
      }},
    ],
  }}

"""

        SCRIPT_TAG = (
            '      <script\n'
            '        type="application/ld+json"\n'
            '        dangerouslySetInnerHTML={{ __html: JSON.stringify(jsonLd) }}\n'
            '      />\n'
        )

        # Insert jsonLd const before the return statement
        sp2 = re.sub(r'(\n  return\s*\()', JSON_LD_CONST + r'\1', sp, count=1)

        # Insert <script> tag as first child of return's JSX (after the first <>  or <main or <div)
        sp2 = re.sub(
            r'(return\s*\(\s*\n\s*<>)',
            r'\1\n' + SCRIPT_TAG,
            sp2, count=1
        )
        # If it uses <main or <article as root, inject after opening tag
        if SCRIPT_TAG not in sp2:
            sp2 = re.sub(
                r'(return\s*\(\s*\n\s*<(?:main|article)\b[^>]*>)',
                r'\1\n' + SCRIPT_TAG,
                sp2, count=1
            )

        if sp2 != sp and 'jsonLd' in sp2:
            wf(SLUG_PATH, sp2, f"{SLUG_PATH} — MedicalWebPage + BreadcrumbList adicionado")
        else:
            print(f"  ⚠️   Inserção automática falhou — adicionar manualmente.")
            print(f"      Cole o bloco abaixo antes do 'return' no componente de página:\n")
            print(textwrap.indent(JSON_LD_CONST.strip(), "      "))
            print(f"\n      E adicione a tag <script> como primeiro filho do JSX retornado:\n")
            print(textwrap.indent(SCRIPT_TAG.strip(), "      "))

# ═══════════════════════════════════════════════════════════════
# 4 — <img> sem width/height (anti-CLS)
# ═══════════════════════════════════════════════════════════════
print("\n[4] <img> sem width/height (anti-CLS)…")
img_issues = []
for dp, _, files in os.walk('src'):
    if any(x in dp for x in ['node_modules', '.next', '.git']):
        continue
    for fn in files:
        if not fn.endswith(('.tsx', '.jsx', '.html')):
            continue
        fp = os.path.join(dp, fn)
        src_text = rf(fp)
        for m in re.finditer(r'<img\b[^>]*/?>|<img\b[^>]*>', src_text):
            tag = m.group(0)
            # Skip Next.js Image component references (already handled)
            if 'next/image' in src_text[:m.start()].split('\n')[-1]:
                continue
            missing = []
            if 'width' not in tag:
                missing.append('width')
            if 'height' not in tag:
                missing.append('height')
            if missing:
                line = src_text[:m.start()].count('\n') + 1
                img_issues.append((fp, line, tag[:100], missing))

if img_issues:
    print(f"  ⚠️   {len(img_issues)} <img> sem dimensões encontrado(s):\n")
    for fp, line, tag, missing in img_issues:
        print(f"    {fp}:{line}")
        print(f"      Tag: {tag}…")
        print(f"      Faltando: {', '.join(missing)}")
        print(f"      Fix: adicionar width={{NNN}} height={{NNN}} ou migrar para <Image> do Next.js\n")
    print("  Dica: use Next.js <Image> com fill + sizes para imagens responsivas:")
    print("    import Image from 'next/image'")
    print("    <Image src='...' alt='...' fill sizes='100vw' />")
else:
    print("  ✅  Nenhum <img> sem dimensões encontrado")

# ═══════════════════════════════════════════════════════════════
# RESUMO
# ═══════════════════════════════════════════════════════════════
print("""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅  Fix Audit #2 concluído.

Confirme as mudanças:
  cd ~/website
  git diff src/app/layout.tsx | head -60

Faça commit e push:
  git add src/app/layout.tsx src/app/artigos/
  git commit -m "seo: CEP 89251-702, geo confirmado, FAQPage 9 perguntas, schema artigos"
  git push
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
""")
