#!/usr/bin/env python3
"""Static site generator voor riesictadvies.nl.

Frameworkloos: Jinja2 + python-markdown. Artikelen zijn markdown-bestanden
met YAML-frontmatter in content/articles/. De output komt in public/ en is
geschikt voor deployment via Cloudflare Pages of GitHub Pages.

Gebruik: python build.py
"""

import shutil
from datetime import datetime, date
from pathlib import Path

import frontmatter
import markdown
from jinja2 import Environment, FileSystemLoader, select_autoescape

ROOT = Path(__file__).parent
TEMPLATES = ROOT / "templates"
CONTENT = ROOT / "content" / "articles"
STATIC = ROOT / "static"
OUTPUT = ROOT / "public"

SITE = {
    "name": "Ries ICT Advies",
    "url": "https://riesictadvies.nl",
    "description": "Onafhankelijk informatieplatform over cloudopslag en databeveiliging voor Nederlandse ondernemers.",
}

NAV = [
    {"label": "Home", "url": "/"},
    {"label": "Over", "url": "/over/"},
    {"label": "Cloudopslag", "url": "/cloudopslag/"},
    {"label": "Nieuws", "url": "/nieuws/"},
    {"label": "Contact", "url": "/contact/"},
]

MONTHS_NL = [
    "januari", "februari", "maart", "april", "mei", "juni",
    "juli", "augustus", "september", "oktober", "november", "december",
]

env = Environment(
    loader=FileSystemLoader(str(TEMPLATES)),
    autoescape=select_autoescape(["html"]),
    trim_blocks=True,
    lstrip_blocks=True,
)

md = markdown.Markdown(extensions=["extra", "sane_lists"])


def nl_date(d: date) -> str:
    return f"{d.day} {MONTHS_NL[d.month - 1]} {d.year}"


def load_articles():
    articles = []
    for path in sorted(CONTENT.glob("*.md")):
        post = frontmatter.load(path)
        slug = path.stem
        d = post["date"]
        if isinstance(d, datetime):
            d = d.date()
        md.reset()
        html = md.convert(post.content)
        articles.append({
            "slug": slug,
            "title": post["title"],
            "description": post["description"],
            "category": post.get("category", "Nieuws"),
            "reading_time": post.get("reading_time", 5),
            "date": d,
            "date_display": nl_date(d),
            "date_iso": d.isoformat(),
            "url": f"/nieuws/{slug}/",
            "html": html,
        })
    articles.sort(key=lambda a: a["date"], reverse=True)
    return articles


def write(rel_path: str, html: str):
    out = OUTPUT / rel_path.lstrip("/")
    out.mkdir(parents=True, exist_ok=True)
    (out / "index.html").write_text(html, encoding="utf-8")


def render(template: str, page_path: str, active: str, **ctx):
    tpl = env.get_template(template)
    return tpl.render(
        site=SITE,
        nav=NAV,
        active=active,
        page_path=page_path,
        year=datetime.now().year,
        legal_date=nl_date(date.today()),
        **ctx,
    )


def related_for(article, articles, count=3):
    same = [a for a in articles if a["slug"] != article["slug"] and a["category"] == article["category"]]
    others = [a for a in articles if a["slug"] != article["slug"] and a["category"] != article["category"]]
    return (same + others)[:count]


def build():
    if OUTPUT.exists():
        shutil.rmtree(OUTPUT)
    OUTPUT.mkdir(parents=True)

    # static assets
    shutil.copytree(STATIC, OUTPUT / "static")

    articles = load_articles()

    # home
    write("/", render("home.html", "/", "/", latest=articles[:3]))

    # over
    write("/over/", render("over.html", "/over/", "/over/"))

    # cloudopslag
    write("/cloudopslag/", render("cloudopslag.html", "/cloudopslag/", "/cloudopslag/"))

    # contact
    write("/contact/", render("contact.html", "/contact/", "/contact/"))

    # legal
    write("/privacybeleid/", render("privacybeleid.html", "/privacybeleid/", None))
    write("/cookiebeleid/", render("cookiebeleid.html", "/cookiebeleid/", None))

    # nieuws index
    write("/nieuws/", render("news.html", "/nieuws/", "/nieuws/", articles=articles))

    # artikelen
    for a in articles:
        write(a["url"], render(
            "article.html", a["url"], "/nieuws/",
            article=a, related=related_for(a, articles),
        ))

    # sitemap + robots
    write_sitemap(articles)
    write_robots()

    print(f"Gebouwd: {len(articles)} artikelen, output in {OUTPUT}")


def write_sitemap(articles):
    urls = ["/", "/over/", "/cloudopslag/", "/nieuws/", "/contact/",
            "/privacybeleid/", "/cookiebeleid/"]
    urls += [a["url"] for a in articles]
    today = date.today().isoformat()
    lastmod = {a["url"]: a["date_iso"] for a in articles}
    lines = ['<?xml version="1.0" encoding="UTF-8"?>',
             '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for u in urls:
        lines.append("  <url>")
        lines.append(f"    <loc>{SITE['url']}{u}</loc>")
        lines.append(f"    <lastmod>{lastmod.get(u, today)}</lastmod>")
        lines.append("  </url>")
    lines.append("</urlset>")
    (OUTPUT / "sitemap.xml").write_text("\n".join(lines), encoding="utf-8")


def write_robots():
    content = (
        "User-agent: *\n"
        "Allow: /\n\n"
        f"Sitemap: {SITE['url']}/sitemap.xml\n"
    )
    (OUTPUT / "robots.txt").write_text(content, encoding="utf-8")


if __name__ == "__main__":
    build()
