# 🔱 Jai Srimannarayana Tours & Travels — AI Business Engine
### Scaling Hyderabad's Premier Pilgrimage Tour Operator to ₹100 Crore ARR

[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115%2B-green.svg)](https://fastapi.tiangolo.com/)
[![Gemini](https://img.shields.io/badge/LLM-Gemini%203.8%20Flash%20%2F%202.5%20Flash-orange.svg)](https://aistudio.google.com/)
[![WhatsApp Cloud API](https://img.shields.io/badge/WhatsApp-Cloud%20API%20v20.0-25D366.svg)](https://developers.facebook.com/)

---

## 📖 Executive Summary
**Jai Srimannarayana Tours & Travels** is a Hyderabad-based devotional travel brand founded by **Ramesh** ([@telugutravellerramesh5846](https://www.youtube.com/@telugutravellerramesh5846)). This AI Business Engine automates 24/7 WhatsApp lead qualification from YouTube Shorts traffic, generates daily viral video marketing scripts, designs high-margin recurring pilgrimage routes, and synthesizes daily operations into an executive briefing for management.

---

## 🏛️ System Architecture

```
                                  [ YouTube Shorts Traffic ]
                                 (@telugutravellerramesh5846)
                                              │
                                              ▼
                                 [ WhatsApp Cloud API / Meta ]
                                              │
                                      (Ngrok / Webhook)
                                              │
┌─────────────────────────────────────────────▼──────────────────────────────────────────────┐
│                                 FastAPI Webhook Gateway                                     │
│                            (GET /webhook & POST /webhook)                                  │
└─────────────────────────────────────────────┬──────────────────────────────────────────────┘
                                              │
                      ┌───────────────────────┴───────────────────────┐
                      ▼                                               ▼
     ┌──────────────────────────────────┐            ┌──────────────────────────────────┐
     │      1. Sales Qualifier Agent    │            │        2. Marketing Agent        │
     │  - Telugu / Hindi / English      │            │  - 3 Daily YouTube Shorts        │
     │  - Multi-turn Conversational     │            │  - Hooks, B-Roll, Telugu VO      │
     │  - 5-Point Parameter Extraction  │            │  - Directives for Ramesh    │
     │  - Priority Handover to 9030780132│           └────────────────┬─────────────────┘
     └────────────────┬─────────────────┘                             │
                      │                                               │
                      ▼                                               ▼
     ┌──────────────────────────────────────────────────────────────────────────────────┐
     │                      SQLite / PostgreSQL Database Layer                          │
     │    (Tables: leads, conversations, marketing_content, expansion_pitches, etc.)    │
     └────────────────┬───────────────────────────────────────────────┬─────────────────┘
                      │                                               │
                      ▼                                               ▼
     ┌──────────────────────────────────┐            ┌──────────────────────────────────┐
     │        3. Expansion Agent        │            │     4. CEO Agent (Orchestrator)  │
     │  - 4-Day Recurring Routes        │            │  - Scheduled at 8:00 AM IST      │
     │  - Hyderabad Departures          │───────────►│  - Synthesizes Leads + Marketing │
     │  - Arunachalam, Ujjain, Vellore  │            │  - Daily Executive Briefing      │
     │  - 35% - 42% Profit Margins      │            │  - ₹100 Crore Roadmap Tracker    │
     └──────────────────────────────────┘            └──────────────────────────────────┘
```

---

## 🚀 Quickstart Guide

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure Environment Variables
Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```
Open `.env` and fill in your keys:
- `GEMINI_API_KEY`: Get your free key from [Google AI Studio](https://aistudio.google.com/).
- `GEMINI_MODEL`: Defaults to `gemini-2.5-flash` (or `gemini-3.8-flash` if enabled on your tier).
- `WHATSAPP_VERIFY_TOKEN`: Choose a secure secret token (e.g. `***REMOVED***`).
- `WHATSAPP_TOKEN`: Meta System User or Temporary Access Token.
- `WHATSAPP_PHONE_NUMBER_ID`: Sender phone number ID from Meta App Dashboard.

### 3. Run the End-to-End Simulation Suite
Verify the entire system locally without needing Meta credentials:
```bash
python test_simulation.py
```
This tests:
1. Meta Webhook Verification challenge (`GET /webhook`)
2. Multi-turn WhatsApp conversation in Telugu with senior citizen wheelchair & ground-floor room requirements
3. Lead qualification and SQLite storage
4. Generation of 3 YouTube Shorts scripts
5. Generation of high-margin 4-day route proposal
6. Daily Executive Briefing synthesis for Ramesh

### 4. Start the FastAPI Production Server
```bash
python main.py
```
*Or using Uvicorn directly:*
```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```
The server will be live at `http://localhost:8000`. You can inspect the interactive Swagger API docs at `http://localhost:8000/docs`.

---

## 🌐 Connecting Meta WhatsApp Cloud API via Ngrok

### Step 1: Start Ngrok Tunnel
In a separate terminal window, expose port 8000:
```bash
ngrok http 8000
```
Ngrok will display a public HTTPS URL:
```
Forwarding https://1a2b-3c4d.ngrok-free.app -> http://localhost:8000
```

### Step 2: Configure Meta Developer Portal
1. Go to [developers.facebook.com](https://developers.facebook.com/) and open your App.
2. In the left sidebar, navigate to **WhatsApp** -> **Configuration**.
3. Under **Webhook**, click **Edit**:
   - **Callback URL**: `https://1a2b-3c4d.ngrok-free.app/webhook`
   - **Verify Token**: Enter the exact value from your `.env` file (`WHATSAPP_VERIFY_TOKEN`).
4. Click **Verify and Save**. Meta will send a `GET` request to verify the endpoint.
5. Under **Webhook Fields**, click **Manage** and subscribe to **`messages`**.

### Step 3: Test Live WhatsApp Message
Send a WhatsApp message from any phone to your WhatsApp Business Number:
> *"Jai Srimannarayana! Ramesh video chusamu, Chardham Yatra 2026 details kavali."*

The Sales Agent will immediately detect Telugu, maintain memory, extract passenger count and senior needs, qualify the lead, and prepare the lead for Ramesh to close!

---

## 📡 API Reference

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/` | **Public Web Portal Homepage**: Search bar, featured pilgrimage cards, interactive budget calculator, video showcase, and direct WhatsApp CTA. |
| `GET` | `/destinations` | **Global & Domestic Directory**: Catalog of countries (India, Nepal) and states with Hyderabad departures. |
| `GET` | `/destinations/{country_slug}` | **Country Hub**: Currency exchange rates (INR), visa guidelines, and state directories. |
| `GET` | `/destinations/{country_slug}/{state_slug}` | **State Hub**: Best travel seasons, capital cities, and list of famous sacred places. |
| `GET` | `/destinations/{country}/{state}/{place}` | **Destination Detail Page**: Rich SEO metadata, Schema.org JSON-LD (`TouristAttraction`, `BreadcrumbList`, `FAQPage`), Hyderabad flight/train logistics, budget breakdown, and elder care guidelines. |
| `GET` | `/calculator` | **Hyderabad Travel Budget Calculator**: Real-time INR budget estimator for pilgrims departing from RGIA / Secunderabad. |
| `GET` | `/api/destinations/search?q=...` | **Search API**: Full-text keyword search across destinations, states, and categories. |
| `GET` | `/api/status` *(or `/api/health`)* | System health check and real-time database stats. |
| `POST` | `/agent-team/execute` *(or `/ask`)* | **Universal Multi-Agent Engine**: Dispatches any question to Sales, Marketing, Operations, runs the **Critic Agent** attack, applies self-healing fixes, and outputs the CEO decision. |
| `GET` | `/webhook` | Meta WhatsApp Cloud API verification handshake. |
| `POST` | `/webhook` | Receives incoming WhatsApp messages, extracts lead, and replies. |
| `GET` | `/daily-briefing` | Triggers CEO Agent to generate executive summary & roadmap status. |
| `POST` | `/marketing/generate` | Generates 3 daily YouTube Shorts scripts for Ramesh. |
| `GET` | `/marketing/scripts` | View recent marketing scripts stored in the database. |
| `POST` | `/expansion/generate` | Generates a 4-day recurring route pitch departing from Hyderabad. |
| `GET` | `/expansion/pitches` | View proposed expansion packages. |
| `GET` | `/leads` | View all leads with optional filters (`?is_qualified=true`). |
| `GET` | `/leads/{phone}` | View individual lead profile and full WhatsApp chat history. |

---

## 🎯 The ₹100 Crore ARR Business Formula

| Strategic Pillar | Target Volume | Average Ticket Size | Projected Annual Revenue |
|---|---|---|---|
| **Chardham Yatra 2026** (May-Oct) | 500 Batches (10,000 Pilgrims) | ₹55,000 / pax | **₹55 Crore** |
| **Kashi - Ayodhya - Naimisharanyam** | 1,200 Batches (18,000 Pilgrims) | ₹18,000 / pax | **₹32 Crore** |
| **Recurring Weekend Routes** (Arunachalam, Ujjain) | 8,000 Pilgrims across 12 months | ₹16,000 / pax | **₹13 Crore** |
| **Total Engine Output** | | | **₹100 Crore** |

**Core Moat:** 
1. 100% Satvik South Indian / Telugu chef traveling with pilgrims.
2. Verified ground-floor hotel rooms & Kedarnath helicopter booking.
3. Telugu-speaking tour managers assisting senior citizens end-to-end.
4. AI Sales Qualifier ensuring **zero dropped leads** from YouTube viral spikes.

---

## 🗄️ PostgreSQL Migration (When Scaling)
To switch from SQLite to PostgreSQL in production:
1. Provision a PostgreSQL instance (e.g., Supabase, AWS RDS, Cloud SQL).
2. Update `.env`:
   ```env
   DATABASE_URL=postgresql://postgres:yourpassword@dbhost:5432/pilgrimage_tours
   ```
3. Run `python -c "import database; database.init_db()"` to generate all tables in PostgreSQL.

---

*“ధర్మో రక్షతి రక్షితః — భక్తుల సేవయే శ్రీమన్నారాయణ సేవ”*
