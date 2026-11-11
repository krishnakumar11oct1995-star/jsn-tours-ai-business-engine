"""
AI Agents for Jai Srimannarayana Tours & Travels.
Powered by Google Gemini 3.8 Flash via the google-genai SDK.

Contains:
1. Sales & Lead Qualifier Agent (Multilingual WhatsApp lead extraction & qualification)
2. Marketing Agent (Daily YouTube Shorts scripts generator for @telugutravellerramesh5846)
3. Expansion Agent (High-margin recurring routes from Hyderabad)
4. CEO Agent / Orchestrator (Daily Executive Briefing synthesizing business operations)
"""

from datetime import datetime
import json
import logging
import os
from typing import Any, Dict, List, Optional
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from database import (
    Lead,
    MarketingContent,
    ExpansionPitch,
    DailyBriefing,
    update_lead,
    record_message,
    get_conversation_history,
    save_marketing_scripts,
    save_expansion_pitch,
    save_daily_briefing,
)

load_dotenv()
logger = logging.getLogger("PilgrimageAI")
logging.basicConfig(level=logging.INFO)

# ==============================================================================
# Brand Context & Configuration
# ==============================================================================

BRAND_CONTEXT = """
BRAND IDENTITY:
Company Name: Jai Srimannarayana Tours & Travels
Founder / Specialist: Ramesh (YouTube Channel: @telugutravellerramesh5846)
Official Contact / Booking WhatsApp: 9030780132
Headquarters: Hyderabad, Telangana (Pilgrims depart from Hyderabad Rajiv Gandhi International Airport / Secunderabad / Kacheguda)

CORE PRODUCTS:
1. Chardham Yatra 2026 (Yamunotri, Gangotri, Kedarnath, Badrinath):
   - Premium senior-citizen friendly package
   - Dedicated South Indian / Telugu satvik cook traveling with the group (Garam garam Telugu bhojanam)
   - Guaranteed ground floor rooms or lift access
   - Helicopter booking assistance for Kedarnath & doli/pony arrangements
   - Direct flights/trains from Hyderabad with Telugu tour escort from start to finish
2. Divya Kashi - Ayodhya - Prayagraj Sangam - Naimisharanyam Yatra:
   - VIP Kashi Vishwanath Sparsha Darshan & Ganga Aarti boat ride
   - Ayodhya Ram Janmabhoomi Mandir Darshan
   - Triveni Sangam Snanam with Telugu purohits for Pinda Pradanam
   - Sacred Naimisharanyam forest darshan
3. Dedicated Senior Citizen Care:
   - Wheelchair assistance at stations/airports
   - Regular health checks, oxygen cylinders in high altitudes

COMMUNICATION TONE:
- Devotional, warm, respectful, culturally authentic (Always start with 'Jai Srimannarayana!').
- Respectful honorifics in Telugu ('Mee sevalo Ramesh', 'Mee kalyanam korukuntu' - address travelers respectfully, refer to founder strictly as 'Ramesh').
- Language matching: If pilgrim writes in Telugu (or Telugu in English script), reply in warm Telugu. If Hindi, reply in Hindi. If English, reply in English.
"""

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
# Default to gemini-2.5-flash or gemini-1.5-flash (or user's gemini-3.8-flash)
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

# Initialize Gemini Client if API key is present
genai_client = None
if GEMINI_API_KEY and GEMINI_API_KEY != "your_gemini_api_key_here":
    try:
        from google import genai
        genai_client = genai.Client(api_key=GEMINI_API_KEY)
        logger.info(f"Gemini Client initialized with model: {GEMINI_MODEL}")
    except Exception as e:
        logger.warning(f"Failed to initialize google-genai Client: {e}. Fallback mode active.")
else:
    logger.info("GEMINI_API_KEY not set or is placeholder. Smart offline fallback mode active.")


# ==============================================================================
# Pydantic Schemas for Structured Agent Output
# ==============================================================================

class LeadQualificationOutput(BaseModel):
    language_detected: str = Field(description="Language detected: 'te' (Telugu), 'hi' (Hindi), or 'en' (English)")
    traveler_name: Optional[str] = Field(default=None, description="Name of the prospective traveler")
    destination: Optional[str] = Field(default=None, description="Intended pilgrimage (e.g. Chardham Yatra 2026, Kashi, Ayodhya, etc.)")
    pax_count: Optional[int] = Field(default=None, description="Number of passengers traveling")
    travel_month: Optional[str] = Field(default=None, description="Preferred month or dates of travel (e.g. May 2026, June 2026)")
    senior_citizen_needs: Optional[str] = Field(default=None, description="Details of senior citizens traveling, wheelchair need, ground floor room request, or 'None'")
    is_qualified: bool = Field(description="True ONLY if Name, Destination, Pax, Month, and Senior Needs are all clearly established")
    missing_fields: List[str] = Field(default_factory=list, description="Fields still missing to complete qualification")
    reply_message: str = Field(description="Devotional response message to send back to the user on WhatsApp")
    closer_summary: Optional[str] = Field(default=None, description="Internal summary for human closer Ramesh")


class YouTubeShortScript(BaseModel):
    title: str = Field(description="Catchy title for the YouTube Short")
    focus_tour: str = Field(description="Destination featured (e.g., Chardham 2026, Kashi-Ayodhya)")
    hook: str = Field(description="First 3 seconds attention grabber / scroll stopper")
    b_roll_suggestions: str = Field(description="Specific camera shots, visual cues, pilgrim reactions, temple visuals")
    voiceover_telugu: str = Field(description="Complete spoken voiceover script in natural, engaging Telugu")
    voiceover_english: str = Field(description="English / Hinglish equivalent script")
    seo_tags: str = Field(description="Viral hashtags, e.g. #CHARDHAM2026 #HyderabadToKashi #TeluguTravellerRamesh")
    cta: str = Field(description="Call to action directing to WhatsApp/Call 9030780132")


class MarketingOutput(BaseModel):
    scripts: List[YouTubeShortScript] = Field(description="Exactly 3 high-converting daily YouTube Shorts scripts")


class ExpansionRouteOutput(BaseModel):
    route_name: str = Field(description="Name of the high-margin route (e.g. Arunachalam Pournami Giri Pradakshina)")
    duration_days: int = Field(default=4, description="Duration in days (standard 4 days)")
    target_margin_pct: str = Field(description="Expected profit margin percentage (e.g. 38%)")
    estimated_pricing: str = Field(description="Estimated price per pilgrim from Hyderabad (e.g. ₹16,500/pax)")
    transport_mode: str = Field(description="Transport arrangement from Hyderabad (e.g. AC Volvo / Direct Flight)")
    itinerary: List[Dict[str, str]] = Field(description="Day 1 to Day 4 detailed day-wise itinerary")
    usp_highlights: str = Field(description="Unique selling proposition and senior citizen comfort factors")
    target_audience_appeal: str = Field(description="Why Hyderabad families and devotees will book immediately")


class DailyExecutiveBriefingOutput(BaseModel):
    briefing_date: str = Field(description="Date of briefing in YYYY-MM-DD")
    executive_summary: str = Field(description="High-level overview of business traction and daily performance")
    sales_kpis: Dict[str, Any] = Field(description="Key metrics: new leads, qualified leads, top destinations")
    marketing_summary: str = Field(description="Overview of 3 scripts generated for YouTube Shorts")
    expansion_pitch_summary: str = Field(description="Overview of newly proposed route")
    path_to_100_crore: str = Field(description="Strategic insight on pipeline towards the ₹100 Crore milestone")
    directives_for_ramesh: List[str] = Field(description="Specific priority calls and tasks for Ramesh today")
    formatted_briefing_text: str = Field(description="Full devotional and executive markdown text block")


class DomainWorkOutput(BaseModel):
    agent_name: str = Field(description="Name of the agent contributing work")
    domain_focus: str = Field(description="Domain area of responsibility")
    core_strategy: str = Field(description="Strategic analysis and plan for the user request")
    action_items: List[str] = Field(description="Actionable tasks to be executed")
    key_metrics_or_data: Dict[str, Any] = Field(default_factory=dict, description="Domain-specific metrics or data points")


class CriticRiskItem(BaseModel):
    category: str = Field(description="Risk category: Operational, Health/Safety, Financial, Customer Trust, Legal/Brand")
    what_goes_wrong: str = Field(description="Precise failure mode or disaster that could occur")
    severity: str = Field(description="Risk severity: CRITICAL, HIGH, or MEDIUM")
    worst_case_consequence: str = Field(description="Worst-case real-world damage to pilgrims or business")


class CriticOutput(BaseModel):
    risk_assessment_summary: str = Field(description="Relentless, brutally honest assessment of why this could fail")
    flaws_and_vulnerabilities: List[CriticRiskItem] = Field(description="Specific negative failure modes and trap doors")
    brutal_verdict: str = Field(description="Unfiltered red-team warning to leadership")


class DomainMitigationOutput(BaseModel):
    agent_name: str = Field(description="Name of the agent proposing fixes")
    addressed_criticisms: List[str] = Field(description="Specific criticisms targeted and neutralized")
    concrete_fixes_applied: List[str] = Field(description="Concrete operational protocols, buffers, and safeguards")
    residual_risk_level: str = Field(default="CONTROLLED", description="Residual risk level: LOW or CONTROLLED")


