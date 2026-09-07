# TK1104 - course script (Quarto)

Quarto book project for the TK1104 *Digital Technology* lecture script,
set up like the SKY2100 course script (`tamling/SKY2100`): One chapter per
lecture, rendered as an HTML book - and **every page has a dark mode**
(light/dark theme toggle in the navbar, configured in `_quarto.yml`).

```
_quarto.yml               project config; light/dark themes; annotations flag (ON)
includes/hypothesis.html  the Hypothesis embed snippet (header include)
index.qmd                 book landing page (the script's preface)
chapters/                 one NN-name.qmd per lecture (1–11)
chapters/figures/         pre-built SVG figures (committed)
_tikz/                    TikZ sources for the figures + build.sh → chapters/figures/*.svg
appendix/                 abbreviations, revision history
theme.scss                shared course styling (didactic bridges)
theme-dark.scss           dark-mode fixes (light backing card behind figures)
.github/workflows/        publish.yml - quarto render → GitHub Pages
```

Render: `quarto render`. The dark mode needs no build step - Quarto
renders the theme toggle on every page from the `theme.light`/`theme.dark`
pair in `_quarto.yml`.

## Figures

The diagrams are TikZ, kept as sources in `_tikz/fig-*.tikz` and committed
as SVGs under `chapters/figures/`, so rendering the book needs no LaTeX.
To rebuild after editing a source:

```
_tikz/build.sh   # needs pdflatex + TikZ, pdfcrop, pdftocairo (poppler)
```

In dark mode the SVGs (dark ink, transparent background) sit on a light
backing card - see `theme-dark.scss`.

## Password protection

The published site is password-protected: the publish workflow encrypts
every rendered page with [StatiCrypt](https://github.com/robinmoisson/staticrypt)
(AES-256; "remember me" keeps a browser unlocked for 30 days) and removes
the plain-text `search.json` (search is disabled in `_quarto.yml` for the
same reason). The default password lives in
`.github/workflows/publish.yml`; add a repository secret named
`STATICRYPT_PASSWORD` to override it without a code change. Note that
this protects the *site* only - while the repository is public, the
sources remain readable; make the repository private for real
confidentiality.

## Conventions carried over from the LaTeX script

* Numbered **definitions**, **examples** and **exercises** (Quarto theorem
  blocks `#def-…`, `#exm-…`, `#exr-…`); every concept is defined once,
  before it is used.
* Grey **Excursus** callouts: Enrichment from the classic textbooks
  (Tanenbaum et al.) - background, not exam material.
* Blue **Worked exercise** callouts: Small tasks with compact solutions,
  next to the technique they practise.
* Each chapter ends with a **Self-check** (sketch answers in a collapsed
  box) and a *bridge* paragraph linking it to the next chapter.
