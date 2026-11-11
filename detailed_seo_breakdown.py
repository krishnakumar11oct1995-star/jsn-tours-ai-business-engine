import os
import sys
import glob
from bs4 import BeautifulSoup
import json

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

base_dir = r"C:\Users\Krishna\Downloads\Business\website_hostinger"
html_files = glob.glob(os.path.join(base_dir, "**", "*.html"), recursive=True)
html_files = [f for f in html_files if not os.path.basename(f).startswith("google")]

print(f"DETAILED SEO BREAKDOWN FOR {len(html_files)} PAGES:\n")

for f in sorted(html_files):
    rel = os.path.relpath(f, base_dir).replace("\\", "/")
    with open(f, "r", encoding="utf-8") as fp:
        soup = BeautifulSoup(fp.read(), "html.parser")
    title = soup.find("title").get_text().strip() if soup.find("title") else "N/A"
    desc = soup.find("meta", attrs={"name": "description"})
    desc_text = desc.get("content", "").strip() if desc else "N/A"
    h1 = soup.find("h1").get_text().strip() if soup.find("h1") else "N/A"
    
    scripts = soup.find_all("script", attrs={"type": "application/ld+json"})
    schemas = []
    for s in scripts:
        if s.string:
            try:
                d = json.loads(s.string)
                if isinstance(d, dict):
                    schemas.append(d.get("@type"))
                elif isinstance(d, list):
                    schemas.extend([item.get("@type") for item in d if isinstance(item, dict)])
            except Exception:
                pass
                
    print(f"PAGE: {rel}")
    print(f"  Title ({len(title)}c): {title}")
    print(f"  Desc ({len(desc_text)}c): {desc_text}")
    print(f"  H1: {h1}")
    print(f"  Schemas: {schemas}")
    print("-" * 70)