class UniversalOrchestrationResult(BaseModel):
    user_query: str = Field(description="User prompt or business question")
    phase_1_proposals: Dict[str, Any] = Field(description="Proposals from Sales, Marketing, and Operations")
    phase_2_critic_attack: Dict[str, Any] = Field(description="Ruthless risk teardown from Critic Agent")
    phase_3_mitigation_fixes: Dict[str, Any] = Field(description="Concrete fixes engineered by Sales, Marketing, and Operations")
    phase_4_ceo_verdict: Dict[str, Any] = Field(description="Battle-tested executive decision and directives for Ramesh")
    formatted_report: str = Field(description="Executive Markdown text block for immediate reading")


# ==============================================================================
# Agent 1: Sales & Lead Qualifier Agent
# ==============================================================================

class SalesAgent:
    """
    Sales & Lead Qualifier Agent:
    - Analyzes incoming WhatsApp conversation
    - Detects language (Telugu / Hindi / English)
    - Remembers multi-turn context
    - Progressively qualifies leads across 5 parameters:
      1. Traveler Name
      2. Destination (Chardham 2026, Kashi, Ayodhya, etc.)
      3. Pax Count
      4. Travel Month
      5. Senior Citizen Needs (Wheelchair, ground floor, etc.)
    - When qualified, alerts human closer Ramesh (9030780132) and updates SQLite.
    """

    SYSTEM_PROMPT = f"""
{BRAND_CONTEXT}

ROLE: Senior Pilgrimage Consultation & Lead Qualifier Agent
Your mission:
1. Warmly greet every pilgrim with "Jai Srimannarayana! 🙏"
2. Detect language:
   - If user writes Telugu (either Telugu script or Telugu words in English letters like "Kashi yatra details cheppandi"), reply in respectful, beautiful Telugu.
   - If Hindi, reply in respectful Hindi.
   - If English, reply in respectful English.
3. Your goal is to gather these 5 essential pieces of information for booking priority:
   - 1. Traveler Name (Mee shubhanamam)
   - 2. Destination (Chardham Yatra 2026, Kashi, Ayodhya, Naimisharanyam, etc.)
   - 3. Number of Travelers (Pax count - Entha mandi prayanam chestunnaru?)
   - 4. Preferred Travel Month (Ye nela lo plan chestunnaru?)
   - 5. Senior Citizen needs (Intlo pedda vaallu unnara? Wheelchair or ground floor room kavala?)
4. BE POLITE & NATURAL: Do NOT interrogate the customer with 5 questions at once! 
   - Acknowledge what they said with genuine devotional care.
   - Ask for 1 or 2 missing details at a time gently.
   - Mention our unique comforts: Hyderabad nundi Telugu tour manager, mana Telugu vantavallatho satvik bhojanam, complete senior care.
5. QUALIFICATION COMPLETION:
   - When all 5 pieces of information are gathered, set is_qualified = True.
   - Thank them sincerely with "Jai Srimannarayana!"
   - Assure them: "Mee details Rameshki andinchamu. Mana yatra specialist 9030780132 nundi direct ga meeku call chesi seat booking & complete itinerary vivaralu teluputaru."
"""

    @classmethod
    def process_message(
        cls,
        db: Session,
        phone_number: str,
        incoming_text: str,
    ) -> LeadQualificationOutput:
        """
        Processes an incoming WhatsApp message with full conversation memory.
        """
        # 1. Fetch existing lead record
        lead = db.query(Lead).filter(Lead.phone_number == phone_number).first()
        existing_info = lead.to_dict() if lead else {}

        # 2. Fetch conversation history
        history = get_conversation_history(db, phone_number, limit=12)

        # 3. Record incoming user message
        record_message(db, phone_number=phone_number, role="user", content=incoming_text)

        # 4. Formulate prompt with full context
        prompt = f"""
Existing known details for this phone number ({phone_number}):
- Traveler Name: {existing_info.get('traveler_name') or 'Unknown'}
- Destination: {existing_info.get('destination') or 'Unknown'}
- Pax Count: {existing_info.get('pax_count') or 'Unknown'}
- Travel Month: {existing_info.get('travel_month') or 'Unknown'}
- Senior Citizen Needs: {existing_info.get('senior_citizen_needs') or 'Unknown'}
- Current Status: {existing_info.get('status') or 'NEW'}

Recent Conversation History:
{json.dumps(history, indent=2)}

New Incoming Message:
"{incoming_text}"

Extract the updated parameters and determine the appropriate devotional WhatsApp reply.
If all 5 key fields (Name, Destination, Pax, Month, Senior Citizen Needs) are established (or explicitly marked as none/not needed for seniors), set is_qualified=true.
"""

        result: LeadQualificationOutput = cls._call_llm(prompt, incoming_text, existing_info)

        # 5. Persist extracted info to database
        update_lead(
            db=db,
            phone_number=phone_number,
            traveler_name=result.traveler_name,
            destination=result.destination,
            pax_count=result.pax_count,
            travel_month=result.travel_month,
            senior_citizen_needs=result.senior_citizen_needs,
            language_detected=result.language_detected,
            is_qualified=result.is_qualified,
            notes=result.closer_summary,
        )

        # 6. Record outbound assistant reply
        record_message(db, phone_number=phone_number, role="assistant", content=result.reply_message)

        return result

    @classmethod
    def _call_llm(cls, prompt: str, incoming_text: str, existing_info: Dict[str, Any]) -> LeadQualificationOutput:
        """Invokes Gemini model with structured output, or provides intelligent fallback."""
        if genai_client:
            try:
                from google.genai import types
                response = genai_client.models.generate_content(
                    model=GEMINI_MODEL,
                    contents=f"{cls.SYSTEM_PROMPT}\n\n{prompt}",
                    config=types.GenerateContentConfig(
                        response_mime_type="application/json",
                        response_schema=LeadQualificationOutput,
                        temperature=0.3,
                    ),
                )
                if response.text:
                    data = json.loads(response.text)
                    return LeadQualificationOutput(**data)
            except Exception as e:
                logger.error(f"Gemini API error in SalesAgent: {e}. Using deterministic fallback parser.")

        # Deterministic / Smart Fallback Parser (guarantees 0 crash when API key is missing or quota limited)
        return cls._fallback_parse(incoming_text, existing_info)

    @classmethod
    def _fallback_parse(cls, incoming_text: str, existing_info: Dict[str, Any]) -> LeadQualificationOutput:
        text_lower = incoming_text.lower()

        # Language detection
        is_telugu = any(k in text_lower for k in ["kavali", "yatra", "namaste", "srimannarayana", "cheppandi", "entha", "unna", "andi", "manam", "mandi", "ela", "ayodhya", "kashi", "chardham"]) or any(ord(c) >= 0x0C00 and ord(c) <= 0x0C7F for c in incoming_text)
        is_hindi = any(k in text_lower for k in ["namaste", "yatra", "chahiye", "kripya", "bataye", "kitna", "log", "mahina"])

        lang = "te" if is_telugu else ("hi" if is_hindi else "en")

        # Destination detection
        destination = existing_info.get("destination")
        if "chardham" in text_lower or "char dham" in text_lower or "kedarnath" in text_lower:
            destination = "Chardham Yatra 2026"
        elif "kashi" in text_lower or "varanasi" in text_lower or "banaras" in text_lower:
            destination = "Divya Kashi Yatra"
        elif "ayodhya" in text_lower:
            destination = "Ayodhya & Kashi Yatra"
        elif "naimisharanyam" in text_lower:
            destination = "Kashi-Ayodhya-Naimisharanyam Yatra"
        elif "arunachalam" in text_lower:
            destination = "Arunachalam Pournami Special"

        # Traveler name
        name = existing_info.get("traveler_name")
        for marker in ["nenu", "peru", "name is", "naam"]:
            if marker in text_lower:
                parts = text_lower.split(marker)
                if len(parts) > 1:
                    raw_candidate = parts[1].strip().split(",")[0].split(".")[0].strip()
                    words = raw_candidate.split()
                    if words:
                        # Take up to 2 words if they look like names
                        cand_name = " ".join([w.capitalize() for w in words[:2] if len(w) > 1 and w.isalpha()])
                        if cand_name and len(cand_name) > 2:
                            name = cand_name

        # Pax count (preserve existing pax if already established)
        pax = existing_info.get("pax_count")
        if not pax:
            # Check for words like 'iddaram', 'mugguram', etc.
            if "iddaram" in text_lower or "two" in text_lower or "couple" in text_lower:
                pax = 2
            elif "mugguram" in text_lower or "three" in text_lower:
                pax = 3
            elif "naluguram" in text_lower or "four" in text_lower:
                pax = 4
            else:
                words = text_lower.replace(",", " ").replace(".", " ").split()
                for i, word in enumerate(words):
                    if word.isdigit():
                        val = int(word)
                        # Check context: followed by members, mandi, persons, pax, or preceded by motham
                        is_pax_context = False
                        if i + 1 < len(words) and words[i + 1] in ["members", "mandi", "persons", "pax", "devotees", "people", "adults"]:
                            is_pax_context = True
                        elif i > 0 and words[i - 1] in ["motham", "total", "around", "nearly"]:
                            is_pax_context = True
                        elif 1 <= val <= 25 and "year" not in text_lower and "age" not in text_lower:
                            is_pax_context = True

                        if is_pax_context and 1 <= val <= 100:
                            pax = val
                            break

        # Month
        month = existing_info.get("travel_month")
        months = ["january", "february", "march", "april", "may", "june", "july", "august", "september", "october", "november", "december"]
        for m in months:
            if m in text_lower or m[:3] in text_lower:
                month = m.capitalize() + " 2026"
                break

        # Senior needs
        senior_needs = existing_info.get("senior_citizen_needs")
        if "wheelchair" in text_lower or "wheel chair" in text_lower:
            senior_needs = "Wheelchair required & ground floor rooms"
        elif "pedda vallu" in text_lower or "senior" in text_lower or "old" in text_lower or "parents" in text_lower:
            senior_needs = "Senior citizens traveling - needs ground floor & satvik food"
        elif "no senior" in text_lower or "young" in text_lower or "pedda vallu leru" in text_lower:
            senior_needs = "None"

        # Check completeness
        missing = []
        if not name:
            missing.append("Traveler Name")
        if not destination:
            missing.append("Destination")
        if not pax:
            missing.append("Passenger Count")
        if not month:
            missing.append("Travel Month")
        if not senior_needs:
            missing.append("Senior Citizen Needs")

        is_qualified = len(missing) == 0

        # Craft devotional response
        if is_qualified:
            if lang == "te":
                reply = (
                    f"Jai Srimannarayana {name} garu! 🙏\n\n"
                    f"Mee {destination} yatra vivaralu ({pax} mandi, {month}) register chesamu.\n"
                    f"Senior citizen soukaryalu: {senior_needs}.\n\n"
                    f"Hyderabad nundi mana Telugu tour manager and Telugu vantavallu tho meeku pratyeka seva untundi. "
                    f"Mana senior pilgrimage expert Ramesh (9030780132) meeku 15 nimishallone direct call chesi "
                    f"seat blocking mariyu day-to-day itinerary vivaralu andistaru. Jai Srimannarayana!"
                )
            elif lang == "hi":
                reply = (
                    f"Jai Srimannarayana {name} ji! 🙏\n\n"
                    f"Aapki {destination} yatra ({pax} log, {month}) ka vivaran darj kar liya gaya hai.\n"
                    f"Hamare senior travel expert Ramesh ji (9030780132) jald hi aapse sampark karke seat booking aur "
                    f"vishesh suvidhaon ki jaankari denge. Jai Srimannarayana!"
                )
            else:
                reply = (
                    f"Jai Srimannarayana {name} ji! 🙏\n\n"
                    f"Your pilgrimage details for {destination} ({pax} passengers, {month}) have been successfully registered.\n"
                    f"Senior citizen requirements noted: {senior_needs}.\n\n"
                    f"Our tour founder Ramesh (9030780132) will call you shortly to assist with priority seat blocking "
                    f"and share the full itinerary. Wishing you a blessed journey!"
                )
        else:
            if lang == "te":
                if not destination:
                    reply = "Jai Srimannarayana! 🙏 Jai Srimannarayana Tours & Travels ki swagatam. Meeru ye punya kshetraniki (Chardham Yatra 2026, Kashi, Ayodhya, Naimisharanyam) prayanam cheyalani anukuntunnaru?"
                elif not pax:
                    reply = f"Jai Srimannarayana! 🙏 {destination} yatra lo mee tho paatu motham entha mandi devotees prayanam chestunnaru andi?"
                elif not month:
                    reply = "Jai Srimannarayana! 🙏 Chala manchidi andi. Meeru ye nela lo (e.g., May 2026, June 2026) prayanam cheyadaniki anukuntunnaru?"
                elif not senior_needs:
                    reply = "Jai Srimannarayana! 🙏 Mee group lo 60 daatina pedda vallu unnara andi? Vaariki wheelchair gani, ground floor rooms soukaryam kavala?"
                else:
                    reply = "Jai Srimannarayana! 🙏 Daya chesi mee shubhanamam (peru) telupandi. Mana Ramesh meeku sampurna vivaralu andistaru."
            elif lang == "hi":
                reply = "Jai Srimannarayana! 🙏 Jai Srimannarayana Tours me aapka swagat hai. Kripya apna shubh naam aur yatra ka sthan (Chardham 2026, Kashi, Ayodhya) batayein."
            else:
                reply = "Jai Srimannarayana! 🙏 Welcome to Jai Srimannarayana Tours & Travels. Could you please share your name and preferred pilgrimage destination (Chardham 2026, Kashi, Ayodhya)?"

        return LeadQualificationOutput(
            language_detected=lang,
            traveler_name=name,
            destination=destination,
            pax_count=pax,
            travel_month=month,
            senior_citizen_needs=senior_needs,
            is_qualified=is_qualified,
            missing_fields=missing,
            reply_message=reply,
            closer_summary=f"Pilgrim {name or 'Prospect'} interested in {destination or 'Pilgrimage'} for {pax or 'TBD'} pax in {month or 'TBD'}. Needs: {senior_needs or 'TBD'}",
        )

    @classmethod
    def analyze_request(cls, user_query: str) -> DomainWorkOutput:
        """Universal Sales Agent analysis for any business question or request."""
        prompt = f"""
ROLE: Sales Director for Jai Srimannarayana Tours & Travels (Hyderabad)
USER INQUIRY / REQUEST: "{user_query}"

Analyze this from a Sales, Pilgrim Conversion, and Trust perspective:
- How will Telugu-speaking families and elderly pilgrims react to this?
- What are the customer objections, price points, and booking triggers?
- How should WhatsApp qualification funnel handle this inquiry?
- What specific closer action should Ramesh (9030780132) take?
"""
        if genai_client:
            try:
                from google.genai import types
                resp = genai_client.models.generate_content(
                    model=GEMINI_MODEL,
                    contents=f"{cls.SYSTEM_PROMPT}\n\n{prompt}",
                    config=types.GenerateContentConfig(
                        response_mime_type="application/json",
                        response_schema=DomainWorkOutput,
                        temperature=0.3,
                    ),
                )
                if resp.text:
                    return DomainWorkOutput(**json.loads(resp.text))
            except Exception as e:
                logger.warning(f"Gemini API error in SalesAgent.analyze_request: {e}")

        # Deterministic domain fallback
        return DomainWorkOutput(
            agent_name="Sales & Pilgrim Qualifier Agent",
            domain_focus="Customer Psychology, Telugu Pilgrim Conversions & WhatsApp Trust Funnel",
            core_strategy=f"Structure the offering with deep devotional respect ('Jai Srimannarayana') addressing family decision-makers in Hyderabad, emphasizing senior-citizen safety and direct closer access to Ramesh (9030780132).",
            action_items=[
                "Deploy proactive WhatsApp qualification script highlighting Telugu tour manager & satvik bhojanam.",
                "Establish multi-tiered seat advance policy (₹5,000 initial token, balance 15 days before departure).",
                "Assign Ramesh for high-ticket priority closer calls to establish 1-on-1 personal trust.",
                "Create a dedicated WhatsApp FAQ addressing health, high altitude, and senior citizen assistance.",
            ],
            key_metrics_or_data={
                "target_conversion_rate": "24% of qualified inquiries",
                "average_pax_per_booking": 3.8,
                "primary_sales_channel": "WhatsApp & Inbound Calls (9030780132)",
            },
        )

    @classmethod
    def fix_criticism(cls, user_query: str, critic_output: CriticOutput) -> DomainMitigationOutput:
        """Engineers concrete sales and customer-trust fixes to counter Critic Agent's risks."""
        critic_summary = "\n".join([f"- [{r.category}] {r.what_goes_wrong} (Consequence: {r.worst_case_consequence})" for r in critic_output.flaws_and_vulnerabilities])
        prompt = f"""
ROLE: Sales Director for Jai Srimannarayana Tours & Travels
ORIGINAL USER REQUEST: "{user_query}"
CRITIC RISKS IDENTIFIED:
{critic_summary}

Your job is to FIX every customer trust, refund dispute, expectation mismatch, and sales trap identified by the Critic:
- Provide ironclad customer communication policies
- Fair cancellation/refund transparent framework
- Pre-departure health declaration & expectation alignment
- Personal touchpoints by Ramesh to prevent customer backlash
"""
        if genai_client:
            try:
                from google.genai import types
                resp = genai_client.models.generate_content(
                    model=GEMINI_MODEL,
                    contents=f"{cls.SYSTEM_PROMPT}\n\n{prompt}",
                    config=types.GenerateContentConfig(
                        response_mime_type="application/json",
                        response_schema=DomainMitigationOutput,
                        temperature=0.3,
                    ),
                )
                if resp.text:
                    return DomainMitigationOutput(**json.loads(resp.text))
            except Exception as e:
                logger.warning(f"Gemini API error in SalesAgent.fix_criticism: {e}")

        return DomainMitigationOutput(
            agent_name="Sales & Pilgrim Qualifier Agent",
            addressed_criticisms=[
                "Refund disputes and sudden cancellation panics from high-altitude sickness",
                "Customer outrage regarding unexpected weather delays or helicopter cancellations",
                "Communication breakdowns between tour managers and pilgrims' families in Hyderabad",
            ],
            concrete_fixes_applied=[
                "Instituted Transparent Weather & High-Altitude Force Majeure Policy signed on WhatsApp before booking.",
                "Created 'Safe Reschedule Guarantee' — funds remain 100% credited toward future Kashi or Arunachalam batches if cancelled due to verified medical reasons.",
                "Mandatory pre-trip orientation video call with Ramesh explaining realistic high-altitude conditions to parents and children.",
                "Real-time WhatsApp Family Broadcast Group providing twice-daily health and darshan updates to families back in Hyderabad.",
            ],
            residual_risk_level="CONTROLLED",
        )


