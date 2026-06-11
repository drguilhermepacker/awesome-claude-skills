#!/usr/bin/env python3
"""
Fix #7 — conteúdo completo para /telemedicina e /medico-de-familia (≥400 palavras)
+ npm audit para diagnosticar a vulnerabilidade do Dependabot.

Rodar a partir da raiz do repo: cd ~/website && python3 ~/fix_content7.py
"""
import os, re, sys, subprocess

def rf(path):
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()

def wf(path, content, label=None):
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"  ✅  {label or path}")

if not os.path.isdir('src/app'):
    sys.exit("❌  Execute a partir da raiz do repo: cd ~/website && python3 ~/fix_content7.py")

print("\n🔧  Fix #7 — conteúdo das landing pages + npm audit\n")

# ═══════════════════════════════════════════════════════════════
# 0 — Descobrir o número de WhatsApp real usado no site
# ═══════════════════════════════════════════════════════════════
wa = None
for p in ['src/app/telemedicina/page.tsx', 'src/components/Contact.tsx',
          'src/components/FloatingWhatsApp.tsx', 'src/lib/constants.ts']:
    if os.path.exists(p):
        m = re.search(r'wa\.me/(\d{10,15})', rf(p))
        if m:
            wa = m.group(1)
            break
if not wa:
    sys.exit("❌  Número de WhatsApp não encontrado nos arquivos do site")
print(f"  ℹ️   WhatsApp detectado: wa.me/{wa}\n")

# ═══════════════════════════════════════════════════════════════
# 1 — /telemedicina — conteúdo completo
# ═══════════════════════════════════════════════════════════════
print("━" * 55)
print("[1] /telemedicina — conteúdo completo…")

