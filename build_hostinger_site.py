"""
Hostinger Static Site Generator for Jai Srimannarayana Tours & Travels.

This script bakes the entire FastAPI/Jinja2 site into a production-ready,
standalone static website folder (`website_hostinger/`) that can be uploaded
directly into Hostinger's `public_html` directory via hPanel or FTP.

Outputs:
1. `website_hostinger/` folder with complete nested directory structure:
   - index.html
   - calculator/index.html
   - destinations/index.html
   - destinations/<country>/index.html
   - destinations/<country>/<state>/index.html
   - destinations/<country>/<state>/<place>/index.html
   - static/ (video, poster, etc.)
   - data/destinations.json
   - .htaccess (Hostinger Apache/LiteSpeed routing, caching, gzip)
   - robots.txt
   - sitemap.xml
2. `website_hostinger.zip` ready for 1-click upload and extraction in Hostinger File Manager.
"""

import os
import shutil
import zipfile
import json
import re
from jinja2 import Environment, FileSystemLoader
from sqlalchemy.orm import joinedload
from database import SessionLocal, Country, State, Place

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATES_DIR = os.path.join(BASE_DIR, "templates")
STATIC_DIR = os.path.join(BASE_DIR, "static")
OUTPUT_DIR = os.path.join(BASE_DIR, "website_hostinger")
ZIP_OUTPUT = os.path.join(BASE_DIR, "website_hostinger.zip")

# Active Live Site URL
DEFAULT_SITE_URL = os.getenv("SITE_URL", "https://jaisrimannarayana.netlify.app")


