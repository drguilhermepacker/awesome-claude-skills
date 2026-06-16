# Dr. Guilherme Packer — Marketing Site

A production-ready static implementation of the **Dr. Guilherme Packer** marketing
website, built from the Claude Design handoff bundle (`claude.ai/design`). It recreates
the "medical luxury" brand — deep forest green, warm gold, and off-white paper, with
Instrument Serif headlines over Outfit body type.

> Médico de Família e Comunidade · Jaraguá do Sul, SC · Atendimento particular
> CRM-SC 32.148 · RQE 24.101 · Site language: Portuguese (pt-BR)

## Run it

It's a zero-build static site — just open `index.html` in a browser, or serve the
folder:

```bash
cd website
python3 -m http.server 8000
# open http://localhost:8000
```

## Files

- `index.html` — the full landing page (header, hero, about, specialty, clinical
  risk widget, FAQ, contact, footer, floating WhatsApp button).
- `styles.css` — design tokens (colors, type, spacing, radii, shadows, motion) lifted
  verbatim from the design bundle, plus all component and section styles.
- `main.js` — vanilla-JS interactions: sticky glass header, smooth-scroll nav with
  active-section highlighting, the cardiovascular-risk calculator, FAQ accordion,
  scroll-reveal entrance motion, and demo toasts.
- `assets/` — brand imagery (gold "G + stethoscope" monogram, hero/about portraits,
  OG image, favicon).

## Implementation notes

- **Sections** mirror the design's UI kit one-to-one: `Hero`, `About` (wall-green band),
  `Specialty` (three pillars), `RiskWidget`, `FAQ`, and `ContactFooter`.
- **Icons** use **Lucide** (the brand's icon system) loaded from CDN at 1.75 stroke
  weight. Social and WhatsApp glyphs are inline official brand SVGs.
- **Fonts** are Instrument Serif + Outfit from Google Fonts — the exact families the
  production site uses.
- **Motion** is restrained: `fadeUp` entrance reveals on the signature easing
  `cubic-bezier(0.22, 1, 0.36, 1)`, staggered ~80ms, and it respects
  `prefers-reduced-motion`.
- **No emoji**, per brand. Gold is the single accent; status colors appear only inside
  the clinical widget.

## Deploy (Vercel)

This folder is a static site — no build step. To deploy it on Vercel:

1. Import the repo as a new Vercel project.
2. Set **Root Directory = `website`** and Framework Preset = **Other**. This is
   important: it makes Vercel serve *only* this folder. Deploying from the repo
   root would publish the entire skills catalog at your domain.
3. Deploy — Vercel serves `index.html` at `/`.

`vercel.json` (in this folder) sets sensible production defaults: optimized
caching for `assets/` (short max-age with `stale-while-revalidate`, so updated
images still propagate), clean URLs, and basic security headers. It is read only
when Root Directory is `website`, and it does **not** replace step 2.

To put it on a custom domain, add the domain under the project's **Settings →
Domains** and apply the DNS records Vercel shows. Pointing an existing domain
here moves it off whatever project currently serves it.

## Source of truth

The design references the production Next.js app at
[`github.com/drguilhermepacker/website`](https://github.com/drguilhermepacker/website).
This static build is a faithful recreation of the design bundle's website UI kit; to
port it into the Next.js codebase, map each section here to its `src/components/*`
counterpart (`Hero`, `About`, `Header`, `Footer`, `FAQ`, `widgets/CardioRisk`).
