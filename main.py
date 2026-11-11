"""
FastAPI application for Jai Srimannarayana Tours & Travels - AI Business Engine.
Handles:
1. Meta WhatsApp Cloud API verification (GET /webhook)
2. WhatsApp incoming messages & lead qualification (POST /webhook)
3. Daily Executive Briefing orchestration (GET /daily-briefing)
4. Marketing script generation (POST /marketing/generate)
5. Route expansion generator (POST /expansion/generate)
6. Lead querying & pipeline management (GET /leads)
"""

from contextlib import asynccontextmanager
from datetime import datetime, timezone
import logging
import os
from typing import Any, Dict, List, Optional
from apscheduler.schedulers.background import BackgroundScheduler
from dotenv import load_dotenv
from fastapi import BackgroundTasks, Depends, FastAPI, HTTPException, Query, Request, Response, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, PlainTextResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import httpx
from pydantic import BaseModel
from sqlalchemy.orm import Session, joinedload

import database
from database import (
    Country,
    DailyBriefing,
    ExpansionPitch,
    Lead,
    MarketingContent,
    Place,
    SessionLocal,
    State,
    get_conversation_history,
    get_db,
    init_db,
)
from agents import CEOAgent, ExpansionAgent, MarketingAgent, SalesAgent, CriticAgent, TeamOrchestrator

load_dotenv()
logger = logging.getLogger("PilgrimageWebhook")
logging.basicConfig(level=logging.INFO)

# Environment variables
WHATSAPP_VERIFY_TOKEN = os.getenv("WHATSAPP_VERIFY_TOKEN", "***REMOVED***")
WHATSAPP_TOKEN = os.getenv("WHATSAPP_TOKEN", "")
WHATSAPP_PHONE_NUMBER_ID = os.getenv("WHATSAPP_PHONE_NUMBER_ID", "")
BUSINESS_PHONE = os.getenv("BUSINESS_PHONE", "9030780132")
BUSINESS_NAME = os.getenv("BUSINESS_NAME", "Jai Srimannarayana Tours & Travels")
ENABLE_DAILY_SCHEDULER = os.getenv("ENABLE_DAILY_SCHEDULER", "true").lower() == "true"

# Cache for deduplicating incoming WhatsApp messages
processed_message_ids = set()

# Initialize scheduler
scheduler = BackgroundScheduler()