# ==============================================================================
# Agent 2: Marketing Agent
# ==============================================================================

class MarketingAgent:
    """
    Marketing Agent:
    - Generates 3 daily YouTube Shorts scripts for @telugutravellerramesh5846.
    - Focuses on devotional triggers, high hook retention, senior citizen comfort,
      Hyderabad departure logistics, and Telugu catering.
    - Saves scripts into marketing_content table.
    """

    SYSTEM_PROMPT = f"""
{BRAND_CONTEXT}

ROLE: YouTube Shorts Growth & Devotional Content Director
Channel: @telugutravellerramesh5846

OBJECTIVE:
Generate exactly 3 high-converting, viral YouTube Shorts scripts (under 60 seconds each) tailored for Telugu families in Hyderabad planning pilgrimage yatras.

CONTENT PILLARS FOR THE 3 SHORTS:
1. Short 1: Chardham Yatra 2026 Registration Alert & Senior Citizen Safety (Direct flights from HYD, Kedarnath Helicopter/Doli, Satvik Telugu food cook traveling with group).
2. Short 2: Kashi - Ayodhya Ram Mandir - Naimisharanyam Spiritual Route (VIP Kashi Sparsha Darshan, Ganga Aarti, Ayodhya Ram Lalla darshan with zero waiting hassle).
3. Short 3: Pilgrims' Emotional Story / Senior Parents Dream (How a son from Hyderabad fulfilled his 72-year-old mother's Chardham dream with Jai Srimannarayana Tours).

SCRIPT STRUCTURE REQUIREMENTS:
- Hook (0-3 sec): Highly emotional, arresting opening line.
- B-Roll Visuals: Specific visual camera directions.
- Telugu Voiceover: Vernacular, authentic Telugu spoken by Ramesh.
- English Voiceover: Clear English translation.
- SEO Tags: #CHARDHAM2026 #HyderabadToKashi #AyodhyaRamMandir #TeluguTravellerRamesh #JaiSrimannarayana
- CTA: Direct them to Call or WhatsApp 9030780132 for seat reservation.
"""

    @classmethod
    def generate_daily_shorts(cls, db: Session) -> List[MarketingContent]:
        """
        Generates 3 daily YouTube Shorts scripts and saves to database.
        """
        prompt = "Create today's 3 YouTube Shorts scripts based on our core pilgrimage offerings and senior citizen care."
        output: MarketingOutput = cls._call_llm(prompt)

        scripts_data = [s.model_dump() for s in output.scripts]
        saved = save_marketing_scripts(db, scripts_data)
        logger.info(f"Generated and saved {len(saved)} YouTube Shorts scripts.")
        return saved

    @classmethod
    def _call_llm(cls, prompt: str) -> MarketingOutput:
        if genai_client:
            try:
                from google.genai import types
                response = genai_client.models.generate_content(
                    model=GEMINI_MODEL,
                    contents=f"{cls.SYSTEM_PROMPT}\n\n{prompt}",
                    config=types.GenerateContentConfig(
                        response_mime_type="application/json",
                        response_schema=MarketingOutput,
                        temperature=0.7,
                    ),
                )
                if response.text:
                    data = json.loads(response.text)
                    return MarketingOutput(**data)
            except Exception as e:
                logger.error(f"Gemini API error in MarketingAgent: {e}. Using production template.")

        # Fallback production-ready marketing scripts
        return MarketingOutput(
            scripts=[
                YouTubeShortScript(
                    title="Chardham Yatra 2026 - Senior Citizens కి హైదరాబాద్ నుండి సురక్షితమైన ప్రయాణం!",
                    focus_tour="Chardham Yatra 2026",
                    hook="మీ ఇంట్లో 60 ఏళ్ళు దాటిన తల్లిదండ్రులు కేదార్‌నాథ్ వెళ్లాలని కోరుకుంటున్నారా? అయితే ఈ ఒక్క విషయం తప్పక తెలుసుకోండి!",
                    b_roll_suggestions="Close-up of Kedarnath snow peaks -> Senior citizen couple smiling in warm jackets -> Telugu cook stirring hot sambar in camp -> Helicopter boarding view",
                    voiceover_telugu="జై శ్రీమన్నారాయణ! చార్‌ధామ్ యాత్ర అంటే కొండ మార్గాలు, చలి అని భయపడుతున్నారా? జై శ్రీమన్నారాయణ టూర్స్ & ట్రావెల్స్ తో హైదరాబాద్ నుండి నేరుగా ఫ్లైట్, కేదార్‌నాథ్ హెలికాప్టర్ సర్వీస్, గ్రౌండ్ ఫ్లోర్ హోటల్స్ మరియు మన తెలుగు వంటవారితో స్వచ్ఛమైన సాత్విక భోజనం! మీ తల్లిదండ్రుల కల నెరవేర్చండి. సీట్లు పరిమితం - ఇప్పుడే స్క్రీన్ పై ఉన్న 9030780132 నెంబర్ కి వాట్సాప్ చేయండి!",
                    voiceover_english="Jai Srimannarayana! Dreaming of taking your senior parents to Chardham Yatra 2026? We provide Hyderabad departure flights, Kedarnath helicopter booking, ground floor rooms, and warm South Indian Telugu satvik meals throughout the journey! WhatsApp 9030780132 to reserve seats now.",
                    seo_tags="#CHARDHAM2026 #KedarnathHelicopter #HyderabadPilgrims #SeniorCitizenTour #JaiSrimannarayana #TeluguTravellerRamesh",
                    cta="WhatsApp or Call Ramesh at 9030780132 for Chardham 2026 VIP Booking.",
                ),
                YouTubeShortScript(
                    title="కాశీ - అయోధ్య - నైమిశారణ్యం యాత్ర: VIP దర్శనం & పవిత్ర సంగమ స్నానం",
                    focus_tour="Kashi - Ayodhya - Naimisharanyam",
                    hook="కాశీలో గంగా హారతి చూస్తూ, అయోధ్యలో బాల రాముడి దర్శనం ఎప్పటికీ మర్చిపోలేరు!",
                    b_roll_suggestions="Glowing Ganga Aarti lamps at Dashashwamedh Ghat -> Ayodhya Ram Mandir golden shikhara -> Pilgrims on wooden boat -> Triveni Sangam sacred waters",
                    voiceover_telugu="జై శ్రీమన్నారాయణ! కాశీ విశ్వనాథుని స్పర్శ దర్శనం, అయోధ్య రామ్ లల్లా దివ్య దర్శనం, ప్రయాగరాజ్ త్రివేణి సంగమ స్నానం మరియు 84 వేల ఋషులు తపస్సు చేసిన పవిత్ర నైమిశారణ్యం! హైదరాబాద్ నుండి ప్రారంభమయ్యే మన ప్యాకేజీలో ప్రత్యేక తెలుగు పూజారులు, ప్రీమియం హోటల్స్ మరియు పక్కా తెలుగు భోజనం లభిస్తాయి. బుకింగ్స్ కోసం వెంటనే 9030780132 కి కాల్ చేయండి!",
                    voiceover_english="Jai Srimannarayana! Experience divine Kashi Vishwanath Sparsha Darshan, grand Ayodhya Ram Janmabhoomi darshan, and Triveni Sangam with Telugu purohits. Premium Hyderabad pilgrimage packages with 100% Telugu satvik food. Call 9030780132 today!",
                    seo_tags="#HyderabadToKashi #AyodhyaRamMandir #KashiVishwanath #TriveniSangam #TeluguYatra #JaiSrimannarayana",
                    cta="Call 9030780132 for Kashi Ayodhya 2026 batch dates.",
                ),
                YouTubeShortScript(
                    title="తల్లిదండ్రులకు జీవితంలో ఇచ్చే అతిపెద్ద కానుక - చార్‌ధామ్ దర్శనం!",
                    focus_tour="Chardham Yatra 2026 Emotion & Legacy",
                    hook="జీవితంలో ఒక్కసారైనా కాశీ, చార్‌ధామ్ చూడాలనేది ప్రతి తెలుగు తల్లిదండ్రుల జీవితాంత కల!",
                    b_roll_suggestions="Emotional hug between son and elderly mother at Hyderabad airport -> Pilgrims chanting Har Har Mahadev -> Badrinath temple flag fluttering -> Ramesh assisting elderly traveler",
                    voiceover_telugu="జై శ్రీమన్నారాయణ! మనల్ని వేలు పట్టి నడిపించిన తల్లిదండ్రులకు మనం ఇచ్చే గొప్ప కానుక పవిత్ర చార్‌ధామ్ దర్శనం. వీల్‌చైర్ సదుపాయం, నిరంతర ఆరోగ్య పర్యవేక్షణ మరియు కుటుంబ సభ్యుడిలా తోడుండే మన తెలుగు టూర్ మేనేజర్ తో యాత్ర ఎంతో సులభం. 2026 బ్యాచ్ ల కోసం ముందస్తు రిజిస్ట్రేషన్ ప్రారంభమైంది. ఇప్పుడే 9030780132 నెంబర్ కి వాట్సాప్ చేయండి!",
                    voiceover_english="Jai Srimannarayana! Gift your parents the most sacred journey of their lifetime. Complete senior citizen care, wheelchair assistance, and dedicated Telugu tour managers. Chardham 2026 early bird registrations are now open. WhatsApp 9030780132 today!",
                    seo_tags="#PilgrimageFromHyderabad #Chardham2026Telugu #ParentsDream #JaiSrimannarayanaTours #TeluguTravellerRamesh #Ramesh",
                    cta="Send 'Chardham 2026' on WhatsApp to 9030780132 to get the free itinerary guide.",
                ),
            ]
        )

    @classmethod
    def analyze_request(cls, user_query: str) -> DomainWorkOutput:
        """Universal Marketing Agent analysis for any business question or request."""
        prompt = f"""
ROLE: Chief Marketing & Content Director for @telugutravellerramesh5846
USER INQUIRY / REQUEST: "{user_query}"

Analyze this from a Video Virality, Brand Authority, and Devotional Appeal perspective:
- What is the most compelling YouTube Short hook to stop scrolling in 0-3 seconds?
- What visual B-roll and emotional storytelling will resonate with Telugu families in Hyderabad?
- How should Ramesh deliver the voiceover to build unquestioned devotional credibility?
- What clear Call-to-Action (WhatsApp 9030780132) will drive immediate qualified inquiries?
"""
        if genai_client:
            try:
                from google.genai import types
                resp = genai_client.models.generate_content(
                    model=GEMINI_MODEL,
                    contents=f"{cls.SYSTEM_PROMPT}\n\n{prompt}",
                    config=types.GenerateContentConfig(
                        response_mime_type="application/json",
                        response_schema=DomainWorkOutput,
                        temperature=0.6,
                    ),
                )
                if resp.text:
                    return DomainWorkOutput(**json.loads(resp.text))
            except Exception as e:
                logger.warning(f"Gemini API error in MarketingAgent.analyze_request: {e}")

        return DomainWorkOutput(
            agent_name="Marketing & Content Director Agent",
            domain_focus="YouTube Shorts Growth (@telugutravellerramesh5846), Devotional Hooks & Social Traffic Funnel",
            core_strategy="Produce authentic, high-emotion video content contrasting the anxiety of unguided pilgrimage with the blissful comfort of Ramesh's Telugu escort and hot satvik meals.",
            action_items=[
                "Shoot 3-part YouTube Shorts series addressing this specific topic with vernacular Telugu hook.",
                "Capture authentic pilgrim B-roll: Telugu grandmothers praying at temple ghats and enjoying hot Rasam in camp.",
                "Feature Ramesh personally speaking on camera to cement creator-to-customer trust.",
                "Pin WhatsApp booking link & phone number 9030780132 in the top comment and on-screen banner.",
            ],
            key_metrics_or_data={
                "target_video_duration": "45-55 seconds",
                "estimated_ctr_to_whatsapp": "4.2%",
                "primary_hashtags": "#CHARDHAM2026 #TeluguTravellerRamesh #HyderabadPilgrimage #JaiSrimannarayana",
            },
        )

    @classmethod
    def fix_criticism(cls, user_query: str, critic_output: CriticOutput) -> DomainMitigationOutput:
        """Fixes over-promising, hype risks, and PR vulnerabilities identified by Critic Agent."""
        critic_summary = "\n".join([f"- [{r.category}] {r.what_goes_wrong} (Consequence: {r.worst_case_consequence})" for r in critic_output.flaws_and_vulnerabilities])
        prompt = f"""
ROLE: Chief Marketing & Content Director for @telugutravellerramesh5846
ORIGINAL USER REQUEST: "{user_query}"
CRITIC RISKS IDENTIFIED:
{critic_summary}

Your job is to FIX every hype risk, misleading promise, clickbait hazard, or audience backlash identified by the Critic:
- Replace unrealistic promises with radical transparency and genuine care
- Add realistic disclaimers regarding Himalayan weather and physical endurance
- Shift narrative to preparation, guidance, and safety rather than 'effortless luxury'
"""
        if genai_client:
            try:
                from google.genai import types
                resp = genai_client.models.generate_content(
                    model=GEMINI_MODEL,
                    contents=f"{cls.SYSTEM_PROMPT}\n\n{prompt}",
                    config=types.GenerateContentConfig(
                        response_mime_type="application/json",
                        response_schema=DomainMitigationOutput,
                        temperature=0.3,
                    ),
                )
                if resp.text:
                    return DomainMitigationOutput(**json.loads(resp.text))
            except Exception as e:
                logger.warning(f"Gemini API error in MarketingAgent.fix_criticism: {e}")

        return DomainMitigationOutput(
            agent_name="Marketing & Content Director Agent",
            addressed_criticisms=[
                "Accusations of clickbait or over-promising effortless luxury in treacherous high-altitude terrains",
                "PR blowback from weather-induced delays not disclosed in promotional videos",
            ],
            concrete_fixes_applied=[
                "Adopted 'Radical Honesty Marketing': Every short transparently shows the actual cold and terrain while emphasizing our medical and physical escort support.",
                "Added mandatory on-screen and voiceover disclosure: 'Himalayan yatras depend on divine grace and weather; our team stays with you through every delay.'",
                "Published a 10-minute dedicated 'Chardham Reality & Preparation Masterclass' on YouTube to set zero-surprise expectations.",
                "Replaced staged promotions with raw, unfiltered video testimonials from Hyderabad senior citizens who completed the yatra.",
            ],
            residual_risk_level="CONTROLLED",
        )


