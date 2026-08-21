import json
from pathlib import Path
import datetime
import re

BASE = Path(__file__).parent
DATA = json.loads((BASE / "data.json").read_text(encoding="utf-8"))
OUT = BASE.parent / "chronos-ui" / "public" / "sitemap.xml"

def slug(text):
    return re.sub(r'[^a-z0-9]+', '-', text.lower()).strip('-')

urls = [
    "https://smriti-kaal.vercel.app/",
    "https://smriti-kaal.vercel.app/docs",
    "https://smriti-kaal.vercel.app/dashboard",
    "https://smriti-kaal.vercel.app/integration/supabase-event-memory"
]

for f in DATA.get('frameworks', []):
    urls.append(f"https://smriti-kaal.vercel.app/memory/{slug(f)}")

for u in DATA.get('use_cases', []):
    urls.append(f"https://smriti-kaal.vercel.app/use-case/{slug(u)}")

for p in DATA.get('problems', []):
    urls.append(f"https://smriti-kaal.vercel.app/problem/{slug(p)}")

today = datetime.datetime.utcnow().strftime("%Y-%m-%d")

xml = '<?xml version="1.0" encoding="UTF-8"?>\n'
xml += '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'

for u in urls:
    xml += "  <url>\n"
    xml += f"    <loc>{u}</loc>\n"
    xml += f"    <lastmod>{today}</lastmod>\n"
    xml += "    <changefreq>weekly</changefreq>\n"
    xml += "    <priority>0.8</priority>\n"
    xml += "  </url>\n"

xml += '</urlset>'

OUT.write_text(xml, encoding="utf-8")
print(f"[OK] Generated {OUT}")
