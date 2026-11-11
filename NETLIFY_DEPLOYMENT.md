# 🔱 Jai Srimannarayana Tours & Travels — Live Site & Deployment Guide

## 🌐 Live Website Details
- **Live URL:** [https://jaisrimannarayana.netlify.app](https://jaisrimannarayana.netlify.app)
- **Status:** 🟢 **Active & Live Worldwide** (Free HTTPS/SSL Included)
- **Hosting Provider:** Netlify (Starter Tier — 100 GB Bandwidth / Month, Unlimited Requests)
- **Local Source Folder:** `c:\Users\Krishna\Downloads\Business\website_hostinger`
- **Deployment Archive:** `c:\Users\Krishna\Downloads\Business\website_hostinger.zip`
- **Owner / Founder:** Ramesh
- **Official Contact:** +91 9030780132
- **WhatsApp Hotline:** [https://wa.me/919030780132](https://wa.me/919030780132)

---

## 🗺️ Key Live Pages on Netlify

| Page | Live URL | Description |
| :--- | :--- | :--- |
| **Homepage** | [`https://jaisrimannarayana.netlify.app/`](https://jaisrimannarayana.netlify.app/) | Yatra highlights, featured video short, instant calculator, YouTube cards. |
| **Destinations Directory** | [`https://jaisrimannarayana.netlify.app/destinations/`](https://jaisrimannarayana.netlify.app/destinations/) | Complete directory of India and Nepal sacred circuits. |
| **Budget Calculator** | [`https://jaisrimannarayana.netlify.app/calculator/`](https://jaisrimannarayana.netlify.app/calculator/) | Dynamic Pax multiplier & full static approximate budget reference table. |
| **Kashi & Ayodhya** | [`.../destinations/india/uttar-pradesh/kashi-varanasi/`](https://jaisrimannarayana.netlify.app/destinations/india/uttar-pradesh/kashi-varanasi/) | Darshan timings, ghat snanam, satvik Telugu food, flight/train routes. |
| **Kedarnath Jyotirlinga** | [`.../destinations/india/uttarakhand/kedarnath/`](https://jaisrimannarayana.netlify.app/destinations/india/uttarakhand/kedarnath/) | High-altitude senior care, helicopter base camp, oxygen escorts. |
| **Badrinath Temple** | [`.../destinations/india/uttarakhand/badrinath/`](https://jaisrimannarayana.netlify.app/destinations/india/uttarakhand/badrinath/) | Alaknanda holy bath, Mana village, Mana pass, and Telugu cook details. |
| **Arunachalam** | [`.../destinations/india/tamil-nadu/arunachalam-tiruvannamalai/`](https://jaisrimannarayana.netlify.app/destinations/india/tamil-nadu/arunachalam-tiruvannamalai/) | Pournami Giri Pradakshina, battery cars, AC coach departures from Hyderabad. |
| **Muktinath (Nepal)** | [`.../destinations/nepal/gandaki/muktinath-nepal/`](https://jaisrimannarayana.netlify.app/destinations/nepal/gandaki/muktinath-nepal/) | 108 sacred spouts, Muktinath helicopter tour, visa & currency guide. |
| **Tirupati Balaji** | [`.../destinations/india/andhra-pradesh/tirupati-balaji/`](https://jaisrimannarayana.netlify.app/destinations/india/andhra-pradesh/tirupati-balaji/) | Special entry darshan, Tirumala hill transit, family accommodation. |
| **Ujjain Mahakaleshwar** | [`.../destinations/india/madhya-pradesh/ujjain-mahakaleshwar/`](https://jaisrimannarayana.netlify.app/destinations/india/madhya-pradesh/ujjain-mahakaleshwar/) | Bhasma Aarti bookings, Omkareshwar Jyotirlinga, Indore connectivity. |

---

## 🔄 How I Will Manage Updates For You

Whenever you want to make any changes to the website:

1. **Ask Me to Make Any Update:**
   - *Example:* "Update the Kashi budget to ₹18,000"
   - *Example:* "Add a new video from Ramesh's YouTube channel"
   - *Example:* "Add a new route for Shirdi or Rameswaram"
   - *Example:* "Change contact number or WhatsApp message text"

2. **Automated Re-Baking:**
   I will update the codebase, verify with our test suite (`test_web_portal.py`), and run:
   ```powershell
   python build_hostinger_site.py
   ```
   This regenerates the entire static website in `website_hostinger/` with zero broken links.

3. **Deploying the Update to Netlify:**
   - **Method A (Drag & Drop - 10 Seconds):**
     Open [app.netlify.com](https://app.netlify.com), click on your **`jaisrimannarayana`** project &rarr; **Deploys** &rarr; Drag the `website_hostinger/` folder into the drop area. The live site updates instantly!
   - **Method B (Automatic via GitHub):**
     If you connect a free GitHub repository to Netlify, every time I commit and push changes, Netlify will build and deploy automatically without any manual clicking!