def build_site():
    print("=" * 70)
    print("[BUILD] BUILDING HOSTINGER DEPLOYMENT PACKAGE FOR JAI SRIMANNARAYANA")
    print("=" * 70)

    # 1. Clean and initialize output folder
    if os.path.exists(OUTPUT_DIR):
        def _handle_remove_readonly(func, path, exc):
            import stat
            try:
                os.chmod(path, stat.S_IWRITE)
                func(path)
            except Exception:
                pass

        try:
            shutil.rmtree(OUTPUT_DIR, onexc=_handle_remove_readonly)
        except TypeError:
            shutil.rmtree(OUTPUT_DIR, onerror=_handle_remove_readonly)
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    print(f"[INIT] Output directory: {OUTPUT_DIR}")

    # 2. Setup Jinja2 Environment
    env = Environment(loader=FileSystemLoader(TEMPLATES_DIR), autoescape=True)

    # Database session
    db = SessionLocal()

    try:
        # Fetch data
        countries = db.query(Country).options(joinedload(Country.states).joinedload(State.places)).all()
        places = db.query(Place).join(State).join(Country).all()

        sitemap_urls = []

        def convert_static_url(url: str, root_prefix: str) -> str:
            """Converts root-relative paths (/destinations, /calculator, /) to portable relative paths."""
            if url.startswith(("http://", "https://", "tel:", "mailto:", "javascript:", "#")) or url.startswith("//"):
                return url
            if url == "/":
                return f"{root_prefix}index.html" if root_prefix else "index.html"
            if url.startswith("/static/"):
                return f"{root_prefix}{url[1:]}"
            if url.startswith("/data/"):
                return f"{root_prefix}{url[1:]}"
            clean = url.lstrip("/")
            if clean.endswith((".html", ".jpg", ".jpeg", ".png", ".webp", ".mp4", ".css", ".js", ".json", ".xml", ".txt")):
                return f"{root_prefix}{clean}"
            clean = clean.rstrip("/")
            return f"{root_prefix}{clean}/index.html"

        def rewrite_html_for_static(html: str, rel_path: str) -> str:
            """Rewrites root-relative URLs in href, src, poster to relative paths for local and web server portability."""
            norm_path = rel_path.replace("\\", "/")
            dirname = os.path.dirname(norm_path)
            depth = len(dirname.split("/")) if dirname else 0
            root_prefix = "../" * depth if depth > 0 else ""

            def repl(match):
                attr = match.group(1)
                url = match.group(2)
                if url.startswith("/") and not url.startswith("//"):
                    new_url = convert_static_url(url, root_prefix)
                    return f'{attr}="{new_url}"'
                return match.group(0)

            pattern = re.compile(r'(href|src|poster|action)=["\'](/[^"\'\s]*)["\']')
            return pattern.sub(repl, html)

        def save_page(rel_path, html_content):
            """Saves html_content into website_hostinger/<rel_path> with portable relative links."""
            full_path = os.path.join(OUTPUT_DIR, rel_path)
            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            portable_html = rewrite_html_for_static(html_content, rel_path)
            with open(full_path, "w", encoding="utf-8") as f:
                f.write(portable_html)
            print(f"  [PAGE] Rendered: {rel_path}")

        # -------------------------------------------------------------
        # A. Render Homepage (index.html)
        # -------------------------------------------------------------
        home_tmpl = env.get_template("index.html")
        home_html = home_tmpl.render(places=places)
        save_page("index.html", home_html)
        sitemap_urls.append("")

        # -------------------------------------------------------------
        # B. Render Destinations Directory (destinations/index.html)
        # -------------------------------------------------------------
        dest_tmpl = env.get_template("destinations.html")
        dest_html = dest_tmpl.render(countries=countries)
        save_page(os.path.join("destinations", "index.html"), dest_html)
        sitemap_urls.append("destinations")

        # -------------------------------------------------------------
        # C. Render Budget Calculator (calculator/index.html)
        # -------------------------------------------------------------
        calc_tmpl = env.get_template("calculator.html")
        calc_html = calc_tmpl.render(places=places)
        save_page(os.path.join("calculator", "index.html"), calc_html)
        sitemap_urls.append("calculator")

        # -------------------------------------------------------------
        # C1. Render Tour Packages
        # -------------------------------------------------------------
        pkg_tmpl = env.get_template("package_kashi_ayodhya.html")
        pkg_html = pkg_tmpl.render()
        save_page(os.path.join("packages", "kashi-prayagraj-ayodhya", "index.html"), pkg_html)
        sitemap_urls.append("packages/kashi-prayagraj-ayodhya")

        diwali_tmpl = env.get_template("package_diwali_dev_deepavali.html")
        diwali_html = diwali_tmpl.render()
        save_page(os.path.join("packages", "diwali-dev-deepavali", "index.html"), diwali_html)
        sitemap_urls.append("packages/diwali-dev-deepavali")

        ram_tmpl = env.get_template("package_rameswaram_south_india.html")
        ram_html = ram_tmpl.render()
        save_page(os.path.join("packages", "rameswaram-madurai-kanyakumari", "index.html"), ram_html)
        sitemap_urls.append("packages/rameswaram-madurai-kanyakumari")

        jyotirlinga_tmpl = env.get_template("package_7jyotirlingas_5dwarakas.html")
        jyotirlinga_html = jyotirlinga_tmpl.render()
        save_page(os.path.join("packages", "7-jyotirlingas-5-dwarakas", "index.html"), jyotirlinga_html)
        sitemap_urls.append("packages/7-jyotirlingas-5-dwarakas")

        # -------------------------------------------------------------
        # C2. Render About & Contact Pages
        # -------------------------------------------------------------
        about_tmpl = env.get_template("about.html")
        about_html = about_tmpl.render()
        save_page(os.path.join("about", "index.html"), about_html)
        sitemap_urls.append("about")

        contact_tmpl = env.get_template("contact.html")
        contact_html = contact_tmpl.render()
        save_page(os.path.join("contact", "index.html"), contact_html)
        sitemap_urls.append("contact")

        # -------------------------------------------------------------
        # D. Render Country, State, and Place Detail Pages
        # -------------------------------------------------------------
        country_tmpl = env.get_template("country.html")
        state_tmpl = env.get_template("state.html")
        place_tmpl = env.get_template("place_detail.html")

        for country in countries:
            # Country page
            c_html = country_tmpl.render(country=country)
            save_page(os.path.join("destinations", country.slug, "index.html"), c_html)
            sitemap_urls.append(f"destinations/{country.slug}")

            for state in country.states:
                # State page
                s_html = state_tmpl.render(state=state)
                save_page(os.path.join("destinations", country.slug, state.slug, "index.html"), s_html)
                sitemap_urls.append(f"destinations/{country.slug}/{state.slug}")

                for place in state.places:
                    # Place page
                    p_html = place_tmpl.render(place=place)
                    save_page(
                        os.path.join("destinations", country.slug, state.slug, place.slug, "index.html"),
                        p_html
                    )
                    sitemap_urls.append(f"destinations/{country.slug}/{state.slug}/{place.slug}")

        # -------------------------------------------------------------
        # E. Copy Static Assets (Video, Posters, Images)
        # -------------------------------------------------------------
        target_static = os.path.join(OUTPUT_DIR, "static")
        if os.path.exists(STATIC_DIR):
            shutil.copytree(STATIC_DIR, target_static)
            print(f"  [STATIC] Copied static assets to {target_static}")

        # -------------------------------------------------------------
        # F. Export Search Data JSON
        # -------------------------------------------------------------
        target_data = os.path.join(OUTPUT_DIR, "data")
        os.makedirs(target_data, exist_ok=True)
        destinations_json_path = os.path.join(target_data, "destinations.json")
        with open(destinations_json_path, "w", encoding="utf-8") as f:
            json.dump([p.to_dict() for p in places], f, indent=2, ensure_ascii=False)
        print("  [DATA] Exported data/destinations.json for client-side search index")

        # -------------------------------------------------------------
        # G. Generate .htaccess for Hostinger (Apache/LiteSpeed)
        # -------------------------------------------------------------
        htaccess_content = """# ==============================================================================
# Hostinger Apache / LiteSpeed Configuration for Jai Srimannarayana
# ==============================================================================

# Enable Rewrite Engine
RewriteEngine On
RewriteBase /

# Force HTTPS
RewriteCond %{HTTPS} off
RewriteRule ^(.*)$ https://%{HTTP_HOST}%{REQUEST_URI} [L,R=301]

# Remove Trailing Slashes if not a real directory
RewriteCond %{REQUEST_FILENAME} !-d
RewriteRule ^(.*)/$ /$1 [L,R=301]

# Serve clean URLs without .html
RewriteCond %{REQUEST_FILENAME} !-f
RewriteCond %{REQUEST_FILENAME} !-d
RewriteCond %{REQUEST_FILENAME}.html -f
RewriteRule ^(.*)$ $1.html [L]

# Gzip Compression for Fast Loading
<IfModule mod_deflate.c>
    AddOutputFilterByType DEFLATE text/html text/plain text/xml text/css
    AddOutputFilterByType DEFLATE application/javascript application/json application/xml
    AddOutputFilterByType DEFLATE image/svg+xml
</IfModule>

# Browser Caching Headers
<IfModule mod_expires.c>
    ExpiresActive On
    ExpiresByType image/jpg "access plus 1 year"
    ExpiresByType image/jpeg "access plus 1 year"
    ExpiresByType image/gif "access plus 1 year"
    ExpiresByType image/png "access plus 1 year"
    ExpiresByType image/webp "access plus 1 year"
    ExpiresByType video/mp4 "access plus 1 year"
    ExpiresByType text/css "access plus 1 month"
    ExpiresByType application/javascript "access plus 1 month"
    ExpiresByType text/html "access plus 1 hour"
</IfModule>

# Security Headers
<IfModule mod_headers.c>
    Header set X-Content-Type-Options "nosniff"
    Header set X-Frame-Options "SAMEORIGIN"
    Header set X-XSS-Protection "1; mode=block"
    Header set Referrer-Policy "strict-origin-when-cross-origin"
</IfModule>

# Custom 404 Error Page
ErrorDocument 404 /index.html
"""
        with open(os.path.join(OUTPUT_DIR, ".htaccess"), "w", encoding="utf-8") as f:
            f.write(htaccess_content)
        print("  [CONFIG] Created .htaccess with HTTPS redirect, caching, and clean URLs")

        # -------------------------------------------------------------
        # H. Generate robots.txt
        # -------------------------------------------------------------
        robots_content = f"""User-agent: *
Allow: /

Sitemap: {DEFAULT_SITE_URL}/sitemap.xml
"""
        with open(os.path.join(OUTPUT_DIR, "robots.txt"), "w", encoding="utf-8") as f:
            f.write(robots_content)
        print("  [ROBOTS] Created robots.txt")

        # -------------------------------------------------------------
        # I. Generate sitemap.xml for Google Search Console
        # -------------------------------------------------------------
        sitemap_items = []
        for path in sitemap_urls:
            clean_path = path.strip("/")
            url = f"{DEFAULT_SITE_URL}/{clean_path}/" if clean_path else f"{DEFAULT_SITE_URL}/"
            priority = "1.0" if clean_path == "" else ("0.9" if "destinations/" in clean_path and clean_path.count("/") == 2 else "0.8")
            sitemap_items.append(f"""  <url>
    <loc>{url}</loc>
    <changefreq>weekly</changefreq>
    <priority>{priority}</priority>
  </url>""")

        sitemap_xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
{chr(10).join(sitemap_items)}
</urlset>
"""
        with open(os.path.join(OUTPUT_DIR, "sitemap.xml"), "w", encoding="utf-8") as f:
            f.write(sitemap_xml)
        print(f"  [SITEMAP] Created sitemap.xml with {len(sitemap_urls)} indexed canonical URLs")

        # Netlify headers file for exact XML mime-type and cache
        netlify_headers = """/sitemap.xml
  Content-Type: application/xml; charset=utf-8
  X-Robots-Tag: all
  Cache-Control: public, max-age=0, must-revalidate