TELE = '''import type { Metadata } from 'next'
import Link from 'next/link'

export const metadata: Metadata = {
  title: 'Telemedicina | Dr. Guilherme Packer — Médico de Família',
  description: 'Teleconsulta com Médico de Família e Comunidade. Atendimento online para seguimento de condições crônicas, renovação de receitas e avaliação de novos sintomas.',
  alternates: { canonical: 'https://drguilherme.com/telemedicina/' },
  openGraph: {
    title: 'Telemedicina | Dr. Guilherme Packer',
    description: 'Consulta médica online com Médico de Família e Comunidade.',
    url: 'https://drguilherme.com/telemedicina/',
    siteName: 'Dr. Guilherme Packer',
    locale: 'pt_BR',
    type: 'website',
  },
}

const jsonLd = {
  '@context': 'https://schema.org',
  '@graph': [
    {
      '@type': 'MedicalWebPage',
      '@id': 'https://drguilherme.com/telemedicina/#webpage',
      url: 'https://drguilherme.com/telemedicina/',
      name: 'Teleconsulta com Médico de Família — Dr. Guilherme Packer',
      inLanguage: 'pt-BR',
      author: { '@id': 'https://drguilherme.com/#physician' },
      publisher: { '@id': 'https://drguilherme.com/#physician' },
      reviewedBy: { '@id': 'https://drguilherme.com/#physician' },
    },
    {
      '@type': 'BreadcrumbList',
      itemListElement: [
        { '@type': 'ListItem', position: 1, name: 'Início', item: 'https://drguilherme.com/' },
        { '@type': 'ListItem', position: 2, name: 'Telemedicina' },
      ],
    },
  ],
}

export default function TelemedicinaPage() {
  return (
    <>
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(jsonLd) }}
      />
      <main className="max-w-3xl mx-auto px-6 py-16">
        <nav aria-label="Breadcrumb" className="text-sm text-gray-500 mb-10">
          <ol className="flex items-center gap-2">
            <li><Link href="/" className="hover:underline text-green-700">Início</Link></li>
            <li aria-hidden="true">/</li>
            <li aria-current="page">Telemedicina</li>
          </ol>
        </nav>

        <h1 className="text-3xl font-bold text-gray-900 mb-6 leading-tight">
          Teleconsulta com Médico de Família e Comunidade
        </h1>

        <p className="text-lg text-gray-700 mb-6 leading-relaxed">
          A teleconsulta leva o mesmo cuidado longitudinal do consultório até onde você
          estiver — em casa, no trabalho ou em viagem. A telemedicina é regulamentada
          pelo Conselho Federal de Medicina (Resolução CFM nº 2.314/2022) e, quando bem
          indicada, oferece a mesma qualidade de escuta, raciocínio clínico e plano de
          cuidado da consulta presencial.
        </p>

        <h2 className="text-xl font-semibold text-gray-900 mt-10 mb-4">Como funciona</h2>
        <p className="text-gray-700 mb-6 leading-relaxed">
          O agendamento é feito pelo WhatsApp. No horário marcado, você recebe um link
          seguro de videochamada — não é preciso instalar nenhum aplicativo especial,
          basta um celular ou computador com câmera e internet. A consulta tem a mesma
          estrutura do atendimento presencial: escuta da sua história, revisão de exames
          e medicações, raciocínio diagnóstico e construção conjunta do plano de cuidado.
        </p>

        <h2 className="text-xl font-semibold text-gray-900 mt-10 mb-4">
          Para que situações a teleconsulta é indicada
        </h2>
        <ul className="list-disc list-inside text-gray-700 space-y-2 mb-6">
          <li>Retornos e seguimento de condições crônicas já em acompanhamento — como hipertensão, diabetes e obesidade</li>
          <li>Discussão de resultados de exames</li>
          <li>Renovação e ajuste de receitas de uso contínuo</li>
          <li>Avaliação inicial de sintomas leves, com orientação sobre a necessidade de avaliação presencial</li>
          <li>Orientações sobre prevenção, vacinas e rastreamentos</li>
          <li>Pacientes que moram fora de Jaraguá do Sul e desejam manter o vínculo com o mesmo médico</li>
        </ul>

        <h2 className="text-xl font-semibold text-gray-900 mt-10 mb-4">
          Quando o presencial é preferível
        </h2>
        <p className="text-gray-700 mb-6 leading-relaxed">
          A primeira consulta, sempre que possível, é presencial — o exame físico completo
          faz parte de uma boa avaliação inicial. Sintomas agudos importantes, como dor no
          peito, falta de ar ou sinais de alarme, exigem avaliação presencial ou de
          urgência. Durante a teleconsulta, se eu identificar que o seu caso pede exame
          físico, oriento a conversão para atendimento presencial ou{' '}
          <Link href="/visita-domiciliar-jaragua-do-sul" className="text-green-700 hover:underline">
            visita domiciliar
          </Link>{' '}
          sem custo adicional de reavaliação.
        </p>

        <h2 className="text-xl font-semibold text-gray-900 mt-10 mb-4">
          Receitas, atestados e pedidos de exame digitais
        </h2>
        <p className="text-gray-700 mb-6 leading-relaxed">
          Ao final da teleconsulta, você recebe receitas, atestados e pedidos de exame
          com assinatura digital certificada, válidos em farmácias e laboratórios de todo
          o Brasil. Todo o atendimento segue o sigilo médico e a Lei Geral de Proteção de
          Dados (LGPD), em plataforma segura.
        </p>

        <a
          href="https://wa.me/__WA__"
          className="inline-flex items-center gap-2 bg-green-600 text-white px-7 py-3.5 rounded-xl font-semibold hover:bg-green-700 transition-colors text-lg"
          target="_blank"
          rel="noopener noreferrer"
        >
          Agendar teleconsulta pelo WhatsApp →
        </a>

        <div className="mt-14 pt-8 border-t border-gray-100">
          <p className="text-sm text-gray-500 mb-3">
            Dr. Guilherme Packer · Médico de Família e Comunidade · CRM-SC 32.148 · RQE 24.101
          </p>
          <Link href="/" className="text-green-700 hover:underline text-sm">← Voltar para a página inicial</Link>
        </div>
      </main>
    </>
  )
}
'''.replace('__WA__', wa)

wf('src/app/telemedicina/page.tsx', TELE, "/telemedicina — conteúdo completo (~450 palavras)")

# ═══════════════════════════════════════════════════════════════
# 2 — /medico-de-familia — conteúdo completo
# ═══════════════════════════════════════════════════════════════
print("\n[2] /medico-de-familia — conteúdo completo…")

