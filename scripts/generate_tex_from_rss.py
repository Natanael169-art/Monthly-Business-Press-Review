import csv
import feedparser
from datetime import datetime, timedelta
from jinja2 import Environment, FileSystemLoader
import re
from html import unescape
from bs4 import BeautifulSoup

# Fichiers
CSV_FILE = "client_rss_feeds_cleaned.csv"
TEMPLATE_DIR = "templates"
TEMPLATE_FILE = "press_review_template.tex"
OUTPUT_TEX = "press_review.tex"

# Fonction d’échappement LaTeX
def escape_latex(text):
    if not text:
        return ""
    replacements = {
        '\\': r'\textbackslash{}',
        '&amp;': r'\&amp;',
        '&': r'\&',
        '%': r'\%',
        '$': r'\$',
        '#': r'\#',
        '_': r'\_',
        '{': r'\{',
        '}': r'\}',
        '~': r'\textasciitilde{}',
        '^': r'\^{}'
    }
    regex = re.compile('|'.join(re.escape(key) for key in replacements.keys()))
    return regex.sub(lambda match: replacements[match.group()], text)

# Nettoyage HTML
def clean_html(text):
    if not text:
        return ""
    soup = BeautifulSoup(unescape(text), "html.parser")
    return soup.get_text(separator=" ", strip=True)

# Fenêtre temporelle
now = datetime.utcnow()
seven_days_ago = now - timedelta(days=7)

# Lecture des flux RSS
companies = []
with open(CSV_FILE, newline='', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        company_name = row.get("Company", "Unnamed Company")
        rss_url = row.get("RSS Feed URL", "").strip()

        if not rss_url:
            continue

        feed = feedparser.parse(rss_url)

        recent_articles = []
        for entry in feed.entries:
            pub_date = entry.get("published_parsed") or entry.get("updated_parsed")
            if pub_date:
                pub_datetime = datetime(*pub_date[:6])
                if pub_datetime >= seven_days_ago:
                    title = escape_latex(entry.get("title", "No title"))
                    summary = escape_latex(clean_html(entry.get("summary", "")))
                    published = escape_latex(entry.get("published", "") or entry.get("updated", ""))
                    link = escape_latex(entry.get("link", ""))  # ✅ échappement ajouté

                    recent_articles.append({
                        "title": title,
                        "summary": summary,
                        "published": published,
                        "link": link
                    })

        if recent_articles:
            print(f"✅ {company_name}: {len(recent_articles)} article(s) trouvé(s)")
            companies.append({
                "company": escape_latex(company_name),
                "articles": recent_articles[:5]
            })
        else:
            print(f"⚠️ {company_name}: aucun article trouvé")

# Rendu LaTeX
env = Environment(loader=FileSystemLoader(TEMPLATE_DIR))
template = env.get_template(TEMPLATE_FILE)

rendered_tex = template.render(
    generated_date=now.strftime("%Y-%m-%d"),
    companies=companies
)

# Écriture du fichier .tex
with open(OUTPUT_TEX, "w", encoding="utf-8") as f:
    f.write(rendered_tex)

print(f"\n✅ Fichier LaTeX généré : {OUTPUT_TEX}")
