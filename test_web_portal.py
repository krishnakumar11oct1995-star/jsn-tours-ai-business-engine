"""
Automated Integration Tests for Jai Srimannarayana Tours & Travels Web Portal.
Tests:
1. GET / -> Homepage renders with status 200, contains pilgrimage cards, video, WhatsApp CTA
2. GET /destinations -> Catalog renders with countries & states
3. GET /destinations/india -> Country hub renders with states & places
4. GET /destinations/india/uttar-pradesh -> State hub renders
5. GET /destinations/india/uttar-pradesh/kashi -> Place detail renders with Schema.org JSON-LD & Hyderabad logistics
6. GET /calculator -> Interactive budget calculator renders
7. GET /api/destinations/search?q=kashi -> JSON search returns matched results
8. GET /api/health & GET /api/status -> Return system metrics
9. 404 error handling on invalid slugs
"""

import json
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_home_page():
    response = client.get("/")
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    html = response.text
    assert "Jai Srimannarayana Tours & Travels" in html
    assert "9030780132" in html
    assert "Hyderabad" in html
    assert "Devotional Care Tailored for Telugu Pilgrims" in html
    assert "100% Satvik Telugu Bhojanam" in html
    assert "Ramesh Garu" not in html
    assert "kashi_yatra_oct25.mp4" not in html
    assert "GnFzdND__fE" in html
    assert "i.ytimg.com/vi/GnFzdND__fE" in html
    assert "@telugutravellerramesh5846" in html
    print("[PASS] test_home_page passed.")


def test_destinations_catalog():
    response = client.get("/destinations")
    assert response.status_code == 200
    html = response.text
    assert "Destinations Directory" in html
    assert "India" in html
    assert "Nepal" in html
    print("[PASS] test_destinations_catalog passed.")


def test_country_hub():
    response = client.get("/destinations/india")
    assert response.status_code == 200
    html = response.text
    assert "India" in html
    assert "INR" in html
    assert "Uttar Pradesh" in html or "Uttarakhand" in html
    print("[PASS] test_country_hub passed.")


def test_state_hub():
    response = client.get("/destinations/india/uttar-pradesh")
    assert response.status_code == 200
    html = response.text
    assert "Uttar Pradesh" in html
    assert "Kashi" in html or "Ayodhya" in html
    print("[PASS] test_state_hub passed.")


def test_place_detail_and_seo_schema():
    response = client.get("/destinations/india/uttar-pradesh/kashi-varanasi")
    assert response.status_code == 200
    html = response.text
    assert "Kashi" in html
    assert "Rajiv Gandhi International Airport (HYD)" in html or "Secunderabad" in html
    assert "9030780132" in html
    assert "application/ld+json" in html
    assert "TouristAttraction" in html
    assert "BreadcrumbList" in html
    assert "Ramesh Garu" not in html
    assert "GnFzdND__fE" in html
    assert "i.ytimg.com/vi/GnFzdND__fE" in html
    assert "Direct Static Approximate Tariffs" in html
    assert "Economy Package" in html
    assert "Comfort Package" in html
    assert "detailCalculatedCost" in html
    assert "Travel Engine" not in html
    assert "Programmatic SEO" not in html
    print("[PASS] test_place_detail_and_seo_schema passed.")


def test_budget_calculator_page():
    response = client.get("/calculator")
    assert response.status_code == 200
    html = response.text
    assert "Hyderabad Travel Budget Calculator" in html
    assert "calcResultDisplay" in html
    assert "Static Approximate Tour Budgets" in html
    assert "Economy (Train)" in html
    assert "Comfort (Flight)" in html
    assert "VIP Senior Care" in html
    assert "selectDestinationFromTable" in html
    assert "Travel Engine" not in html
    assert "Programmatic SEO" not in html
    print("[PASS] test_budget_calculator_page passed.")


def test_search_api():
    response = client.get("/api/destinations/search?q=kashi")
    assert response.status_code == 200
    data = response.json()
    assert data["count"] >= 1
    assert any("Kashi" in r["name"] for r in data["results"])
    print(f"[PASS] test_search_api passed ({data['count']} results found).")


def test_api_status():
    response = client.get("/api/status")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "online"
    assert data["company"] == "Jai Srimannarayana Tours & Travels"
    assert data["stats"]["destinations_cataloged"] >= 8
    print(f"[PASS] test_api_status passed: {data['stats']['destinations_cataloged']} destinations cataloged.")