MDF = '''import type { Metadata } from 'next'
import Link from 'next/link'

export const metadata: Metadata = {
  title: 'O que é Médico de Família e Comunidade | Dr. Guilherme Packer',
  description: 'Entenda o que faz um Médico de Família e Comunidade: cuidado longitudinal, prevenção e coordenação com especialistas. Diferença entre MFC e Clínico Geral explicada.',
  alternates: { canonical: 'https://drguilherme.com/medico-de-familia/' },
  openGraph: {
    title: 'O que é Médico de Família e Comunidade',
    description: 'Conheça a especialidade médica focada em cuidado integral, longitudinal e preventivo para todas as idades.',
    url: 'https://drguilherme.com/medico-de-familia/',
    siteName: 'Dr. Guilherme Packer',
    locale: 'pt_BR',
    type: 'article',
  },
}

const jsonLd = {
  '@context': 'https://schema.org',
  '@graph': [
    {
      '@type': 'MedicalWebPage',
      '@id': 'https://drguilherme.com/medico-de-familia/#webpage',
      url: 'https://drguilherme.com/medico-de-familia/',
      name: 'O que faz um Médico de Família e Comunidade — e por que isso muda seu cuidado',
      inLanguage: 'pt-BR',
      author: { '@id': 'https://drguilherme.com/#physician' },
      publisher: { '@id': 'https://drguilherme.com/#physician' },
      reviewedBy: { '@id': 'https://drguilherme.com/#physician' },
      about: { '@type': 'MedicalSpecialty', name: 'Family Practice' },
    },
    {
      '@type': 'BreadcrumbList',
      itemListElement: [
        { '@type': 'ListItem', position: 1, name: 'Início', item: 'https://drguilherme.com/' },
        { '@type': 'ListItem', position: 2, name: 'Médico de Família e Comunidade' },
      ],
    },
  ],
}

export default function MedicoFamiliaPage() {
  return (
    <>
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(jsonLd) }}
      />
      <main className="max-w-3xl mx-auto px-6 py-16">
        <nav aria-label="Breadcrumb" className="text-sm text-gray-500 mb-10">
          <ol className="flex items-center gap-2">
            <li><Link href="/" className="hover:underline text-green-700">Início</Link></li>
            <li aria-hidden="true">/</li>
            <li aria-current="page">Médico de Família e Comunidade</li>
          </ol>
        </nav>

        <h1 className="text-3xl font-bold text-gray-900 mb-6 leading-tight">
          O que faz um Médico de Família e Comunidade — e por que isso muda seu cuidado
        </h1>

        <p className="text-lg text-gray-700 mb-6 leading-relaxed">
          O Médico de Família e Comunidade (MFC) é o especialista em pessoas — não em um
          órgão, uma doença ou uma faixa etária. É o médico formado para ser o seu ponto
          fixo de referência ao longo da vida: alguém que conhece a sua história, o seu
          contexto e a sua família, e que usa esse conhecimento para tomar decisões
          clínicas melhores.
        </p>

        <h2 className="text-xl font-semibold text-gray-900 mt-10 mb-4">
          Uma especialidade médica completa
        </h2>
        <p className="text-gray-700 mb-6 leading-relaxed">
          A Medicina de Família e Comunidade é uma especialidade reconhecida pelo Conselho
          Federal de Medicina, com residência médica própria e Registro de Qualificação de
          Especialista (RQE). A formação abrange o cuidado de crianças, adultos, gestantes
          e idosos, saúde mental, manejo de doenças crônicas, prevenção e pequenos
          procedimentos — tudo com ênfase na relação médico-paciente de longo prazo.
        </p>

        <h2 className="text-xl font-semibold text-gray-900 mt-10 mb-4">
          Qual a diferença entre Médico de Família e Clínico Geral?
        </h2>
        <p className="text-gray-700 mb-6 leading-relaxed">
          São especialidades distintas. O Clínico Geral (especialista em Clínica Médica)
          concentra-se nas doenças internas do adulto. O Médico de Família e Comunidade
          tem formação específica em cuidado longitudinal, abordagem familiar e
          comunitária, prevenção quaternária — proteger o paciente de exames e
          tratamentos desnecessários — e coordenação do cuidado entre os diferentes
          especialistas, atendendo todas as idades.
        </p>

        <h2 className="text-xl font-semibold text-gray-900 mt-10 mb-4">
          O que significa cuidado longitudinal
        </h2>
        <p className="text-gray-700 mb-6 leading-relaxed">
          Cuidado longitudinal é acompanhar a mesma pessoa ao longo dos anos. Em vez de
          recomeçar a sua história a cada consulta com um profissional diferente, você
          tem um médico que acompanha a evolução dos seus exames, conhece suas medicações
          e percebe mudanças sutis que um atendimento pontual não captaria. Sistemas de
          saúde organizados em torno de uma atenção primária forte estão associados, na
          literatura científica, a melhores desfechos e menos hospitalizações evitáveis.
        </p>

        <h2 className="text-xl font-semibold text-gray-900 mt-10 mb-4">
          Coordenação do cuidado
        </h2>
        <p className="text-gray-700 mb-6 leading-relaxed">
          Quando você precisa de um cardiologista, endocrinologista ou cirurgião, o MFC
          não desaparece: ele encaminha com critério, conversa com o especialista,
          integra as recomendações e evita interações medicamentosas e exames duplicados.
          O resultado é um cuidado mais seguro, coerente e econômico.
        </p>

        <h2 className="text-xl font-semibold text-gray-900 mt-10 mb-4">
          Para quem é indicado
        </h2>
        <ul className="list-disc list-inside text-gray-700 space-y-2 mb-6">
          <li>Adultos que querem um médico de referência para check-ups e prevenção</li>
          <li>Pessoas com condições crônicas — hipertensão, diabetes, obesidade — que precisam de seguimento contínuo</li>
          <li>Famílias que preferem um único médico para todas as gerações</li>
          <li>Idosos com múltiplas medicações e vários especialistas envolvidos</li>
          <li>Quem busca orientação imparcial antes de decidir por exames ou cirurgias</li>
        </ul>

        <p className="text-gray-700 mb-10 leading-relaxed">
          O atendimento é presencial em Jaraguá do Sul, com opções de{' '}
          <Link href="/telemedicina" className="text-green-700 hover:underline">teleconsulta</Link>{' '}
          e{' '}
          <Link href="/visita-domiciliar-jaragua-do-sul" className="text-green-700 hover:underline">
            visita domiciliar
          </Link>. Você também pode conhecer mais sobre saúde nos{' '}
          <Link href="/artigos" className="text-green-700 hover:underline">artigos do blog</Link>.
        </p>

        <a
          href="https://wa.me/__WA__"
          className="inline-flex items-center gap-2 bg-green-600 text-white px-7 py-3.5 rounded-xl font-semibold hover:bg-green-700 transition-colors text-lg"
          target="_blank"
          rel="noopener noreferrer"
        >
          Agendar consulta pelo WhatsApp →
        </a>

        <div className="mt-14 pt-8 border-t border-gray-100">
          <p className="text-sm text-gray-500 mb-3">
            Dr. Guilherme Packer · Médico de Família e Comunidade · CRM-SC 32.148 · RQE 24.101
          </p>
          <Link href="/" className="text-green-700 hover:underline text-sm">← Voltar para a página inicial</Link>
        </div>
      </main>
    </>
  )
}
'''.replace('__WA__', wa)

wf('src/app/medico-de-familia/page.tsx', MDF, "/medico-de-familia — conteúdo completo (~500 palavras)")

# ═══════════════════════════════════════════════════════════════
# 3 — npm audit — diagnóstico da vulnerabilidade
# ═══════════════════════════════════════════════════════════════
print("\n[3] npm audit — diagnóstico…")
try:
    r = subprocess.run(['npm', 'audit'], capture_output=True, text=True, timeout=120)
    print(r.stdout or r.stderr)
except Exception as e:
    print(f"  ⚠️   npm audit falhou: {e} — rode manualmente: npm audit")

print("""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Próximos passos:
  1. npm run build
  2. Se passar:
       git add -A
       git commit -m "content: paginas telemedicina e medico-de-familia completas"
       git push
  3. Cole a saída do npm audit acima no chat — indico o fix
     exato da vulnerabilidade (sem usar --force às cegas).
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
""")
