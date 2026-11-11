"""
End-to-End Simulation Runner for Jai Srimannarayana Tours & Travels.
Tests:
1. Meta WhatsApp webhook verification (GET /webhook)
2. Multi-turn WhatsApp conversation simulation (POST /webhook) with progressive qualification:
   - Turn 1: Initial inquiry in Telugu about Chardham 2026 from YouTube Shorts
   - Turn 2: Name, passenger count, travel month
   - Turn 3: Senior citizen wheelchair & ground floor room requirements -> Fully Qualified!
3. Marketing Agent: Generates 3 daily YouTube Shorts scripts for @telugutravellerramesh5846
4. Expansion Agent: Generates high-margin 4-day itinerary from Hyderabad
5. CEO Agent (Orchestrator): Compiles Daily Executive Briefing
"""

import json
import sys
import time

# Ensure Windows console supports UTF-8 and Telugu characters
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

from fastapi.testclient import TestClient
from database import SessionLocal, Lead, MarketingContent, ExpansionPitch, DailyBriefing, init_db
from main import app

# Initialize test client
client = TestClient(app)


def print_banner(title: str):
    print("\n" + "=" * 80)
    print(f"🔱  {title}")
    print("=" * 80)


def test_meta_webhook_verification():
    print_banner("1. TESTING META WHATSAPP WEBHOOK VERIFICATION (GET /webhook)")
    verify_token = "***REMOVED***"
    challenge = "115325236"

    # Positive test
    resp = client.get(f"/webhook?hub.mode=subscribe&hub.verify_token={verify_token}&hub.challenge={challenge}")
    print(f"Status Code: {resp.status_code}")
    print(f"Response Challenge: {resp.text}")
    assert resp.status_code == 200
    assert resp.text == challenge
    print("✅ Meta Webhook Verification Passed!")


def simulate_whatsapp_message(phone: str, text: str, sender_name: str, msg_id: str):
    """Simulates exact payload sent by Meta WhatsApp Cloud API."""
    payload = {
        "object": "whatsapp_business_account",
        "entry": [
            {
                "id": "10023456789",
                "changes": [
                    {
                        "value": {
                            "messaging_product": "whatsapp",
                            "metadata": {
                                "display_phone_number": "9030780132",
                                "phone_number_id": "9876543210123"
                            },
                            "contacts": [
                                {
                                    "profile": {"name": sender_name},
                                    "wa_id": phone
                                }
                            ],
                            "messages": [
                                {
                                    "from": phone,
                                    "id": msg_id,
                                    "timestamp": str(int(time.time())),
                                    "text": {"body": text},
                                    "type": "text"
                                }
                            ]
                        },
                        "field": "messages"
                    }
                ]
            }
        ]
    }
    return client.post("/webhook", json=payload)


