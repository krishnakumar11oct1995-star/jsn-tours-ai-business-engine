"""
Universal Multi-Agent Test Suite with Adversarial Critic Loop.
Tests:
1. Scenario A: "We want to launch a VIP 3-day helicopter Chardham package from Hyderabad at ₹1,25,000 per person."
2. Scenario B: "A pilgrim from Secunderabad is demanding a full refund because their mother developed altitude sickness in Badrinath."
3. Scenario C: "Can we expand to weekly Arunachalam Pournami tours with 5 luxury AC sleeper buses departing from Hyderabad simultaneously?"
4. FastAPI HTTP Endpoint Test: POST /agent-team/execute & POST /ask
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
from database import init_db
from agents import TeamOrchestrator
from main import app

client = TestClient(app)


def print_separator(title: str):
    print("\n" + "=" * 80)
    print(f"🔱  {title}")
    print("=" * 80)


def test_scenario(query: str, test_number: int):
    print_separator(f"TEST {test_number}: {query}")

    # 1. Run through TeamOrchestrator
    result = TeamOrchestrator.process_universal_request(user_query=query)

    print("\n--- PHASE 1: UNIVERSAL WORK ASSIGNMENT ---")
    print(f"• Sales Agent Strategy: {result.phase_1_proposals['sales']['core_strategy'][:120]}...")
    print(f"• Marketing Agent Strategy: {result.phase_1_proposals['marketing']['core_strategy'][:120]}...")
    print(f"• Operations Agent Strategy: {result.phase_1_proposals['operations']['core_strategy'][:120]}...")

    print("\n--- PHASE 2: ADVERSARIAL CRITIC ATTACK (WHAT GOES WRONG) ---")
    critic = result.phase_2_critic_attack
    print(f"⚠️  Critic Brutal Verdict: {critic['brutal_verdict'][:140]}...")
    for idx, flaw in enumerate(critic["flaws_and_vulnerabilities"][:3], 1):
        print(f"   [{idx}] {flaw['category']} ({flaw['severity']}): {flaw['what_goes_wrong'][:100]}...")

    print("\n--- PHASE 3: SELF-HEALING FIXES & COUNTERMEASURES ---")
    fixes = result.phase_3_mitigation_fixes
    print("🛡️ Sales Fixes:")
    for f in fixes["sales_fixes"]["concrete_fixes_applied"][:2]:
        print(f"   ✅ {f}")
    print("🛡️ Marketing Fixes:")
    for f in fixes["marketing_fixes"]["concrete_fixes_applied"][:2]:
        print(f"   ✅ {f}")
    print("🛡️ Operations Fixes:")
    for f in fixes["operations_fixes"]["concrete_fixes_applied"][:2]:
        print(f"   ✅ {f}")

    print("\n--- PHASE 4: CEO EXECUTIVE VERDICT ---")
    ceo = result.phase_4_ceo_verdict
    print(f"👑 Decision: {ceo.get('decision')}")
    print(f"🎯 Directives for Ramesh (9030780132):")
    for d in ceo.get("approved_directives_for_ramesh", []):
        print(f"   👉 {d}")

    assert result.phase_1_proposals["sales"]["core_strategy"]
    assert result.phase_1_proposals["marketing"]["core_strategy"]
    assert result.phase_1_proposals["operations"]["core_strategy"]
    assert len(critic["flaws_and_vulnerabilities"]) > 0
    assert len(fixes["sales_fixes"]["concrete_fixes_applied"]) > 0
    assert len(fixes["marketing_fixes"]["concrete_fixes_applied"]) > 0
    assert len(fixes["operations_fixes"]["concrete_fixes_applied"]) > 0
    assert ceo.get("decision")
    print(f"\n✅ Test {test_number} Passed Successfully!")


def test_api_endpoint():
    print_separator("TEST 4: FASTAPI HTTP ENDPOINT (POST /agent-team/execute & POST /ask)")
    query = "How do we scale Chardham 2026 bookings from YouTube Shorts without getting banned by WhatsApp?"

    # Test /agent-team/execute
    resp1 = client.post("/agent-team/execute", json={"query": query})
    assert resp1.status_code == 200
    data1 = resp1.json()
    assert "phase_1_proposals" in data1
    assert "phase_2_critic_attack" in data1
    assert "phase_3_mitigation_fixes" in data1
    assert "phase_4_ceo_verdict" in data1
    print("✅ POST /agent-team/execute responded with full 4-phase payload!")

    # Test /ask alias
    resp2 = client.post("/ask", json={"query": query})
    assert resp2.status_code == 200
    print("✅ POST /ask alias endpoint responded 200 OK!")


if __name__ == "__main__":
    init_db()
    test_scenario(
        "We want to launch a VIP 3-day helicopter Chardham package from Hyderabad at ₹1,25,000 per person.",
        1,
    )
    test_scenario(
        "A pilgrim from Secunderabad is demanding a full refund because their mother developed altitude sickness in Badrinath.",
        2,
    )
    test_scenario(
        "Can we expand to weekly Arunachalam Pournami tours with 5 luxury AC sleeper buses departing from Hyderabad simultaneously?",
        3,
    )
    test_api_endpoint()
    print_separator("🎉 ALL UNIVERSAL AGENT + CRITIC TESTS PASSED! 🎉")