/robots.txt
  Content-Type: text/plain; charset=utf-8
  Cache-Control: public, max-age=0, must-revalidate
"""
        with open(os.path.join(OUTPUT_DIR, "_headers"), "w", encoding="utf-8") as f:
            f.write(netlify_headers)
        print("  [CONFIG] Created _headers for Netlify edge caching and XML content-type")

        # -------------------------------------------------------------
        # J. Copy Google Verification Files & Static root items
        # -------------------------------------------------------------
        for f in os.listdir(BASE_DIR):
            if f.startswith("google") and f.endswith(".html"):
                src_path = os.path.join(BASE_DIR, f)
                dst_path = os.path.join(OUTPUT_DIR, f)
                shutil.copy2(src_path, dst_path)
                print(f"  [VERIFY] Copied Google Search Console verification file: {f}")

        # -------------------------------------------------------------
        # K. Create Hostinger Deployment README inside the folder
        # -------------------------------------------------------------
        hostinger_readme = """# How to Upload to Hostinger (in 3 Minutes)

This folder contains the complete, pre-built website for **Jai Srimannarayana Tours & Travels**.
It requires **zero Python setup** or background daemons on Hostinger shared hosting.

## Method 1: Upload via Hostinger hPanel File Manager (Easiest)
1. Log in to your **Hostinger Control Panel (hPanel)**.
2. Go to **Websites** -> Select your domain -> Click **Manage**.
3. Under **Files**, click **File Manager**.
4. Double-click to open the **`public_html`** directory.
5. Delete any default `default.php` file if present.
6. Click the **Upload** icon (top right) -> Select **Archive** -> Upload `website_hostinger.zip`.
7. Right-click `website_hostinger.zip` inside `public_html` and click **Extract**.
8. Ensure all files (`index.html`, `destinations/`, `calculator/`, `static/`, `.htaccess`) are directly inside `public_html/`.
9. Visit your domain in your browser! Your website is live with 100% speed!

