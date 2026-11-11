"""
Database schema and ORM models for Jai Srimannarayana Tours & Travels.
Configured with SQLite by default for easy local testing and structured
for zero-friction migration to PostgreSQL.
"""

from datetime import datetime, timezone
import json
import os
from typing import Any, Dict, List, Optional
from dotenv import load_dotenv
from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
    create_engine,
    desc,
)
from sqlalchemy.orm import declarative_base, sessionmaker, Session, relationship

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./pilgrimage_tours.db")

# Ensure SQLite handles multiple threads cleanly
connect_args = {}
if DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

engine = create_engine(DATABASE_URL, connect_args=connect_args, echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class Lead(Base):
    """
    Stores potential pilgrims generated from YouTube Shorts, WhatsApp, and referrals.
    """
    __tablename__ = "leads"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    phone_number = Column(String(32), unique=True, index=True, nullable=False)
    traveler_name = Column(String(128), nullable=True)
    destination = Column(String(128), nullable=True)
    pax_count = Column(Integer, nullable=True)
    travel_month = Column(String(64), nullable=True)
    senior_citizen_needs = Column(Text, nullable=True)  # Wheelchair, ground floor, satvik food, etc.
    language_detected = Column(String(32), default="te")  # te, hi, en
    status = Column(String(32), default="NEW", index=True)  # NEW, QUALIFYING, QUALIFIED, CLOSER_ASSIGNED
    closer_notes = Column(Text, nullable=True)
    is_qualified = Column(Boolean, default=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "phone_number": self.phone_number,
            "traveler_name": self.traveler_name,
            "destination": self.destination,
            "pax_count": self.pax_count,
            "travel_month": self.travel_month,
            "senior_citizen_needs": self.senior_citizen_needs,
            "language_detected": self.language_detected,
            "status": self.status,
            "is_qualified": self.is_qualified,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class Conversation(Base):
    """
    Tracks complete WhatsApp chat history per phone number for conversational memory.
    """
    __tablename__ = "conversations"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    phone_number = Column(String(32), index=True, nullable=False)
    role = Column(String(16), nullable=False)  # user, assistant, system
    content = Column(Text, nullable=False)
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "phone_number": self.phone_number,
            "role": self.role,
            "content": self.content,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
        }


class MarketingContent(Base):
    """
    Stores AI-generated YouTube Shorts scripts, hooks, B-roll cues, and voiceovers.
    """
    __tablename__ = "marketing_content"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    title = Column(String(256), nullable=False)
    focus_tour = Column(String(128), nullable=False)  # e.g., "Chardham 2026", "Kashi Yatra"
    hook = Column(Text, nullable=False)  # 0-3 sec hook
    b_roll_suggestions = Column(Text, nullable=False)  # Visual directions
    voiceover_telugu = Column(Text, nullable=False)
    voiceover_english = Column(Text, nullable=False)
    seo_tags = Column(String(512), nullable=False)
    cta = Column(String(256), nullable=False)
    status = Column(String(32), default="APPROVED")  # DRAFT, APPROVED, PUBLISHED
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "title": self.title,
            "focus_tour": self.focus_tour,
            "hook": self.hook,
            "b_roll_suggestions": self.b_roll_suggestions,
            "voiceover_telugu": self.voiceover_telugu,
            "voiceover_english": self.voiceover_english,
            "seo_tags": self.seo_tags,
            "cta": self.cta,
            "status": self.status,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class ExpansionPitch(Base):
    """
    Stores newly proposed high-margin recurring pilgrimage routes from Hyderabad.
    """
    __tablename__ = "expansion_pitches"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    route_name = Column(String(256), nullable=False)
    duration_days = Column(Integer, default=4)
    target_margin_pct = Column(String(32), nullable=False)
    itinerary_json = Column(Text, nullable=False)
    estimated_pricing = Column(String(128), nullable=False)
    usp_highlights = Column(Text, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "route_name": self.route_name,
            "duration_days": self.duration_days,
            "target_margin_pct": self.target_margin_pct,
            "itinerary": json.loads(self.itinerary_json) if self.itinerary_json else [],
            "estimated_pricing": self.estimated_pricing,
            "usp_highlights": self.usp_highlights,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class DailyBriefing(Base):
    """
    Stores CEO Agent executive briefings aggregating sales, marketing, and expansion.
    """
    __tablename__ = "daily_briefings"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    briefing_date = Column(String(32), nullable=False)
    summary_text = Column(Text, nullable=False)
    leads_count = Column(Integer, default=0)
    qualified_leads_count = Column(Integer, default=0)
    scripts_count = Column(Integer, default=0)
    pitches_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "briefing_date": self.briefing_date,
            "summary_text": self.summary_text,
            "leads_count": self.leads_count,
            "qualified_leads_count": self.qualified_leads_count,
            "scripts_count": self.scripts_count,
            "pitches_count": self.pitches_count,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class Country(Base):
    """
    Stores Country directories (India, Nepal, Sri Lanka, etc.).
    """
    __tablename__ = "countries"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(128), unique=True, nullable=False)
    slug = Column(String(128), unique=True, index=True, nullable=False)
    continent = Column(String(64), default="Asia")
    currency_code = Column(String(16), default="INR")
    currency_symbol = Column(String(16), default="₹")
    inr_exchange_rate = Column(String(32), default="1.0")
    visa_requirement = Column(Text, nullable=True)
    flag_emoji = Column(String(16), default="🇮🇳")
    description = Column(Text, nullable=True)
    hero_image = Column(String(512), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    states = relationship("State", back_populates="country", cascade="all, delete-orphan")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "slug": self.slug,
            "continent": self.continent,
            "currency_code": self.currency_code,
            "currency_symbol": self.currency_symbol,
            "inr_exchange_rate": self.inr_exchange_rate,
            "visa_requirement": self.visa_requirement,
            "flag_emoji": self.flag_emoji,
            "description": self.description,
            "hero_image": self.hero_image,
            "states_count": len(self.states) if self.states else 0,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class State(Base):
    """
    Stores States/Provinces within a country (Uttarakhand, Uttar Pradesh, Tamil Nadu, etc.).
    """
    __tablename__ = "states"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    country_id = Column(Integer, ForeignKey("countries.id"), nullable=False)
    name = Column(String(128), nullable=False)
    slug = Column(String(128), index=True, nullable=False)
    capital_city = Column(String(128), nullable=True)
    best_time_to_visit = Column(String(128), nullable=True)
    description = Column(Text, nullable=True)
    hero_image = Column(String(512), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    country = relationship("Country", back_populates="states")
    places = relationship("Place", back_populates="state", cascade="all, delete-orphan")

    @property
    def country_name(self) -> str:
        return self.country.name if self.country else ""

    @property
    def country_slug(self) -> str:
        return self.country.slug if self.country else ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "country_id": self.country_id,
            "country_name": self.country.name if self.country else None,
            "country_slug": self.country.slug if self.country else None,
            "name": self.name,
            "slug": self.slug,
            "capital_city": self.capital_city,
            "best_time_to_visit": self.best_time_to_visit,
            "description": self.description,
            "hero_image": self.hero_image,
            "places_count": len(self.places) if self.places else 0,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class Place(Base):
    """
    Stores specific destinations with Hyderabad-outbound travel logistics and SEO metadata.
    """
    __tablename__ = "places"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    state_id = Column(Integer, ForeignKey("states.id"), nullable=False)
    name = Column(String(128), nullable=False)
    slug = Column(String(128), index=True, nullable=False)
    category = Column(String(64), default="Pilgrimage")  # Pilgrimage, Heritage, Hill Station, Nature
    history_and_importance = Column(Text, nullable=False)
    best_season = Column(String(128), nullable=False)
    nearest_airport = Column(String(128), nullable=True)
    nearest_railway = Column(String(128), nullable=True)
    
    # Hyderabad Outbound Logistical Moat
    hyderabad_flight_options = Column(Text, nullable=True)
    hyderabad_train_options = Column(Text, nullable=True)
    hyderabad_road_options = Column(Text, nullable=True)
    estimated_budget_min_inr = Column(Integer, default=15000)
    estimated_budget_max_inr = Column(Integer, default=35000)
    budget_breakdown_json = Column(Text, nullable=True)
    currency_code = Column(String(16), default="INR")
    currency_symbol = Column(String(16), default="₹")
    telugu_food_rating = Column(Integer, default=5)
    senior_friendly = Column(Boolean, default=True)
    wheelchair_accessible = Column(Boolean, default=True)
    senior_tips = Column(Text, nullable=True)

    # SEO Metadata
    meta_title = Column(String(256), nullable=True)
    meta_description = Column(String(512), nullable=True)
    hero_image = Column(String(512), nullable=True)
    highlights_json = Column(Text, nullable=True)
    faq_json = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    state = relationship("State", back_populates="places")

    @property
    def state_name(self) -> str:
        return self.state.name if self.state else ""

    @property
    def state_slug(self) -> str:
        return self.state.slug if self.state else ""

    @property
    def country_name(self) -> str:
        return self.state.country.name if (self.state and self.state.country) else ""

    @property
    def country_slug(self) -> str:
        return self.state.country.slug if (self.state and self.state.country) else ""

    @property
    def budget_breakdown(self) -> dict:
        return json.loads(self.budget_breakdown_json) if self.budget_breakdown_json else {}

    @property
    def highlights(self) -> list:
        return json.loads(self.highlights_json) if self.highlights_json else []

    @property
    def faqs(self) -> list:
        return json.loads(self.faq_json) if self.faq_json else []

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "state_id": self.state_id,
            "state_name": self.state.name if self.state else None,
            "state_slug": self.state.slug if self.state else None,
            "country_name": self.state.country.name if self.state and self.state.country else None,
            "country_slug": self.state.country.slug if self.state and self.state.country else None,
            "name": self.name,
            "slug": self.slug,
            "category": self.category,
            "history_and_importance": self.history_and_importance,
            "best_season": self.best_season,
            "nearest_airport": self.nearest_airport,
            "nearest_railway": self.nearest_railway,
            "hyderabad_flight_options": self.hyderabad_flight_options,
            "hyderabad_train_options": self.hyderabad_train_options,
            "hyderabad_road_options": self.hyderabad_road_options,
            "estimated_budget_min_inr": self.estimated_budget_min_inr,
            "estimated_budget_max_inr": self.estimated_budget_max_inr,
            "budget_breakdown": json.loads(self.budget_breakdown_json) if self.budget_breakdown_json else {},
            "currency_code": self.currency_code,
            "currency_symbol": self.currency_symbol,
            "telugu_food_rating": self.telugu_food_rating,
            "senior_friendly": self.senior_friendly,
            "wheelchair_accessible": self.wheelchair_accessible,
            "senior_tips": self.senior_tips,
            "meta_title": self.meta_title,
            "meta_description": self.meta_description,
            "hero_image": self.hero_image,
            "highlights": json.loads(self.highlights_json) if self.highlights_json else [],
            "faqs": json.loads(self.faq_json) if self.faq_json else [],
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


def init_db():
    """Initializes tables in database."""
    Base.metadata.create_all(bind=engine)


def get_db():
    """FastAPI dependency for yielding database sessions."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ==============================================================================
# Database Helper Utilities
# ==============================================================================

def get_or_create_lead(db: Session, phone_number: str) -> Lead:
    """Finds existing lead or initializes a new lead record."""
    lead = db.query(Lead).filter(Lead.phone_number == phone_number).first()
    if not lead:
        lead = Lead(phone_number=phone_number, status="NEW")
        db.add(lead)
        db.commit()
        db.refresh(lead)
    return lead


def update_lead(
    db: Session,
    phone_number: str,
    traveler_name: Optional[str] = None,
    destination: Optional[str] = None,
    pax_count: Optional[int] = None,
    travel_month: Optional[str] = None,
    senior_citizen_needs: Optional[str] = None,
    language_detected: Optional[str] = None,
    is_qualified: Optional[bool] = None,
    notes: Optional[str] = None,
) -> Lead:
    """Updates lead fields with newly extracted values."""
    lead = get_or_create_lead(db, phone_number)
    if traveler_name:
        lead.traveler_name = traveler_name
    if destination:
        lead.destination = destination
    if pax_count is not None:
        lead.pax_count = pax_count
    if travel_month:
        lead.travel_month = travel_month
    if senior_citizen_needs:
        lead.senior_citizen_needs = senior_citizen_needs
    if language_detected:
        lead.language_detected = language_detected
    if notes:
        lead.closer_notes = notes

    if is_qualified is not None:
        lead.is_qualified = is_qualified
        if is_qualified:
            lead.status = "QUALIFIED"
        elif lead.status == "NEW":
            lead.status = "QUALIFYING"

    lead.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(lead)
    return lead


def record_message(db: Session, phone_number: str, role: str, content: str) -> Conversation:
    """Records a single conversational turn in the chat history."""
    msg = Conversation(phone_number=phone_number, role=role, content=content)
    db.add(msg)
    db.commit()
    db.refresh(msg)
    return msg


def get_conversation_history(db: Session, phone_number: str, limit: int = 15) -> List[Dict[str, str]]:
    """Retrieves chronological conversation history for prompt context."""
    records = (
        db.query(Conversation)
        .filter(Conversation.phone_number == phone_number)
        .order_by(Conversation.id.asc())
        .limit(limit)
        .all()
    )
    return [{"role": r.role, "content": r.content} for r in records]


def save_marketing_scripts(db: Session, scripts: List[Dict[str, Any]]) -> List[MarketingContent]:
    """Bulk stores generated marketing scripts."""
    saved_records = []
    for s in scripts:
        rec = MarketingContent(
            title=s.get("title", "Untitled Short"),
            focus_tour=s.get("focus_tour", "Pilgrimage Yatra"),
            hook=s.get("hook", ""),
            b_roll_suggestions=s.get("b_roll_suggestions", ""),
            voiceover_telugu=s.get("voiceover_telugu", ""),
            voiceover_english=s.get("voiceover_english", ""),
            seo_tags=s.get("seo_tags", "#Chardham #Pilgrimage"),
            cta=s.get("cta", "Call 9030780132"),
            status="APPROVED",
        )
        db.add(rec)
        saved_records.append(rec)
    db.commit()
    return saved_records


def save_expansion_pitch(db: Session, pitch_data: Dict[str, Any]) -> ExpansionPitch:
    """Stores a generated high-margin expansion route."""
    rec = ExpansionPitch(
        route_name=pitch_data.get("route_name", "Weekend Pilgrimage Route"),
        duration_days=pitch_data.get("duration_days", 4),
        target_margin_pct=pitch_data.get("target_margin_pct", "35%"),
        itinerary_json=json.dumps(pitch_data.get("itinerary", [])),
        estimated_pricing=pitch_data.get("estimated_pricing", "₹15,000/pax"),
        usp_highlights=pitch_data.get("usp_highlights", ""),
    )
    db.add(rec)
    db.commit()
    db.refresh(rec)
    return rec


def save_daily_briefing(db: Session, briefing_data: Dict[str, Any]) -> DailyBriefing:
    """Stores the CEO executive briefing."""
    rec = DailyBriefing(
        briefing_date=briefing_data.get("briefing_date", datetime.now().strftime("%Y-%m-%d")),
        summary_text=briefing_data.get("summary_text", ""),
        leads_count=briefing_data.get("leads_count", 0),
        qualified_leads_count=briefing_data.get("qualified_leads_count", 0),
        scripts_count=briefing_data.get("scripts_count", 0),
        pitches_count=briefing_data.get("pitches_count", 0),
    )
    db.add(rec)
    db.commit()
    db.refresh(rec)
    return rec