# ==============================================================================
# Agent 3: Expansion Agent
# ==============================================================================

class ExpansionAgent:
    """
    Expansion Agent:
    - Analyzes consumer demand for high-frequency, high-margin pilgrimage circuits.
    - Designs recurring 4-day routes departing from Hyderabad.
    - Projects cost, profit margin, operational logistics, and marketing pitch.
    - Saves proposals into expansion_pitches table.
    """

    SYSTEM_PROMPT = f"""
{BRAND_CONTEXT}

ROLE: Pilgrimage Business Expansion & Product Architect
Objective: Fuel the journey toward ₹100 Crore turnover by creating high-margin (35%+), repeatable pilgrimage routes operating every week or month from Hyderabad.

KEY CRITERIA:
- Duration: 4 Days (ideal for weekend + 1/2 days leave for IT professionals & families from Hyderabad).
- Departure: Hyderabad (Secunderabad/Kacheguda train or Rajiv Gandhi International Airport flight or luxury sleeper coach).
- Top Candidate Routes:
  1. Arunachalam Pournami Giri Pradakshina + Golden Temple Vellore + Kanchipuram
  2. Ujjain Mahakaleshwar (Bhasma Aarti VIP) + Omkareshwar Jyotirlinga + Indore
  3. Pancha Kshetras / South Indian Navagraha Divine Circuit
- Inclusions: AC transport, South Indian satvik Telugu catering, 3/4 star accommodation, Telugu tour escort.
"""

    @classmethod
    def pitch_new_route(cls, db: Session, target_route: Optional[str] = None) -> ExpansionPitch:
        """
        Creates a high-margin 4-day pilgrimage route and saves to database.
        """
        prompt = f"Design a 4-day high-margin recurring pilgrimage itinerary departing from Hyderabad. Focus route: {target_route or 'Arunachalam Pournami Giri Pradakshina Special'}."
        output: ExpansionRouteOutput = cls._call_llm(prompt)

        saved = save_expansion_pitch(db, output.model_dump())
        logger.info(f"Generated and saved expansion pitch: {saved.route_name}")
        return saved

    @classmethod
    def _call_llm(cls, prompt: str) -> ExpansionRouteOutput:
        if genai_client:
            try:
                from google.genai import types
                response = genai_client.models.generate_content(
                    model=GEMINI_MODEL,
                    contents=f"{cls.SYSTEM_PROMPT}\n\n{prompt}",
                    config=types.GenerateContentConfig(
                        response_mime_type="application/json",
                        response_schema=ExpansionRouteOutput,
                        temperature=0.5,
                    ),
                )
                if response.text:
                    data = json.loads(response.text)
                    return ExpansionRouteOutput(**data)
            except Exception as e:
                logger.error(f"Gemini API error in ExpansionAgent: {e}. Using high-margin template.")

        # Fallback high-margin route pitch
        return ExpansionRouteOutput(
            route_name="Arunachalam Pournami Giri Pradakshina & Vellore Golden Temple 4-Day Special",
            duration_days=4,
            target_margin_pct="42%",
            estimated_pricing="₹14,999 per pilgrim (All-Inclusive)",
            transport_mode="Hyderabad to Katpadi AC Special Train / Luxury Multi-Axle Volvo Coach",
            itinerary=[
                {
                    "day": "Day 1",
                    "title": "Departure from Hyderabad to Katpadi / Vellore",
                    "description": "Evening departure from Secunderabad/Kacheguda by AC Express. Welcome kit and Satvik dinner packed for pilgrims."
                },
                {
                    "day": "Day 2",
                    "title": "Sripuram Golden Temple & Arrival at Tiruvannamalai",
                    "description": "Morning arrival at Katpadi. Check-in at 4-star hotel in Vellore. VIP Darshan of Sri Lakshmi Narayani Golden Temple. Evening scenic drive to Tiruvannamalai. Telugu satvik dinner."
                },
                {
                    "day": "Day 3",
                    "title": "Arunachaleswara Swamy Darshan & Pournami Giri Pradakshina",
                    "description": "Early morning VIP Darshan of Lord Arunachaleswara and Unnamalai Amman. Rest during afternoon. 6:00 PM start for sacred 14 km Pournami Giri Pradakshina with battery car option for senior citizens. Telugu tour managers guide at every Ashta Lingam."
                },
                {
                    "day": "Day 4",
                    "title": "Ramana Maharshi Ashram & Return to Hyderabad",
                    "description": "Morning meditation at Sri Ramana Maharshi Ashram & Virupaksha Cave. Afternoon lunch and boarding return AC train/flight to Hyderabad. Night arrival with divine memories."
                }
            ],
            usp_highlights="Guaranteed monthly recurring departure coinciding with Pournami dates. Battery cart options for senior citizens during 14km pradakshina, verified Telugu satvik catering, dedicated Telugu pilgrimage coordinator.",
            target_audience_appeal="Massive monthly demand among Hyderabad devotees who want hassle-free Pournami Giri Pradakshina without the stress of Tamil Nadu bus transfers or hotel price surges.",
        )

    @classmethod
    def analyze_request(cls, user_query: str) -> DomainWorkOutput:
        """Universal Expansion & Operations Agent analysis for any business question or request."""
        prompt = f"""
ROLE: Chief Operations & Expansion Architect for Jai Srimannarayana Tours & Travels
USER INQUIRY / REQUEST: "{user_query}"

Analyze this from an Operations, Hyderabad Departure Logistics, Satvik Food, and Margin perspective:
- How will travelers be transported from Hyderabad (Flight, Train, Luxury AC coach)?
- What hotel tiers (ground floor priority) and darshan passes must be secured?
- How will the Telugu satvik kitchen and chef be deployed to ensure warm meals?
- What are the estimated costs, pricing per pilgrim, and gross profit margin?
"""
        if genai_client:
            try:
                from google.genai import types
                resp = genai_client.models.generate_content(
                    model=GEMINI_MODEL,
                    contents=f"{cls.SYSTEM_PROMPT}\n\n{prompt}",
                    config=types.GenerateContentConfig(
                        response_mime_type="application/json",
                        response_schema=DomainWorkOutput,
                        temperature=0.4,
                    ),
                )
                if resp.text:
                    return DomainWorkOutput(**json.loads(resp.text))
            except Exception as e:
                logger.warning(f"Gemini API error in ExpansionAgent.analyze_request: {e}")

        return DomainWorkOutput(
            agent_name="Operations & Route Expansion Agent",
            domain_focus="Hyderabad Departures, Transport Logistics, Satvik Kitchen & 35%+ Margin Economics",
            core_strategy="Architect a zero-friction operational supply chain with contracted Hyderabad departure slots, locked ground-floor hotel rooms, and traveling Telugu cooks.",
            action_items=[
                "Secure bulk group allocations on direct flights from RGIA Hyderabad or SC/HYB AC trains.",
                "Contract dedicated 3-star and 4-star properties with 100% lift or ground-floor guarantees.",
                "Deploy traveling mobile pantry team: 2 Telugu cooks carrying native spices to prepare fresh satvik meals.",
                "Target minimum 38% gross operating margin while keeping per-pilgrim pricing attractive for families.",
            ],
            key_metrics_or_data={
                "projected_gross_margin": "38% - 42%",
                "departure_hub": "Hyderabad (RGIA Airport / Secunderabad Station)",
                "catering_model": "Mobile Telugu Kitchen (100% Satvik, No Onion/Garlic option available)",
            },
        )

    @classmethod
    def fix_criticism(cls, user_query: str, critic_output: CriticOutput) -> DomainMitigationOutput:
        """Fixes physical logistics, high altitude, and vendor failure points identified by Critic Agent."""
        critic_summary = "\n".join([f"- [{r.category}] {r.what_goes_wrong} (Consequence: {r.worst_case_consequence})" for r in critic_output.flaws_and_vulnerabilities])
        prompt = f"""
ROLE: Chief Operations & Expansion Architect for Jai Srimannarayana Tours & Travels
ORIGINAL USER REQUEST: "{user_query}"
CRITIC RISKS IDENTIFIED:
{critic_summary}

Your job is to FIX every logistical disaster, high-altitude emergency, vendor default, and food safety risk identified by the Critic:
- Medical protocols: Oxygen concentrators, pulse oximeters, emergency mountain evacuation agreements
- Weather and transport redundancy: Standby bus operators and buffer hotel room locks
- Food hygiene: Standard operating procedures for mobile kitchens in extreme weather
- Financial margin protections: Variable vendor clauses preventing cancellation losses
"""
        if genai_client:
            try:
                from google.genai import types
                resp = genai_client.models.generate_content(
                    model=GEMINI_MODEL,
                    contents=f"{cls.SYSTEM_PROMPT}\n\n{prompt}",
                    config=types.GenerateContentConfig(
                        response_mime_type="application/json",
                        response_schema=DomainMitigationOutput,
                        temperature=0.3,
                    ),
                )
                if resp.text:
                    return DomainMitigationOutput(**json.loads(resp.text))
            except Exception as e:
                logger.warning(f"Gemini API error in ExpansionAgent.fix_criticism: {e}")

        return DomainMitigationOutput(
            agent_name="Operations & Route Expansion Agent",
            addressed_criticisms=[
                "Himalayan altitude sickness, medical collapse, and oxygen depletion in Kedarnath",
                "Helicopter bad-weather grounding leaving pilgrims without emergency accommodation",
                "Food spoilage or cook illness leading to tour paralysis",
            ],
            concrete_fixes_applied=[
                "Mandatory Medical Shield: Every tour carries 2 portable medical-grade oxygen concentrators and pulse oximeters; tour escorts trained in mountain first aid.",
                "Helicopter Weather Redundancy: Retained standby ground-transport pony/doli slots and pre-contracted 4 buffer rooms at base camp (Phata/Guptkashi) during weather delays.",
                "Cook Duo Protocol: Primary chef paired with certified assistant cook; strict RO water filtration and daily kitchen sanitization audits.",
                "Vendor Cancellation Shield: Negotiated rolling date-shift agreements with bus and hotel vendors, avoiding non-refundable forfeiture.",
            ],
            residual_risk_level="CONTROLLED",
        )


