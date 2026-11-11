import os
import sys
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

import glob
from bs4 import BeautifulSoup
import json
import xml.etree.ElementTree as ET

base_dir = r"C:\Users\Krishna\Downloads\Business\website_hostinger"
html_files = glob.glob(os.path.join(base_dir, "**", "*.html"), recursive=True)

# Exclude google verification
html_files = [f for f in html_files if not os.path.basename(f).startswith("google")]

print(f"Total HTML pages scanned: {len(html_files)}\n")

audit_results = []
titles_set = {}
descriptions_set = {}
canonical_set = {}

for file_path in html_files:
    rel_path = os.path.relpath(file_path, base_dir).replace("\\", "/")
    with open(file_path, "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f.read(), "html.parser")
    
    title = soup.find("title")
    title_text = title.get_text().strip() if title else ""
    
    meta_desc = soup.find("meta", attrs={"name": "description"})
    meta_desc_text = meta_desc.get("content", "").strip() if meta_desc else ""
    
    canonical = soup.find("link", attrs={"rel": "canonical"})
    canonical_href = canonical.get("href", "").strip() if canonical else ""
    
    h1s = [h.get_text().strip() for h in soup.find_all("h1")]
    h2s = [h.get_text().strip() for h in soup.find_all("h2")]
    h3s = [h.get_text().strip() for h in soup.find_all("h3")]
    
    images = soup.find_all("img")
    missing_alt = [img.get("src") for img in images if not img.get("alt") or img.get("alt").strip() == ""]
    
    # JSON-LD
    scripts = soup.find_all("script", attrs={"type": "application/ld+json"})
    schemas = []
    schema_errors = []
    for s in scripts:
        if s.string:
            try:
                data = json.loads(s.string)
                if isinstance(data, dict):
                    schemas.append(data.get("@type", "unknown"))
                elif isinstance(data, list):
                    for item in data:
                        schemas.append(item.get("@type", "unknown"))
            except Exception as e:
                schema_errors.append(str(e))
                
    # OG tags
    og_title = soup.find("meta", property="og:title")
    og_desc = soup.find("meta", property="og:description")
    og_image = soup.find("meta", property="og:image")
    og_url = soup.find("meta", property="og:url")
    
    # Anchor texts
    links = soup.find_all("a", href=True)
    generic_anchors = []
    for a in links:
        txt = a.get_text().strip().lower()
        if txt in ["click here", "read more", "here", "learn more", "view more"]:
            generic_anchors.append(a.get("href"))
            
    # Track duplicates
    if title_text:
        titles_set.setdefault(title_text, []).append(rel_path)
    if meta_desc_text:
        descriptions_set.setdefault(meta_desc_text, []).append(rel_path)
    if canonical_href:
        canonical_set.setdefault(canonical_href, []).append(rel_path)
        
    audit_results.append({
        "rel_path": rel_path,
        "title": title_text,
        "title_len": len(title_text),
        "desc": meta_desc_text,
        "desc_len": len(meta_desc_text),
        "canonical": canonical_href,
        "h1_count": len(h1s),
        "h1s": h1s,
        "h2_count": len(h2s),
        "h3_count": len(h3s),
        "images_count": len(images),
        "missing_alt_count": len(missing_alt),
        "schemas": schemas,
        "schema_errors": schema_errors,
        "og_title": og_title.get("content") if og_title else None,
        "og_desc": og_desc.get("content") if og_desc else None,
        "og_image": og_image.get("content") if og_image else None,
        "generic_anchors_count": len(generic_anchors)
    })

# Check Robots.txt
robots_path = os.path.join(base_dir, "robots.txt")
robots_exists = os.path.exists(robots_path)
robots_content = ""
if robots_exists:
    with open(robots_path, "r", encoding="utf-8") as f:
        robots_content = f.read()

# Check Sitemap.xml
sitemap_path = os.path.join(base_dir, "sitemap.xml")
sitemap_urls = []
if os.path.exists(sitemap_path):
    tree = ET.parse(sitemap_path)
    root = tree.getroot()
    # Handle namespace
    ns = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}
    for url in root.findall("sm:url", ns):
        loc = url.find("sm:loc", ns)
        if loc is not None and loc.text:
            sitemap_urls.append(loc.text.strip())