def test_sales_lead_qualification_flow():
    print_banner("2. TESTING SALES AGENT MULTI-TURN LEAD QUALIFICATION (POST /webhook)")
    test_phone = "919440123456"
    pilgrim_name = "Srinivasa Rao"

    # Turn 1: Initial greeting & interest in Chardham 2026
    turn1_msg = "Jai Srimannarayana! Ramesh video chusamu, Chardham Yatra 2026 details kavali."
    print(f"\n[Pilgrim -> WhatsApp]: '{turn1_msg}'")
    resp1 = simulate_whatsapp_message(test_phone, turn1_msg, pilgrim_name, "wamid.turn1")
    data1 = resp1.json()
    reply1 = data1["details"][0]["reply"]
    print(f"[Sales Agent -> Reply]:\n{reply1}\n")
    print(f"Lead status: {data1['details'][0]['lead_status']}")

    # Turn 2: Traveler specifies pax count and month
    turn2_msg = "Nenu Srinivasa Rao, Hyderabad nundi. Motham 4 members prayanam chestunnamu. May 2026 nela lo."
    print(f"\n[Pilgrim -> WhatsApp]: '{turn2_msg}'")
    resp2 = simulate_whatsapp_message(test_phone, turn2_msg, pilgrim_name, "wamid.turn2")
    data2 = resp2.json()
    reply2 = data2["details"][0]["reply"]
    print(f"[Sales Agent -> Reply]:\n{reply2}\n")
    print(f"Lead status: {data2['details'][0]['lead_status']}")

    # Turn 3: Traveler provides senior citizen requirements -> QUALIFIES LEAD
    turn3_msg = "Maa parents iddaru unnaru, 68 and 72 years. Vaariki wheelchair and ground floor room kavali andi."
    print(f"\n[Pilgrim -> WhatsApp]: '{turn3_msg}'")
    resp3 = simulate_whatsapp_message(test_phone, turn3_msg, pilgrim_name, "wamid.turn3")
    data3 = resp3.json()
    reply3 = data3["details"][0]["reply"]
    print(f"[Sales Agent -> Reply]:\n{reply3}\n")
    print(f"Lead status: {data3['details'][0]['lead_status']}")

    # Verify database persistence
    db = SessionLocal()
    lead = db.query(Lead).filter(Lead.phone_number == test_phone).first()
    assert lead is not None
    print("\n--- Persisted Lead in SQLite ---")
    print(json.dumps(lead.to_dict(), indent=2))
    assert lead.is_qualified == True
    assert lead.status == "QUALIFIED"
    assert lead.destination is not None
    assert lead.pax_count == 4
    db.close()
    print("✅ Multi-turn Lead Qualification & SQLite Persistence Verified!")


def test_marketing_agent():
    print_banner("3. TESTING MARKETING AGENT (POST /marketing/generate)")
    resp = client.post("/marketing/generate")
    assert resp.status_code == 200
    data = resp.json()
    scripts = data["scripts"]
    print(f"Generated {len(scripts)} YouTube Shorts scripts for @telugutravellerramesh5846:")
    for idx, s in enumerate(scripts, 1):
        print(f"\n--- Script #{idx}: {s['title']} ---")
        print(f"Target: {s['focus_tour']}")
        print(f"Hook (0-3s): {s['hook']}")
        print(f"B-Roll: {s['b_roll_suggestions']}")
        print(f"Telugu Voiceover: {s['voiceover_telugu']}")
        print(f"SEO Tags: {s['seo_tags']}")
        print(f"CTA: {s['cta']}")
    assert len(scripts) >= 3
    print("✅ Marketing Agent Generation Verified!")


def test_expansion_agent():
    print_banner("4. TESTING EXPANSION AGENT (POST /expansion/generate)")
    resp = client.post("/expansion/generate")
    assert resp.status_code == 200
    pitch = resp.json()["pitch"]
    print(f"Proposed Route: {pitch['route_name']}")
    print(f"Duration: {pitch['duration_days']} Days")
    print(f"Target Margin: {pitch['target_margin_pct']}")
    print(f"Pricing: {pitch['estimated_pricing']}")
    print(f"USPs: {pitch['usp_highlights']}")
    print(f"Itinerary Days: {len(pitch['itinerary'])} days")
    print("✅ Expansion Agent Verified!")


def test_ceo_executive_briefing():
    print_banner("5. TESTING CEO AGENT DAILY EXECUTIVE BRIEFING (GET /daily-briefing)")
    resp = client.get("/daily-briefing")
    assert resp.status_code == 200
    data = resp.json()
    print(f"Briefing ID: {data['briefing_id']} for {data['briefing_date']}")
    print(f"Total Leads: {data['leads_count']} | Qualified: {data['qualified_leads_count']}")
    print(f"Scripts Count: {data['scripts_count']} | Pitches Count: {data['pitches_count']}")
    print("\n--- Daily Executive Briefing Text ---")
    print(data["formatted_text"])
    print("✅ CEO Agent Executive Briefing Verified!")


if __name__ == "__main__":
    init_db()
    test_meta_webhook_verification()
    test_sales_lead_qualification_flow()
    test_marketing_agent()
    test_expansion_agent()
    test_ceo_executive_briefing()
    print_banner("🎉 ALL TESTS & SIMULATIONS COMPLETED SUCCESSFULLY! 🎉")