def scheduled_daily_briefing_job():
    """Background cron job that runs every morning to generate the CEO briefing."""
    logger.info("Executing scheduled Daily Executive Briefing job...")
    db = SessionLocal()
    try:
        # 1. Generate marketing shorts
        MarketingAgent.generate_daily_shorts(db)
        # 2. Pitch new route
        ExpansionAgent.pitch_new_route(db)
        # 3. Generate CEO briefing
        briefing = CEOAgent.generate_daily_briefing(db)
        logger.info(f"Daily Executive Briefing completed for {briefing.briefing_date}")
    except Exception as e:
        logger.error(f"Error executing daily briefing job: {e}")
    finally:
        db.close()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle manager: initializes database and sets up daily cron jobs."""
    init_db()
    logger.info("Database initialized.")

    if ENABLE_DAILY_SCHEDULER:
        # Schedule daily briefing at 8:00 AM IST
        scheduler.add_job(scheduled_daily_briefing_job, "cron", hour=8, minute=0, id="daily_briefing_job")
        scheduler.start()
        logger.info("Daily CEO executive scheduler started (Scheduled for 08:00 AM daily).")

    yield

    if scheduler.running:
        scheduler.shutdown()
        logger.info("Daily CEO executive scheduler stopped.")


app = FastAPI(
    title="Jai Srimannarayana Tours & Travels - AI Business Engine",
    description="Multi-Agent AI Engine powering WhatsApp Sales, YouTube Shorts Marketing, Route Expansion & CEO Executive Briefings.",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static files & Jinja2 Templates setup
os.makedirs("static", exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


# ==============================================================================
# Helper Functions: WhatsApp Outbound Dispatcher
# ==============================================================================

async def send_whatsapp_reply(to_phone: str, reply_text: str):
    """
    Dispatches outbound WhatsApp text reply to pilgrim via Meta WhatsApp Cloud API.
    If credentials are not yet configured, gracefully logs the simulated outbound dispatch.
    """
    is_placeholder = (
        not WHATSAPP_TOKEN
        or WHATSAPP_TOKEN.startswith("your_")
        or not WHATSAPP_PHONE_NUMBER_ID
        or WHATSAPP_PHONE_NUMBER_ID.startswith("your_")
    )
    if is_placeholder:
        logger.info(
            f"[SIMULATED OUTBOUND WHATSAPP] To: {to_phone} | Message:\n{reply_text}\n"
            f"(Note: Configure WHATSAPP_TOKEN and WHATSAPP_PHONE_NUMBER_ID in .env to send real WhatsApp messages)"
        )
        return {"status": "simulated", "to": to_phone, "message": reply_text}

    url = f"https://graph.facebook.com/v20.0/{WHATSAPP_PHONE_NUMBER_ID}/messages"
    headers = {
        "Authorization": f"Bearer {WHATSAPP_TOKEN}",
        "Content-Type": "application/json",
    }
    payload = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": to_phone,
        "type": "text",
        "text": {"preview_url": False, "body": reply_text},
    }

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.post(url, headers=headers, json=payload)
            if resp.status_code in [200, 201]:
                logger.info(f"WhatsApp message successfully delivered to {to_phone}")
                return resp.json()
            else:
                logger.error(f"Failed to send WhatsApp message: {resp.status_code} - {resp.text}")
                return {"error": resp.text, "status_code": resp.status_code}
    except Exception as e:
        logger.error(f"Exception during WhatsApp dispatch to {to_phone}: {e}")
        return {"error": str(e)}


# ==============================================================================
# Webhook Routes (Meta WhatsApp Cloud API)
# ==============================================================================

@app.get("/webhook")
async def verify_webhook(
    hub_mode: Optional[str] = Query(None, alias="hub.mode"),
    hub_verify_token: Optional[str] = Query(None, alias="hub.verify_token"),
    hub_challenge: Optional[str] = Query(None, alias="hub.challenge"),
):
    """
    Meta WhatsApp Cloud API Webhook Verification Endpoint.
    Echoes back hub.challenge when hub.verify_token matches WHATSAPP_VERIFY_TOKEN.
    """
    logger.info(f"Webhook verification request received: mode={hub_mode}, token={hub_verify_token}")
    if hub_mode == "subscribe" and hub_verify_token == WHATSAPP_VERIFY_TOKEN:
        logger.info("Webhook verified successfully with Meta!")
        return PlainTextResponse(content=hub_challenge or "", status_code=status.HTTP_200_OK)

    logger.warning("Webhook verification failed: token mismatch or invalid mode.")
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Verification token mismatch or invalid hub.mode",
    )


@app.post("/webhook")
async def receive_webhook_event(
    request: Request,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    """
    Meta WhatsApp Cloud API Webhook Event Receiver.
    Parses incoming user messages, feeds multi-turn history into the Sales Agent,
    persists extracted structured leads into SQLite, and dispatches the devotional reply.
    """
    try:
        body = await request.json()
    except Exception:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid JSON payload")

    # Verify if payload is from whatsapp_business_account
    if body.get("object") != "whatsapp_business_account":
        return JSONResponse(content={"status": "ignored", "reason": "Not whatsapp_business_account"}, status_code=200)

    entries = body.get("entry", [])
    results = []

    for entry in entries:
        for change in entry.get("changes", []):
            val = change.get("value", {})
            messages = val.get("messages", [])
            contacts = val.get("contacts", [])
            user_profile_name = contacts[0].get("profile", {}).get("name") if contacts else None

            for msg in messages:
                msg_id = msg.get("id")
                # Deduplication check
                if msg_id and msg_id in processed_message_ids:
                    logger.info(f"Skipping duplicate message id: {msg_id}")
                    continue
                if msg_id:
                    processed_message_ids.add(msg_id)
                    # Keep memory footprint bounded
                    if len(processed_message_ids) > 10000:
                        processed_message_ids.clear()

                from_phone = msg.get("from")
                msg_type = msg.get("type")

                incoming_text = ""
                if msg_type == "text":
                    incoming_text = msg.get("text", {}).get("body", "").strip()
                elif msg_type == "button":
                    incoming_text = msg.get("button", {}).get("text", "").strip()
                elif msg_type == "interactive":
                    interactive = msg.get("interactive", {})
                    if interactive.get("type") == "button_reply":
                        incoming_text = interactive.get("button_reply", {}).get("title", "")
                    elif interactive.get("type") == "list_reply":
                        incoming_text = interactive.get("list_reply", {}).get("title", "")

                if not from_phone or not incoming_text:
                    continue

                logger.info(f"Incoming message from {from_phone} ({user_profile_name or 'Devotee'}): '{incoming_text}'")

                # If name is available from WhatsApp profile and not yet saved, seed it
                if user_profile_name:
                    existing = database.get_or_create_lead(db, from_phone)
                    if not existing.traveler_name:
                        existing.traveler_name = user_profile_name
                        db.commit()

                # Process message through Sales & Lead Qualifier Agent
                qualification_output = SalesAgent.process_message(
                    db=db,
                    phone_number=from_phone,
                    incoming_text=incoming_text,
                )

                # Queue outbound WhatsApp response as background task
                background_tasks.add_task(
                    send_whatsapp_reply,
                    to_phone=from_phone,
                    reply_text=qualification_output.reply_message,
                )

                results.append({
                    "phone": from_phone,
                    "lead_status": "QUALIFIED" if qualification_output.is_qualified else "QUALIFYING",
                    "traveler_name": qualification_output.traveler_name,
                    "destination": qualification_output.destination,
                    "pax_count": qualification_output.pax_count,
                    "reply": qualification_output.reply_message,
                })

    return JSONResponse(
        content={"status": "EVENT_RECEIVED", "processed_count": len(results), "details": results},
        status_code=status.HTTP_200_OK,
    )


# ==============================================================================
# Website & Travel Portal Routes (SSR Jinja2 + SEO JSON-LD)
# ==============================================================================

@app.get("/")
async def home_page(request: Request, db: Session = Depends(get_db)):
    """Render public homepage with curated destinations, budget calculator, and video."""
    places = db.query(Place).join(State).join(Country).all()
    return templates.TemplateResponse(request=request, name="index.html", context={"places": places})


@app.get("/destinations")
async def destinations_page(request: Request, db: Session = Depends(get_db)):
    """Global & domestic destinations directory organized by Country and State."""
    countries = db.query(Country).options(joinedload(Country.states).joinedload(State.places)).all()
    return templates.TemplateResponse(request=request, name="destinations.html", context={"countries": countries})


@app.get("/destinations/{country_slug}")
async def country_page(country_slug: str, request: Request, db: Session = Depends(get_db)):
    """Country hub page with currency exchange, visa rules, and member states."""
    country = db.query(Country).filter(Country.slug == country_slug).options(joinedload(Country.states).joinedload(State.places)).first()
    if not country:
        raise HTTPException(status_code=404, detail=f"Country '{country_slug}' not found")
    return templates.TemplateResponse(request=request, name="country.html", context={"country": country})


@app.get("/destinations/{country_slug}/{state_slug}")
async def state_page(country_slug: str, state_slug: str, request: Request, db: Session = Depends(get_db)):
    """State hub page with all sacred destinations and Hyderabad transit overviews."""
    state = db.query(State).join(Country).filter(Country.slug == country_slug, State.slug == state_slug).options(joinedload(State.places)).first()
    if not state:
        raise HTTPException(status_code=404, detail=f"State '{state_slug}' in country '{country_slug}' not found")
    return templates.TemplateResponse(request=request, name="state.html", context={"state": state})


@app.get("/destinations/{country_slug}/{state_slug}/{place_slug}")
async def place_detail_page(country_slug: str, state_slug: str, place_slug: str, request: Request, db: Session = Depends(get_db)):
    """SEO-optimized destination page with Schema.org JSON-LD, Hyderabad logistics, budgets, and WhatsApp CTAs."""
    place = db.query(Place).join(State).join(Country).filter(
        Country.slug == country_slug,
        State.slug == state_slug,
        Place.slug == place_slug
    ).first()
    if not place:
        raise HTTPException(status_code=404, detail=f"Destination '{place_slug}' not found")
    return templates.TemplateResponse(request=request, name="place_detail.html", context={"place": place})


@app.get("/calculator")
async def calculator_page(request: Request, db: Session = Depends(get_db)):
    """Dedicated interactive travel budget calculator for Hyderabad departures."""
    places = db.query(Place).join(State).join(Country).all()
    return templates.TemplateResponse(request=request, name="calculator.html", context={"places": places})


@app.get("/packages/kashi-prayagraj-ayodhya")
async def package_kashi_ayodhya_page(request: Request):
    """Flagship 5-Day Kashi - Prayagraj - Ayodhya tour package from Hyderabad."""
    return templates.TemplateResponse(request=request, name="package_kashi_ayodhya.html")

@app.get("/packages/diwali-dev-deepavali")
async def package_diwali_dev_deepavali_page(request: Request):
    """Diwali Deepotsav Ayodhya and Kashi Dev Deepavali festival tour package from Hyderabad."""
    return templates.TemplateResponse(request=request, name="package_diwali_dev_deepavali.html")


@app.get("/packages/rameswaram-madurai-kanyakumari")
async def package_rameswaram_page(request: Request):
    """5-Day Rameswaram, Madurai and Kanyakumari South India tour package from Hyderabad."""
    return templates.TemplateResponse(request=request, name="package_rameswaram_south_india.html")


@app.get("/about")
async def about_page(request: Request):
    """About Ramesh and Jai Srimannarayana Tours & Travels."""
    return templates.TemplateResponse(request=request, name="about.html")


@app.get("/contact")
async def contact_page(request: Request):
    """Contact details and Hyderabad pickup hubs."""
    return templates.TemplateResponse(request=request, name="contact.html")


@app.get("/googlec016c122600d7ab7.html")
async def google_verification():
    """Google Search Console HTML verification file handler."""
    return PlainTextResponse("google-site-verification: googlec016c122600d7ab7.html")


@app.get("/api/destinations/search")
async def search_destinations(q: Optional[str] = Query(None, description="Search keyword"), db: Session = Depends(get_db)):
    """Live search API returning matching destinations, states, and countries."""
    if not q or not q.strip():
        places = db.query(Place).limit(10).all()
        return {"query": "", "count": len(places), "results": [p.to_dict() for p in places]}

    keyword = f"%{q.strip().lower()}%"
    places = db.query(Place).join(State).join(Country).filter(
        (Place.name.ilike(keyword)) |
        (Place.category.ilike(keyword)) |
        (State.name.ilike(keyword)) |
        (Country.name.ilike(keyword))
    ).limit(20).all()

    return {
        "query": q.strip(),
        "count": len(places),
        "results": [p.to_dict() for p in places],
    }


# ==============================================================================
# Executive & Operational Endpoints
# ==============================================================================

@app.get("/api/health")
@app.get("/api/status")
async def api_status(db: Session = Depends(get_db)):
    """Health check & real-time system stats."""
    total_leads = db.query(Lead).count()
    qualified_leads = db.query(Lead).filter(Lead.is_qualified == True).count()
    total_scripts = db.query(MarketingContent).count()
    total_pitches = db.query(ExpansionPitch).count()
    total_destinations = db.query(Place).count()

    return {
        "status": "online",
        "company": BUSINESS_NAME,
        "contact_number": BUSINESS_PHONE,
        "youtube_channel": os.getenv("YOUTUBE_CHANNEL", "@telugutravellerramesh5846"),
        "active_models": {"gemini_model": os.getenv("GEMINI_MODEL", "gemini-2.5-flash")},
        "stats": {
            "total_leads": total_leads,
            "qualified_leads": qualified_leads,
            "marketing_scripts": total_scripts,
            "expansion_pitches": total_pitches,
            "destinations_cataloged": total_destinations,
        },
        "endpoints": {
            "website_home": "/",
            "destinations_directory": "/destinations",
            "budget_calculator": "/calculator",
            "search_api": "/api/destinations/search?q=kashi",
            "agent_team_execute": "/agent-team/execute (POST) or /ask (POST) - All agents + Critic + Fixes",
            "webhook_get": "/webhook (Verification)",
            "webhook_post": "/webhook (Meta incoming events)",
            "daily_briefing": "/daily-briefing (CEO Agent)",
            "leads": "/leads",
            "generate_marketing": "/marketing/generate",
            "generate_expansion": "/expansion/generate",
        },
    }


class UniversalQueryRequest(BaseModel):
    query: str


@app.post("/agent-team/execute")
@app.post("/ask")
async def execute_agent_team(
    payload: UniversalQueryRequest,
    db: Session = Depends(get_db),
):
    """
    Executes universal multi-agent workflow for ANY user question or request:
    1. Universal work assignment (Sales, Marketing, Operations)
    2. Adversarial Critic attack (Devil's Advocate, purely negative failure analysis)
    3. Self-healing fixes (Sales, Marketing, Operations fix every single criticism)
    4. CEO executive verdict (Battle-tested action plan and directives for Ramesh)
    """
    if not payload.query or not payload.query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty")
    result = TeamOrchestrator.process_universal_request(user_query=payload.query.strip(), db=db)
    return result.model_dump()


@app.get("/daily-briefing")
async def get_daily_briefing(db: Session = Depends(get_db)):
    """
    Triggers the CEO Agent (Orchestrator) to synthesize:
    1. Sales pipeline & qualified leads
    2. Marketing scripts generated
    3. Route expansion proposals
    Returns both structured JSON metrics and formatted devotional markdown.
    """
    briefing = CEOAgent.generate_daily_briefing(db)
    return {
        "briefing_id": briefing.id,
        "briefing_date": briefing.briefing_date,
        "leads_count": briefing.leads_count,
        "qualified_leads_count": briefing.qualified_leads_count,
        "scripts_count": briefing.scripts_count,
        "pitches_count": briefing.pitches_count,
        "formatted_text": briefing.summary_text,
    }


@app.post("/marketing/generate")
async def trigger_marketing_generation(db: Session = Depends(get_db)):
    """
    Triggers the Marketing Agent to generate 3 daily YouTube Shorts scripts.
    """
    scripts = MarketingAgent.generate_daily_shorts(db)
    return {
        "status": "success",
        "generated_count": len(scripts),
        "scripts": [s.to_dict() for s in scripts],
    }


@app.get("/marketing/scripts")
async def list_marketing_scripts(limit: int = 10, db: Session = Depends(get_db)):
    """Lists recent YouTube Shorts scripts."""
    scripts = db.query(MarketingContent).order_by(MarketingContent.id.desc()).limit(limit).all()
    return {"count": len(scripts), "scripts": [s.to_dict() for s in scripts]}


@app.post("/expansion/generate")
async def trigger_expansion_pitch(
    route: Optional[str] = Query(None, description="Optional custom route name"),
    db: Session = Depends(get_db),
):
    """
    Triggers the Expansion Agent to pitch a high-margin 4-day route departing from Hyderabad.
    """
    pitch = ExpansionAgent.pitch_new_route(db, target_route=route)
    return {
        "status": "success",
        "pitch": pitch.to_dict(),
    }


@app.get("/expansion/pitches")
async def list_expansion_pitches(limit: int = 5, db: Session = Depends(get_db)):
    """Lists recent expansion route pitches."""
    pitches = db.query(ExpansionPitch).order_by(ExpansionPitch.id.desc()).limit(limit).all()
    return {"count": len(pitches), "pitches": [p.to_dict() for p in pitches]}


@app.get("/leads")
async def list_leads(
    status: Optional[str] = None,
    is_qualified: Optional[bool] = None,
    limit: int = 50,
    db: Session = Depends(get_db),
):
    """Lists registered leads with optional filtering."""
    query = db.query(Lead)
    if status:
        query = query.filter(Lead.status == status.upper())
    if is_qualified is not None:
        query = query.filter(Lead.is_qualified == is_qualified)
    leads = query.order_by(Lead.updated_at.desc()).limit(limit).all()
    return {"count": len(leads), "leads": [l.to_dict() for l in leads]}


@app.get("/leads/{phone_number}")
async def get_lead_details(phone_number: str, db: Session = Depends(get_db)):
    """Retrieves lead profile and complete WhatsApp conversation history."""
    lead = db.query(Lead).filter(Lead.phone_number == phone_number).first()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")

    history = get_conversation_history(db, phone_number, limit=30)
    return {
        "lead": lead.to_dict(),
        "conversation_history": history,
    }


# Standalone runner
if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", "8000"))
    host = os.getenv("HOST", "0.0.0.0")
    uvicorn.run("main:app", host=host, port=port, reload=True)