# Summary Report Output
print("=" * 80)
print("ECC CLAUDE SEO SKILL AUDIT REPORT: JAI SRIMANNARAYANA (25 PAGES)")
print("=" * 80)
print(f"Total Pages Checked: {len(audit_results)}")
print(f"Sitemap URL Count:   {len(sitemap_urls)}")
print(f"Robots.txt Present:  {robots_exists}")
print("-" * 80)

# Severity evaluations
critical = []
high = []
medium = []
low = []

# Duplicate checks
for t, pages in titles_set.items():
    if len(pages) > 1:
        high.append(f"Duplicate Title Tag across {len(pages)} pages: '{t[:40]}...' -> {pages}")

for d, pages in descriptions_set.items():
    if len(pages) > 1:
        high.append(f"Duplicate Meta Description across {len(pages)} pages -> {pages}")

for c, pages in canonical_set.items():
    if len(pages) > 1:
        critical.append(f"Duplicate Canonical Tag pointing to same target across {pages} -> {c}")

for r in audit_results:
    # Title issues
    if not r["title"]:
        critical.append(f"Missing Title: {r['rel_path']}")
    elif r["title_len"] < 30:
        medium.append(f"Short Title ({r['title_len']} chars): {r['rel_path']} - '{r['title']}'")
    elif r["title_len"] > 65:
        low.append(f"Long Title ({r['title_len']} chars, exceeds 60 target): {r['rel_path']} - '{r['title']}'")
        
    # Meta Description issues
    if not r["desc"]:
        high.append(f"Missing Meta Description: {r['rel_path']}")
    elif r["desc_len"] < 80:
        medium.append(f"Short Meta Description ({r['desc_len']} chars): {r['rel_path']}")
    elif r["desc_len"] > 165:
        low.append(f"Long Meta Description ({r['desc_len']} chars, exceeds 160 target): {r['rel_path']}")
        
    # Canonical
    if not r["canonical"]:
        critical.append(f"Missing Canonical Tag: {r['rel_path']}")
    elif "jaisrimannarayana.netlify.app" not in r["canonical"]:
        high.append(f"Canonical does not match primary domain: {r['rel_path']} -> {r['canonical']}")
        
    # H1 structure
    if r["h1_count"] == 0:
        high.append(f"Missing H1 Tag: {r['rel_path']}")
    elif r["h1_count"] > 1:
        medium.append(f"Multiple ({r['h1_count']}) H1 Tags: {r['rel_path']}")
        
    # Images alt
    if r["missing_alt_count"] > 0:
        medium.append(f"{r['missing_alt_count']} image(s) missing alt attribute: {r['rel_path']}")
        
    # Schema errors
    if r["schema_errors"]:
        critical.append(f"JSON-LD Parsing Error: {r['rel_path']} -> {r['schema_errors']}")
        
    # OpenGraph
    if not r["og_title"] or not r["og_desc"] or not r["og_image"]:
        low.append(f"Incomplete OpenGraph tags: {r['rel_path']} (Title:{bool(r['og_title'])}, Desc:{bool(r['og_desc'])}, Image:{bool(r['og_image'])})")

print(f"\n[CRITICAL ISSUES: {len(critical)}]")
for c in critical:
    print(f"  🚨 {c}")

print(f"\n[HIGH ISSUES: {len(high)}]")
for h in high:
    print(f"  ⚠️  {h}")

print(f"\n[MEDIUM ISSUES: {len(medium)}]")
for m in medium[:15]:
    print(f"  ℹ️  {m}")
if len(medium) > 15:
    print(f"  ... and {len(medium) - 15} more medium issues.")

print(f"\n[LOW / REFINEMENT ISSUES: {len(low)}]")
for l in low[:10]:
    print(f"  ⚡ {l}")
if len(low) > 10:
    print(f"  ... and {len(low) - 10} more low issues.")

print("\n" + "=" * 80)