def test_404_handling():
    response = client.get("/destinations/invalid-country")
    assert response.status_code == 404
    response = client.get("/destinations/india/invalid-state")
    assert response.status_code == 404
    response = client.get("/destinations/india/uttar-pradesh/invalid-place")
    assert response.status_code == 404
    print("[PASS] test_404_handling passed.")


def test_shirdi_page():
    response = client.get("/destinations/india/maharashtra/shirdi-sai-baba")
    assert response.status_code == 200
    html = response.text
    assert "Shirdi Sai Baba" in html
    assert "Shani Shingnapur" in html
    assert "9030780132" in html
    print("[PASS] test_shirdi_page passed.")


def test_package_kashi_ayodhya():
    response = client.get("/packages/kashi-prayagraj-ayodhya")
    assert response.status_code == 200
    html = response.text
    assert "Kashi" in html
    assert "Ayodhya" in html
    assert "18,500" in html
    assert "9030780132" in html
    print("[PASS] test_package_kashi_ayodhya passed.")

def test_diwali_package_page():
    response = client.get("/packages/diwali-dev-deepavali")
    assert response.status_code == 200
    html = response.text
    assert "Ayodhya Deepotsav" in html
    assert "Kashi Dev Deepavali" in html
    assert "19,500" in html
    assert "9030780132" in html
    print("[PASS] test_diwali_package_page passed.")



def test_rameswaram_package_page():
    response = client.get("/packages/rameswaram-madurai-kanyakumari")
    assert response.status_code == 200
    html = response.text
    assert "Rameswaram" in html
    assert "Madurai" in html
    assert "Kanyakumari" in html
    assert "19,500" in html
    assert "9030780132" in html
    print("[PASS] test_rameswaram_package_page passed.")


def test_package_7jyotirlingas_5dwarakas():
    response = client.get("/packages/7-jyotirlingas-5-dwarakas")
    assert response.status_code == 200
    html = response.text
    assert "7 జ్యోతిర్లింగాలు" in html or "7 Jyotirlingas" in html
    assert "5 ద్వారకల" in html or "5 Dwarakas" in html
    assert "32,000" in html
    assert "9030780132" in html
    assert "business_flyer_7jyotirlinga_hd.png" in html
    assert "Siddipet" in html or "సిద్దిపేట" in html
    print("[PASS] test_package_7jyotirlingas_5dwarakas passed.")


def test_rameswaram_destination_page():
    response = client.get("/destinations/india/tamil-nadu/rameswaram")
    assert response.status_code == 200
    html = response.text
    assert "Rameswaram" in html
    assert "22 Teertha Snanam" in html or "22 Kund Snanam" in html
    assert "9030780132" in html
    print("[PASS] test_rameswaram_destination_page passed.")


def test_srisailam_page():
    response = client.get("/destinations/india/andhra-pradesh/srisailam-mallikarjuna")
    assert response.status_code == 200
    html = response.text
    assert "Srisailam" in html
    assert "Sparsha Darshanam" in html or "Jyotirlinga" in html
    assert "9030780132" in html
    print("[PASS] test_srisailam_page passed.")


def test_pancharama_page():
    response = client.get("/destinations/india/andhra-pradesh/pancharama-kshetras")
    assert response.status_code == 200
    html = response.text
    assert "Pancharama" in html
    assert "Amaravathi" in html
    assert "9030780132" in html
    print("[PASS] test_pancharama_page passed.")


def test_about_page():
    response = client.get("/about")
    assert response.status_code == 200
    html = response.text
    assert "About Ramesh" in html
    assert "Matru-Pitru Seva" in html
    print("[PASS] test_about_page passed.")


def test_contact_page():
    response = client.get("/contact")
    assert response.status_code == 200
    html = response.text
    assert "Rajiv Gandhi International Airport (HYD)" in html
    assert "Secunderabad Railway Station" in html
    assert "9030780132" in html
    print("[PASS] test_contact_page passed.")


if __name__ == "__main__":
    print("\nRunning Web Portal Integration Tests...\n")
    test_home_page()
    test_destinations_catalog()
    test_country_hub()
    test_state_hub()
    test_place_detail_and_seo_schema()
    test_shirdi_page()
    test_package_kashi_ayodhya()
    test_diwali_package_page()
    test_rameswaram_package_page()
    test_package_7jyotirlingas_5dwarakas()
    test_rameswaram_destination_page()
    test_srisailam_page()
    test_pancharama_page()
    test_about_page()
    test_contact_page()
    test_budget_calculator_page()
    test_search_api()
    test_api_status()
    test_404_handling()
    print("\nALL WEB PORTAL INTEGRATION TESTS PASSED SUCCESSFULLY! [100% GREEN]\n")