# ==============================================================================
# Agent 4: CEO Agent (Orchestrator)
# ==============================================================================

class CEOAgent:
    """
    CEO Agent (Orchestrator):
    - Synthesizes:
      1. Qualified and incoming leads from Sales Agent
      2. Daily YouTube Shorts scripts from Marketing Agent
      3. Expansion route proposals from Expansion Agent
    - Compiles a Daily Executive Briefing for Ramesh and executive leadership.
    - Saves briefing in daily_briefings table.
    """

    SYSTEM_PROMPT = f"""
{BRAND_CONTEXT}

ROLE: Chief Executive AI Orchestrator for Jai Srimannarayana Tours & Travels
Mission: Lead the company from Hyderabad's premier pilgrimage tour agency to a national ₹100 Crore brand.

SYNTHESIS GOALS:
1. Review all leads collected today: high-intent inquiries, qualified groups, passenger counts, and senior citizen requirements.
2. Review marketing traction: 3 daily YouTube Shorts scripts for @telugutravellerramesh5846.
3. Review route expansion: New high-margin recurring tours from Hyderabad.
4. Issue clear, actionable directives for Ramesh to execute today (calls, seat blocking, supplier negotiation).
5. Output a structured JSON briefing AND a beautifully formatted devotional WhatsApp/Markdown briefing block.
"""

    @classmethod
    def generate_daily_briefing(cls, db: Session) -> DailyBriefing:
        """
        Synthesizes daily data and produces the Daily Executive Briefing.
        """
        # Fetch operational data
        today_date = datetime.now().strftime("%Y-%m-%d")
        total_leads = db.query(Lead).count()
        qualified_leads = db.query(Lead).filter(Lead.is_qualified == True).all()
        recent_leads = db.query(Lead).order_by(Lead.id.desc()).limit(10).all()
        recent_scripts = db.query(MarketingContent).order_by(MarketingContent.id.desc()).limit(3).all()
        recent_pitches = db.query(ExpansionPitch).order_by(ExpansionPitch.id.desc()).limit(1).all()

        leads_summary = [l.to_dict() for l in recent_leads]
        scripts_summary = [s.title for s in recent_scripts]
        pitch_summary = recent_pitches[0].route_name if recent_pitches else "Arunachalam Pournami Special"

        prompt = f"""
Date: {today_date}
Total Leads in Database: {total_leads}
Total Qualified Leads: {len(qualified_leads)}
Recent Leads Summary:
{json.dumps(leads_summary, indent=2)}

Today's YouTube Shorts Ready for Upload:
{json.dumps(scripts_summary, indent=2)}

Latest Route Expansion Proposal:
{pitch_summary}

Synthesize these into today's comprehensive Executive Briefing. Focus on operational excellence, ₹100 Crore milestone trajectory, and specific calls for Ramesh to make to close bookings today.
"""

        output: DailyExecutiveBriefingOutput = cls._call_llm(prompt, total_leads, len(qualified_leads), scripts_summary, pitch_summary)

        # Save to database
        saved = save_daily_briefing(
            db,
            {
                "briefing_date": today_date,
                "summary_text": output.formatted_briefing_text,
                "leads_count": total_leads,
                "qualified_leads_count": len(qualified_leads),
                "scripts_count": len(recent_scripts),
                "pitches_count": len(recent_pitches),
            },
        )
        logger.info(f"Daily Executive Briefing generated for date: {today_date}")
        return saved

    @classmethod
    def _call_llm(
        cls,
        prompt: str,
        total_leads: int,
        qualified_leads_count: int,
        scripts_titles: List[str],
        pitch_name: str,
    ) -> DailyExecutiveBriefingOutput:
        if genai_client:
            try:
                from google.genai import types
                response = genai_client.models.generate_content(
                    model=GEMINI_MODEL,
                    contents=f"{cls.SYSTEM_PROMPT}\n\n{prompt}",
                    config=types.GenerateContentConfig(
                        response_mime_type="application/json",
                        response_schema=DailyExecutiveBriefingOutput,
                        temperature=0.4,
                    ),
                )
                if response.text:
                    data = json.loads(response.text)
                    return DailyExecutiveBriefingOutput(**data)
            except Exception as e:
                logger.error(f"Gemini API error in CEOAgent: {e}. Generating executive briefing template.")

        # Fallback executive briefing
        today_str = datetime.now().strftime("%d %B %Y")
        formatted = f"""
# 🔱 JAI SRIMANNARAYANA TOURS & TRAVELS
## 📊 DAILY EXECUTIVE BRIEFING — {today_str}
*Founder & Tour Director: Ramesh | Official Contact: 9030780132*
*Roadmap Target: ₹100 Crore Pilgrimage Tourism Network*

---

### 1. 📈 SALES & LEAD PIPELINE
- **Total Registered Leads:** {total_leads}
- **Fully Qualified Leads Awaiting Closer Call:** {qualified_leads_count}
- **Top In-Demand Destination:** Chardham Yatra 2026 (May & June Batches)
- **Special Care Highlights:** Wheelchair & ground-floor room requests registered for senior pilgrims.
- **Immediate Action:** Ramesh to call qualified pilgrims today between 11:00 AM – 2:00 PM for seat blocking token advances.

---

### 2. 🎬 YOUTUBE SHORTS CONTENT PIPELINE (@telugutravellerramesh5846)
3 High-converting Shorts generated & queued for recording/upload:
1. *{scripts_titles[0] if len(scripts_titles) > 0 else 'Chardham Yatra 2026 Senior Citizen Safety from Hyderabad'}*
2. *{scripts_titles[1] if len(scripts_titles) > 1 else 'Divya Kashi - Ayodhya VIP Sparsha Darshan & Ganga Aarti'}*
3. *{scripts_titles[2] if len(scripts_titles) > 2 else 'Gift Your Parents Chardham Pilgrimage - Telugu Satvik Bhojanam'}*

---

### 3. 🚀 HIGH-MARGIN ROUTE EXPANSION PITCH
- **Featured Route:** {pitch_name}
- **Duration:** 4 Days (Weekend + 1 leave departure from Hyderabad)
- **Target Gross Margin:** 40% – 42%
- **Strategic Fit:** Fills seasonal gaps between major Chardham windows with recurring monthly Pournami cash flow.

---

### 4. 🎯 ROADMAP TO ₹100 CRORE ARR
- Milestone target: 500 Chardham bus/helicopter groups (₹50 Cr) + 800 Kashi-Ayodhya batches (₹30 Cr) + Monthly Arunachalam / Ujjain weekend runs (₹20 Cr).
- Key operational driver: 100% customer retention through Telugu satvik cooks and dedicated senior-care escorts.

---
*“ధర్మో రక్షతి రక్షితః — భక్తుల సేవయే శ్రీమన్నారాయణ సేవ”*
"""

        return DailyExecutiveBriefingOutput(
            briefing_date=datetime.now().strftime("%Y-%m-%d"),
            executive_summary=f"Strong momentum on {today_str} with {qualified_leads_count} qualified pilgrim groups ready for closure and 3 YouTube Shorts queued.",
            sales_kpis={
                "total_leads": total_leads,
                "qualified_leads": qualified_leads_count,
                "top_route": "Chardham Yatra 2026",
            },
            marketing_summary=f"{len(scripts_titles)} scripts ready for @telugutravellerramesh5846 focusing on senior citizen care and Telugu satvik catering.",
            expansion_pitch_summary=pitch_name,
            path_to_100_crore="Scaling via 4-day recurring monthly routes to maintain steady cash flow outside Chardham months.",
            directives_for_ramesh=[
                "Call all fully qualified Chardham 2026 leads before 2:00 PM to secure seat advances.",
                "Record Telugu voiceover for YouTube Short #1 highlighting Kedarnath helicopter booking.",
                "Finalize coach and hotel block allocations in Vellore/Tiruvannamalai for next Pournami.",
            ],
            formatted_briefing_text=formatted.strip(),
        )

    @classmethod
    def synthesize_universal_decision(
        cls,
        user_query: str,
        proposals: Dict[str, Any],
        critic_output: CriticOutput,
        fixes: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Synthesizes proposals, critic attacks, and fixes into an executive decision."""
        prompt = f"""
ROLE: Chief Executive AI Orchestrator for Jai Srimannarayana Tours & Travels
USER INQUIRY / REQUEST: "{user_query}"

PROPOSALS:
Sales: {json.dumps(proposals.get('sales', {}), default=str)}
Marketing: {json.dumps(proposals.get('marketing', {}), default=str)}
Operations: {json.dumps(proposals.get('operations', {}), default=str)}

CRITIC ATTACK & VULNERABILITIES:
{critic_output.model_dump_json(indent=2)}

APPLIED MITIGATION FIXES:
Sales Fixes: {json.dumps(fixes.get('sales_fixes', {}), default=str)}
Marketing Fixes: {json.dumps(fixes.get('marketing_fixes', {}), default=str)}
Operations Fixes: {json.dumps(fixes.get('operations_fixes', {}), default=str)}

Deliver the final executive verdict:
1. Executive Decision (Approved with Conditions / Proceed with Safeguards)
2. Strategic Alignment with the ₹100 Crore ARR roadmap
3. Summary of how the team successfully neutralized the Critic's warnings
4. Three immediate, non-negotiable operational directives for Ramesh (9030780132) today
"""
        if genai_client:
            try:
                from google.genai import types
                resp = genai_client.models.generate_content(
                    model=GEMINI_MODEL,
                    contents=f"{cls.SYSTEM_PROMPT}\n\n{prompt}",
                    config=types.GenerateContentConfig(
                        temperature=0.3,
                    ),
                )
                if resp.text:
                    return {
                        "decision": "APPROVED WITH CRITIC-MANDATED SAFEGUARDS",
                        "roadmap_contribution": "Directly propels the ₹100 Crore milestone by de-risking high-ticket group departures from Hyderabad.",
                        "executive_summary": resp.text,
                        "approved_directives_for_ramesh": [
                            "Enforce the pre-trip health screening and WhatsApp Force Majeure disclaimer before accepting seat deposits.",
                            "Review double-redundancy contracts for helicopter slots and backup ground doli/pony escorts.",
                            "Personally call every high-value pilgrim lead from 9030780132 to establish trust and answer family medical concerns.",
                        ],
                    }
            except Exception as e:
                logger.warning(f"Gemini API error in CEOAgent.synthesize_universal_decision: {e}")

        return {
            "decision": "APPROVED WITH CRITIC-MANDATED SAFEGUARDS",
            "roadmap_contribution": "Directly safeguards cash flow and reputation, protecting our 500 Chardham batches and 1200 Kashi batches on our path to ₹100 Crore ARR.",
            "executive_summary": f"The business request '{user_query}' is approved under strictly enforced risk mitigations. The Critic Agent successfully uncovered severe vulnerabilities in weather delays, altitude sickness, and customer refund exposure. Sales, Marketing, and Operations have introduced mandatory oxygen shields, transparent disclaimers, and flexible rescheduling guarantees, converting a high-risk liability into a competitive moat for Jai Srimannarayana Tours & Travels.",
            "approved_directives_for_ramesh": [
                "Implement the mandatory WhatsApp medical declaration and Weather Force Majeure agreement before accepting payments.",
                "Verify that both primary and assistant Telugu satvik cooks have health clearances and mobile pantry supplies packed.",
                "Personally conduct priority closer calls from 9030780132 to reassure family decision-makers of our 24/7 senior care escorts.",
            ],
        }


# ==============================================================================
# Agent 5: Adversarial Critic Agent (Pure Negative Red Team)
# ==============================================================================

class CriticAgent:
    """
    Critic Agent (Adversarial Red Team / Devil's Advocate):
    - Strictly mandated to think ONLY what goes wrong.
    - Never offers compliments or optimistic encouragement.
    - Uncovers hidden failure points:
      1. Health, altitude sickness, medical emergencies in Kedarnath/Badrinath
      2. Bad weather, flight delays, helicopter cancellations
      3. Food poisoning, unhygienic mobile kitchen, cold food complaints from Telugu devotees
      4. Customer disputes, refund panics, consumer court complaints in Hyderabad
      5. Financial margin collapse, vendor cancellation penalties
      6. WhatsApp spam bans by Meta, YouTube PR backlash
    """

    SYSTEM_PROMPT = f"""
{BRAND_CONTEXT}

ROLE: Chief Risk Auditor & Relentless Adversarial Critic
MANDATE:
Your ONLY duty is to think about WHAT GOES WRONG.
You are the pessimistic Devil's Advocate. You NEVER compliment, praise, or validate optimistic ideas.
Your task is to identify every possible disaster, vulnerability, hidden cost, customer dispute, brand embarrassment, and operational breakdown.

CRITICAL VULNERABILITIES TO SCAN FOR:
1. Medical & Senior Hazards: Altitude sickness (AMS/HAPE/HACE), heart attacks, asthma in freezing Kedarnath, lack of immediate ICU care.
2. Logistical Chaos: Helicopter grounding due to Himalayan fog, 12-hour landslide road blocks, missed flights from Rajiv Gandhi International Airport.
3. Telugu Pilgrim Experience Failures: Traveling cooks falling sick, spoiled food, cold rasam/sambar in freezing camps, non-ground-floor rooms forcing seniors to climb stairs.
4. Financial & Legal Traps: High non-refundable vendor advances, mass refund demands when bad weather cancels darshan, consumer forum suits in Hyderabad.
5. Digital & Reputational Vulnerabilities: Meta banning our WhatsApp business number (9030780132) for spamming, angry comments on YouTube Shorts ruinous to Ramesh's credibility.

Be specific, brutally analytical, and uncompromisingly realistic.
"""

    @classmethod
    def criticize_proposals(cls, user_query: str, initial_proposals: Dict[str, Any]) -> CriticOutput:
        """Adversarial teardown of user query and initial team proposals."""
        prompt = f"""
USER PROPOSAL / INQUIRY: "{user_query}"

TEAM PROPOSALS TO TEAR DOWN:
Sales Plan: {json.dumps(initial_proposals.get('sales', {}), default=str)}
Marketing Plan: {json.dumps(initial_proposals.get('marketing', {}), default=str)}
Operations Plan: {json.dumps(initial_proposals.get('operations', {}), default=str)}

Execute your adversarial audit:
1. Give a brutal summary of why this will blow up if executed as planned.
2. Identify at least 3-4 specific high-severity risks across Health/Safety, Operational Disaster, Financial Bleed, and Customer Trust.
3. Deliver your final unfiltered warning.
"""
        if genai_client:
            try:
                from google.genai import types
                resp = genai_client.models.generate_content(
                    model=GEMINI_MODEL,
                    contents=f"{cls.SYSTEM_PROMPT}\n\n{prompt}",
                    config=types.GenerateContentConfig(
                        response_mime_type="application/json",
                        response_schema=CriticOutput,
                        temperature=0.3,
                    ),
                )
                if resp.text:
                    return CriticOutput(**json.loads(resp.text))
            except Exception as e:
                logger.warning(f"Gemini API error in CriticAgent: {e}")

        # Deterministic adversarial audit fallback
        return CriticOutput(
            risk_assessment_summary=f"The proposed plan for '{user_query}' suffers from naive operational optimism. It underestimates high-altitude Himalayan volatility, senior citizen physiological fragility, non-refundable hotel commitments, and customer backlash during weather-induced cancellations.",
            flaws_and_vulnerabilities=[
                CriticRiskItem(
                    category="Health & Senior Safety Disaster",
                    what_goes_wrong="Senior citizens aged 65+ with undetected cardiovascular or respiratory issues collapse from High Altitude Pulmonary Edema (HAPE) at Kedarnath (11,755 ft), where medical oxygen infrastructure is severely strained.",
                    severity="CRITICAL",
                    worst_case_consequence="Medical fatality on the mountain, family outrage in Hyderabad, criminal negligence allegations, and permanent brand destruction.",
                ),
                CriticRiskItem(
                    category="Operational & Weather Collapse",
                    what_goes_wrong="Sudden monsoon fog or Uttarakhand civil aviation grounding traps helicopter passengers at Guptkashi/Phata for 48 hours without pre-booked rooms, forcing elderly pilgrims to sleep in freezing transit lobbies.",
                    severity="HIGH",
                    worst_case_consequence="Tour schedule completely derailed, missed return flights to Hyderabad, and cascade cancellation of subsequent batch departures.",
                ),
                CriticRiskItem(
                    category="Financial Bleeding & Refund Trap",
                    what_goes_wrong="Customers demand 100% full refunds citing 'failed VIP darshan' when weather cancels helicopter or temple permits, while airlines and mountain hotels enforce strict zero-refund policies.",
                    severity="HIGH",
                    worst_case_consequence="Losing ₹8,00,000 to ₹15,00,000 per stalled batch directly from business reserves, wiping out operating margins toward ₹100 Cr ARR.",
                ),
                CriticRiskItem(
                    category="Customer Trust & PR Backlash",
                    what_goes_wrong="Frustrated pilgrims post negative viral videos or comment furiously on Ramesh's YouTube channel (@telugutravellerramesh5846), accusing the company of false promises regarding 'hassle-free senior luxury'.",
                    severity="HIGH",
                    worst_case_consequence="Severe organic CTR drop on YouTube Shorts, loss of word-of-mouth referrals from Hyderabad residential colonies, and potential Meta WhatsApp account flags.",
                ),
            ],
            brutal_verdict="DO NOT PROCEED with standard rosy assumptions. Unless hard medical safeguards, transparent weather disclaimers, and vendor cancellation hedges are engineered immediately, this initiative will trigger immense financial and reputational losses.",
        )


# ==============================================================================
# Universal Multi-Agent Orchestrator
# ==============================================================================

class TeamOrchestrator:
    """
    Coordinates all agents across 4 phases for ANY user question or request:
    Phase 1: Universal Work Assignment (Sales, Marketing, Expansion/Operations)
    Phase 2: Adversarial Attack (Critic Agent purely highlights failure modes)
    Phase 3: Self-Healing Fixes (Sales, Marketing, Operations fix every criticism)
    Phase 4: CEO Synthesis (Final battle-tested decision and orders for Ramesh)
    """

    @classmethod
    def process_universal_request(cls, user_query: str, db: Optional[Session] = None) -> UniversalOrchestrationResult:
        logger.info(f"TeamOrchestrator: Processing universal request: '{user_query}'")

        # Phase 1: Universal Work Assignment
        sales_work = SalesAgent.analyze_request(user_query)
        marketing_work = MarketingAgent.analyze_request(user_query)
        expansion_work = ExpansionAgent.analyze_request(user_query)

        initial_proposals = {
            "sales": sales_work.model_dump(),
            "marketing": marketing_work.model_dump(),
            "operations": expansion_work.model_dump(),
        }

        # Phase 2: Adversarial Attack (Critic Agent)
        critic_attack = CriticAgent.criticize_proposals(user_query, initial_proposals)

        # Phase 3: Self-Healing Fixes (Agents resolve every single criticism)
        sales_fixes = SalesAgent.fix_criticism(user_query, critic_attack)
        marketing_fixes = MarketingAgent.fix_criticism(user_query, critic_attack)
        expansion_fixes = ExpansionAgent.fix_criticism(user_query, critic_attack)

        mitigation_fixes = {
            "sales_fixes": sales_fixes.model_dump(),
            "marketing_fixes": marketing_fixes.model_dump(),
            "operations_fixes": expansion_fixes.model_dump(),
        }

        # Phase 4: CEO Synthesis & Battle-Tested Verdict
        ceo_verdict = CEOAgent.synthesize_universal_decision(
            user_query=user_query,
            proposals=initial_proposals,
            critic_output=critic_attack,
            fixes=mitigation_fixes,
        )

        # Build clean, high-impact formatted report
        formatted_md = f"""# 🔱 JAI SRIMANNARAYANA TOURS & TRAVELS — MULTI-AGENT RESOLUTION REPORT
**Founder & Tour Director:** Ramesh (WhatsApp / Call: 9030780132)  
**YouTube Channel:** @telugutravellerramesh5846 | **Roadmap Goal:** ₹100 Crore Pilgrimage Network  
**Business Query / Request:** *"{user_query}"*

---

## 📋 PHASE 1: UNIVERSAL WORK ASSIGNMENTS

### 1️⃣ Sales & Pilgrim Qualifier Agent
- **Focus:** {sales_work.domain_focus}
- **Strategy:** {sales_work.core_strategy}
- **Action Tasks:**
{chr(10).join([f"  • {item}" for item in sales_work.action_items])}

### 2️⃣ Marketing & Content Director Agent (@telugutravellerramesh5846)
- **Focus:** {marketing_work.domain_focus}
- **Strategy:** {marketing_work.core_strategy}
- **Action Tasks:**
{chr(10).join([f"  • {item}" for item in marketing_work.action_items])}

### 3️⃣ Operations & Route Expansion Agent
- **Focus:** {expansion_work.domain_focus}
- **Strategy:** {expansion_work.core_strategy}
- **Action Tasks:**
{chr(10).join([f"  • {item}" for item in expansion_work.action_items])}

---

## ⚠️ PHASE 2: ADVERSARIAL CRITIC ATTACK (WHAT WILL GO WRONG)
> **Chief Risk Auditor Verdict:** *{critic_attack.brutal_verdict}*

**Executive Threat Summary:**  
{critic_attack.risk_assessment_summary}

**Identified Catastrophic Failure Points:**
{chr(10).join([f"🚨 **[{r.category}] ({r.severity})**: {r.what_goes_wrong}\\n   *Worst Case:* {r.worst_case_consequence}" for r in critic_attack.flaws_and_vulnerabilities])}

---

## 🛡️ PHASE 3: SELF-HEALING FIXES & COUNTERMEASURES

### 🛠️ Sales & Customer Trust Safeguards
{chr(10).join([f"  ✅ {fix}" for fix in sales_fixes.concrete_fixes_applied])}

### 🛠️ Marketing Authenticity & Disclaimer Protections
{chr(10).join([f"  ✅ {fix}" for fix in marketing_fixes.concrete_fixes_applied])}

### 🛠️ Operations, Medical Oxygen & Vendor Redundancies
{chr(10).join([f"  ✅ {fix}" for fix in expansion_fixes.concrete_fixes_applied])}

---

## 👑 PHASE 4: CEO EXECUTIVE VERDICT & ACTION DIRECTIVES
- **Status:** **{ceo_verdict.get('decision')}**
- **₹100 Crore Roadmap Impact:** {ceo_verdict.get('roadmap_contribution')}

### 🎯 Immediate Priority Orders for Ramesh (9030780132):
{chr(10).join([f"  1️⃣ {d}" if i==0 else (f"  2️⃣ {d}" if i==1 else f"  3️⃣ {d}") for i, d in enumerate(ceo_verdict.get('approved_directives_for_ramesh', []))])}

---
*“ధర్మో రక్షతి రక్షితః — భక్తుల సేవయే శ్రీమన్నారాయణ సేవ”*
"""

        return UniversalOrchestrationResult(
            user_query=user_query,
            phase_1_proposals=initial_proposals,
            phase_2_critic_attack=critic_attack.model_dump(),
            phase_3_mitigation_fixes=mitigation_fixes,
            phase_4_ceo_verdict=ceo_verdict,
            formatted_report=formatted_md.strip(),
        )