## Method 2: Upload via FTP (FileZilla)
1. In Hostinger hPanel, find your **FTP Accounts** credentials (Host, Username, Password, Port 21).
2. Connect FileZilla to your Hostinger server.
3. Open the remote folder `/public_html`.
4. Drag and drop all files and folders from `website_hostinger/` directly into `/public_html`.

## Key Features Included:
- **Clean URLs**: Works seamlessly at `yourdomain.com/destinations/india/uttar-pradesh/kashi-varanasi`.
- **Google SEO Ready**: Embedded Schema.org JSON-LD structured data on all destination pages.
- **Fast Speed**: HTML pre-rendered with Gzip compression and browser caching in `.htaccess`.
- **Direct WhatsApp Funnel**: Instant bookings routed to Ramesh at 9030780132.
"""
        with open(os.path.join(OUTPUT_DIR, "HOSTINGER_UPLOAD_GUIDE.md"), "w", encoding="utf-8") as f:
            f.write(hostinger_readme)

        # -------------------------------------------------------------
        # K. Create website_hostinger.zip archive
        # -------------------------------------------------------------
        print(f"\n[ZIP] Creating zip archive: {ZIP_OUTPUT}...")
        with zipfile.ZipFile(ZIP_OUTPUT, "w", zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(OUTPUT_DIR):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, OUTPUT_DIR)
                    zipf.write(file_path, arcname)

        zip_size_mb = os.path.getsize(ZIP_OUTPUT) / (1024 * 1024)
        print(f"[SUCCESS] Hostinger deployment archive created ({zip_size_mb:.2f} MB)")
        print(f"Folder path: {OUTPUT_DIR}")
        print(f"Zip path:    {ZIP_OUTPUT}")
        print("=" * 70)

    finally:
        db.close()


if __name__ == "__main__":
    build_site()
