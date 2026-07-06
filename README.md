# riesictadvies.nl

Statische website voor Ries ICT Advies, een informatieplatform over cloudopslag en databeveiliging. Frameworkloos gebouwd met Python en Jinja2, geschikt voor deployment via Cloudflare Pages of GitHub Pages.

## Structuur

```
build.py                 Static site generator
requirements.txt         Python-dependencies
templates/               Jinja2-templates (base, home, page-templates, article)
content/articles/        Nieuwsartikelen als markdown met YAML-frontmatter
static/                  CSS, favicon en overige assets
public/                  Build-output (wordt gegenereerd, niet in versiebeheer)
```

## Lokaal bouwen

```bash
pip install -r requirements.txt
python build.py
```

De output verschijnt in `public/`. Lokaal bekijken kan met een eenvoudige webserver:

```bash
cd public && python -m http.server 8000
```

## Nieuw artikel toevoegen

Plaats een markdown-bestand in `content/articles/` met frontmatter:

```markdown
---
title: "Titel van het artikel"
description: "Korte omschrijving voor zoekmachines en previews."
date: 2026-01-15
category: "Basiskennis"
reading_time: 5
---

De inhoud in markdown.
```

De bestandsnaam bepaalt de URL: `wat-is-cloudopslag.md` wordt `/nieuws/wat-is-cloudopslag/`. Na `python build.py` staat het artikel in de nieuwsindex, op de homepage en in de sitemap.

## Deployment via Cloudflare Pages

Twee werkwijzen zijn mogelijk.

### A. Bouwen op Cloudflare (aanbevolen)

Koppel de GitHub-repository aan een Cloudflare Pages-project en stel in:

- Build command: `pip install -r requirements.txt && python build.py`
- Build output directory: `public`
- Python-versie: 3.x (via omgevingsvariabele `PYTHON_VERSION`, bijvoorbeeld `3.12`)

Bij iedere push naar de hoofdbranch bouwt Cloudflare de site opnieuw.

### B. Vooraf bouwen en committen

Verwijder `public/` uit `.gitignore`, voer lokaal `python build.py` uit en commit de map. Stel in Cloudflare Pages het build command leeg in en de output directory op `public`.

## Deployment via GitHub Pages

Bouw lokaal, plaats de inhoud van `public/` op de `gh-pages`-branch of gebruik een GitHub Action die `python build.py` draait en `public/` publiceert.

## Domein

Productie: `https://riesictadvies.nl`. Pas de waarde `SITE["url"]` in `build.py` aan wanneer het domein wijzigt; die waarde bepaalt de canonical-tags en de sitemap.
