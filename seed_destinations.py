"""
Seed script to pre-populate Countries, States, and Famous Destinations
with authentic Hyderabad-outbound logistical data, INR budgets, and SEO metadata.
"""

import json
from database import SessionLocal, Country, State, Place, init_db

def seed_data():
    init_db()
    db = SessionLocal()

    print("Checking existing data...")
    if db.query(Country).count() > 0:
        print("Data already seeded! Skipping.")
        db.close()
        return

    print("Seeding Countries, States, and Destinations...")

    # 1. INDIA
    india = Country(
        name="India",
        slug="india",
        continent="Asia",
        currency_code="INR",
        currency_symbol="₹",
        inr_exchange_rate="1.0",
        visa_requirement="No visa needed (Domestic travel for Indian Citizens. Government ID required).",
        flag_emoji="🇮🇳",
        description="The spiritual homeland of ancient Sanatana Dharma, holy river sangams, and sacred Jyotirlingas. Seamless connectivity from Hyderabad via direct flights and superfast express trains.",
        hero_image="https://images.unsplash.com/photo-1561361513-2d000a50f0dc?auto=format&fit=crop&w=1200&q=80",
    )
    db.add(india)
    db.commit()
    db.refresh(india)

    # 2. NEPAL
    nepal = Country(
        name="Nepal",
        slug="nepal",
        continent="Asia",
        currency_code="NPR",
        currency_symbol="रू",
        inr_exchange_rate="0.625",  # 1 INR = 1.60 NPR (Indian rupee is widely accepted)
        visa_requirement="Visa-free entry for Indian citizens with Voter ID or Passport. Indian currency (₹100 notes) widely accepted.",
        flag_emoji="🇳🇵",
        description="The Himalayan kingdom home to sacred Pashupatinath and Muktinath (108 holy spouts). Direct flights from Hyderabad via Kathmandu.",
        hero_image="https://images.unsplash.com/photo-1544735716-392fe2489ffa?auto=format&fit=crop&w=1200&q=80",
    )
    db.add(nepal)
    db.commit()
    db.refresh(nepal)

    # STATES IN INDIA
    # -------------------------------------------------------------
    # Uttarakhand
    uttarakhand = State(
        country_id=india.id,
        name="Uttarakhand",
        slug="uttarakhand",
        capital_city="Dehradun",
        best_time_to_visit="May to June & September to October (Avoid peak monsoon landslides in July-August)",
        description="Devbhoomi (Land of Gods), home to the sacred Chardham pilgrimage (Yamunotri, Gangotri, Kedarnath, Badrinath) and the Holy Ganges.",
        hero_image="https://images.unsplash.com/photo-1626621341517-bbf3d9990a23?auto=format&fit=crop&w=1200&q=80",
    )
    db.add(uttarakhand)

    # Uttar Pradesh
    uttar_pradesh = State(
        country_id=india.id,
        name="Uttar Pradesh",
        slug="uttar-pradesh",
        capital_city="Lucknow",
        best_time_to_visit="October to March (Pleasant winter weather for temple darshans and river snanam)",
        description="Heartland of Hindu heritage featuring Mokshapuri Kashi (Varanasi), Ayodhya Ram Janmabhoomi, Prayagraj Triveni Sangam, and Naimisharanyam.",
        hero_image="https://images.unsplash.com/photo-1561361513-2d000a50f0dc?auto=format&fit=crop&w=1200&q=80",
    )
    db.add(uttar_pradesh)

    # Tamil Nadu
    tamil_nadu = State(
        country_id=india.id,
        name="Tamil Nadu",
        slug="tamil-nadu",
        capital_city="Chennai",
        best_time_to_visit="November to March & Pournami full-moon dates every month",
        description="Ancient Dravidian temple architecture featuring Agni Lingam Arunachalam, Rameswaram Jyotirlinga, Madurai Meenakshi, and Kanchipuram.",
        hero_image="https://images.unsplash.com/photo-1582510003544-4d00b7f74220?auto=format&fit=crop&w=1200&q=80",
    )
    db.add(tamil_nadu)

    # Andhra Pradesh
    andhra_pradesh = State(
        country_id=india.id,
        name="Andhra Pradesh",
        slug="andhra-pradesh",
        capital_city="Amaravati",
        best_time_to_visit="September to February",
        description="Kali Yuga Vaikuntham Tirumala Lord Venkateswara Swamy, Srisailam Mallikarjuna Jyotirlinga, and Kanaka Durga Temple Vijayawada.",
        hero_image="https://images.unsplash.com/photo-1609766857041-ed402ea8069a?auto=format&fit=crop&w=1200&q=80",
    )
    db.add(andhra_pradesh)

    # Madhya Pradesh
    madhya_pradesh = State(
        country_id=india.id,
        name="Madhya Pradesh",
        slug="madhya-pradesh",
        capital_city="Bhopal",
        best_time_to_visit="October to March",
        description="Sacred twin Jyotirlingas: Ujjain Mahakaleshwar (famous Bhasma Aarti) and Omkareshwar on Narmada River.",
        hero_image="https://images.unsplash.com/photo-1608958435020-e8a7109ba809?auto=format&fit=crop&w=1200&q=80",
    )
    db.add(madhya_pradesh)

    # Nepal - Gandaki Province
    gandaki = State(
        country_id=nepal.id,
        name="Gandaki Province",
        slug="gandaki",
        capital_city="Pokhara",
        best_time_to_visit="March to May & September to November",
        description="The gateway to the Annapurna mountain range and the sacred Muktinath Dham perched at 12,172 feet.",
        hero_image="https://images.unsplash.com/photo-1544735716-392fe2489ffa?auto=format&fit=crop&w=1200&q=80",
    )
    db.add(gandaki)

    db.commit()
    db.refresh(uttarakhand)
    db.refresh(uttar_pradesh)
    db.refresh(tamil_nadu)
    db.refresh(andhra_pradesh)
    db.refresh(madhya_pradesh)
    db.refresh(gandaki)

    # PLACES / DESTINATIONS
    # -------------------------------------------------------------
    places_data = [
        # 1. KEDARNATH
        Place(
            state_id=uttarakhand.id,
            name="Kedarnath Jyotirlinga",
            slug="kedarnath",
            category="Pilgrimage",
            history_and_importance="One of the 12 sacred Jyotirlingas of Lord Shiva and the foremost temple of the Himalayan Chardham. According to Mahabharata, the Pandavas built this shrine to seek redemption from Lord Shiva after the Kurukshetra war. The current stone temple was revived by Adi Shankaracharya in the 8th century.",
            best_season="May to June & September to October",
            nearest_airport="Jolly Grant Airport, Dehradun (DED)",
            nearest_railway="Rishikesh (RKSH) / Haridwar (HW)",
            hyderabad_flight_options="Direct flight from Rajiv Gandhi International Airport (HYD) to Dehradun (DED) via Indigo (2h 15m), followed by scenic road transfer to Guptkashi/Phata.",
            hyderabad_train_options="Secunderabad to Haridwar via Kalinga Utkal Express or Telangana Express (transfer via Delhi).",
            hyderabad_road_options="Dehradun/Rishikesh -> Devprayag -> Rudraprayag -> Guptkashi -> Sonprayag (Drive 7-8 hrs). Helicopter from Phata/Guptkashi or 16 km trek on pony/palki to Kedarnath temple.",
            estimated_budget_min_inr=28000,
            estimated_budget_max_inr=58000,
            budget_breakdown_json=json.dumps({
                "transport_flights_trains": "₹9,000 - ₹18,000",
                "helicopter_ticket": "₹9,500 - ₹11,000 (Roundtrip Phata/Guptkashi)",
                "hotel_and_camps": "₹6,000 - ₹14,000 (Ground floor guaranteed)",
                "satvik_food": "₹4,000 (Included in Jai Srimannarayana packages)"
            }),
            currency_code="INR",
            currency_symbol="₹",
            telugu_food_rating=5,
            senior_friendly=True,
            wheelchair_accessible=False,
            senior_tips="High altitude (11,755 ft). Mandatory acclimatization night at Guptkashi. Use helicopter or doli/palki. Jai Srimannarayana Tours carries portable oxygen concentrators and Telugu guides at every step.",
            meta_title="Kedarnath from Hyderabad: Best Time, Helicopter Booking, Budget & Route Guide (2026)",
            meta_description="Planning Kedarnath from Hyderabad? Complete guide with direct flights from RGIA, helicopter tickets from Guptkashi, expected INR budget, Telugu satvik food, and senior citizen elder care.",
            hero_image="https://images.unsplash.com/photo-1626621341517-bbf3d9990a23?auto=format&fit=crop&w=1200&q=80",
            highlights_json=json.dumps([
                "Sacred Jyotirlinga Sparsha Darshan",
                "Kedarnath Helicopter Booking from Phata/Sersi",
                "Adi Shankaracharya Samadhi Memorial",
                "Telugu Satvik Bhojanam by Traveling Chef",
                "Bhairavnath Temple Mountain View"
            ]),
            faq_json=json.dumps([
                {
                    "question": "What is the best way to reach Kedarnath from Hyderabad for senior citizens?",
                    "answer": "Take a direct morning flight from Hyderabad (HYD) to Dehradun (DED), AC coach to Phata/Guptkashi, and a pre-booked helicopter to Kedarnath Helipad (8 minutes flight). Avoid the 16 km walking trek."
                },
                {
                    "question": "How much does a 5-day Kedarnath trip cost from Hyderabad?",
                    "answer": "Standard packages range from ₹28,000 (via AC train) to ₹48,000 - ₹58,000 (via direct flight + helicopter roundtrip and 3-star ground-floor hotels)."
                }
            ])
        ),

        # 2. BADRINATH
        Place(
            state_id=uttarakhand.id,
            name="Badrinath Temple",
            slug="badrinath",
            category="Pilgrimage",
            history_and_importance="The supreme seat of Lord Badri Vishal (Lord Vishnu) in the Garhwal Himalayas along the Alaknanda River. One of the 108 Divya Desams and the core of the Char Dham. Known for the natural hot sulphur spring 'Tapt Kund' and the sacred Mana Village (the last Indian village near Tibet border).",
            best_season="May to June & September to October",
            nearest_airport="Jolly Grant Airport, Dehradun (DED)",
            nearest_railway="Rishikesh (RKSH)",
            hyderabad_flight_options="Direct flight from Hyderabad (HYD) to Dehradun (DED), followed by scenic mountain coach drive through Joshimath to Badrinath.",
            hyderabad_train_options="Secunderabad to Haridwar / Rishikesh by AC Express.",
            hyderabad_road_options="Haridwar -> Rishikesh -> Srinagar -> Joshimath -> Badrinath (100% motorable road up to temple gate).",
            estimated_budget_min_inr=24000,
            estimated_budget_max_inr=48000,
            budget_breakdown_json=json.dumps({
                "transport_flights_trains": "₹8,000 - ₹16,000",
                "ac_coach_transfers": "₹7,000 - ₹12,000",
                "hotel_rooms": "₹6,000 - ₹12,000",
                "food_and_temple_pass": "₹3,500"
            }),
            currency_code="INR",
            currency_symbol="₹",
            telugu_food_rating=5,
            senior_friendly=True,
            wheelchair_accessible=True,
            senior_tips="Unlike Kedarnath, Badrinath is completely motorable by bus/car right to the temple entrance with wheelchair ramp access. Very comfortable for senior parents.",
            meta_title="Badrinath Yatra from Hyderabad: Travel Plan, Budget in INR, Best Season & Temple Guide",
            meta_description="Complete guide to visit Badrinath from Hyderabad. Motorable routes, flight connectivity, Mana village, expected INR costs, and Telugu food arrangements for families.",
            hero_image="https://images.unsplash.com/photo-1598440947619-2c35fc9aa908?auto=format&fit=crop&w=1200&q=80",
            highlights_json=json.dumps([
                "Lord Badri Vishal Maha Abhishekam Darshan",
                "Tapt Kund Sacred Hot Spring",
                "Mana Village - Vyas Gufa & Saraswati River Origin",
                "Brahma Kapal Pinda Pradanam with Telugu Purohits",
                "Direct motorable access for elders"
            ]),
            faq_json=json.dumps([
                {
                    "question": "Is trekking required to reach Badrinath?",
                    "answer": "No trekking is required. Luxury coaches from Hyderabad tour packages drop pilgrims directly at the Badrinath temple gate with wheelchair ramp access."
                }
            ])
        ),

        # 3. KASHI (VARANASI)
        Place(
            state_id=uttar_pradesh.id,
            name="Kashi Vishwanath (Varanasi)",
            slug="kashi-varanasi",
            category="Pilgrimage",
            history_and_importance="The oldest living spiritual city on earth. Lord Shiva's eternal abode where bathing in the holy Ganges grants salvation (Moksha). The recently expanded Kashi Vishwanath Dham corridor connects the river directly to the golden sanctum. Famous for Ganga Aarti at Dashashwamedh Ghat and Sankat Mochan temple.",
            best_season="October to March (Pleasant winter weather)",
            nearest_airport="Lal Bahadur Shastri Airport, Varanasi (VNS)",
            nearest_railway="Varanasi Junction (BSB) / Pt. Deen Dayal Upadhyaya (DDU)",
            hyderabad_flight_options="Direct daily Indigo flights from Rajiv Gandhi International Airport (HYD) to Varanasi (VNS) (2 hours 10 mins).",
            hyderabad_train_options="Secunderabad Danapur Express (12791) or Secunderabad-Varanasi Special Train.",
            hyderabad_road_options="Private AC coach transfers between Varanasi, Prayagraj Sangam, and Ayodhya (all within 2.5 - 3 hours drive on 4-lane expressways).",
            estimated_budget_min_inr=16500,
            estimated_budget_max_inr=34000,
            budget_breakdown_json=json.dumps({
                "flights_or_train": "₹6,000 - ₹14,000",
                "hotel_cantt_ac": "₹5,000 - ₹10,000 (3 nights)",
                "private_boat_aarti": "₹1,500",
                "satvik_food_telugu": "₹3,000"
            }),
            currency_code="INR",
            currency_symbol="₹",
            telugu_food_rating=5,
            senior_friendly=True,
            wheelchair_accessible=True,
            senior_tips="Kashi Vishwanath Corridor now has battery carts, escalators, and wheelchair ramps. Pre-book Sugam VIP Sparsha Darshan to bypass all general lines.",
            meta_title="Kashi Yatra from Hyderabad: Flights, Train Timings, Budget & VIP Darshan Guide (2026)",
            meta_description="Plan your Kashi Varanasi pilgrimage from Hyderabad. Direct flights from RGIA, Sugam VIP darshan pass, Ganga Aarti private boats, Telugu satvik bhojanam, and full budget in INR.",
            hero_image="https://images.unsplash.com/photo-1561361513-2d000a50f0dc?auto=format&fit=crop&w=1200&q=80",
            highlights_json=json.dumps([
                "Kashi Vishwanath Jyotirlinga Sparsha Darshan",
                "Evening Ganga Aarti on Private Motorboat",
                "Kalabhairava Swamy & Annapurna Devi Darshan",
                "Manikarnika & Harishchandra Sacred Ghats",
                "100% Telugu Satvik Catering"
            ]),
            faq_json=json.dumps([
                {
                    "question": "Can senior citizens with walking difficulty visit Kashi Vishwanath?",
                    "answer": "Yes. With the new Kashi Corridor, battery carts are available from the gate directly to the sanctum. Jai Srimannarayana Tours provides wheelchairs and dedicated escorts."
                }
            ])
        ),

        # 4. AYODHYA
        Place(
            state_id=uttar_pradesh.id,
            name="Ayodhya Ram Janmabhoomi",
            slug="ayodhya",
            category="Pilgrimage",
            history_and_importance="The sacred birthplace of Maryada Purushottam Lord Sri Rama on the banks of holy Sarayu River. Home to the monumental pink sandstone Ram Janmabhoomi Mandir inaugurated in 2024, Hanuman Garhi, and Kanak Bhavan.",
            best_season="October to March",
            nearest_airport="Maharishi Valmiki International Airport, Ayodhya (AYJ)",
            nearest_railway="Ayodhya Dham Junction (AY)",
            hyderabad_flight_options="Direct flight from Hyderabad (HYD) to Ayodhya (AYJ) or via Lucknow (LKO) with 2-hour expressway drive.",
            hyderabad_train_options="Secunderabad to Ayodhya via weekly express or via Varanasi connection.",
            hyderabad_road_options="Smooth 4-lane highway connecting Varanasi -> Ayodhya (195 km, 3.5 hrs).",
            estimated_budget_min_inr=14000,
            estimated_budget_max_inr=28000,
            budget_breakdown_json=json.dumps({
                "transport_from_hyderabad": "₹5,000 - ₹12,000",
                "ac_hotel_stay": "₹4,000 - ₹8,000",
                "local_transfers": "₹2,000",
                "food_and_prasad": "₹2,500"
            }),
            currency_code="INR",
            currency_symbol="₹",
            telugu_food_rating=5,
            senior_friendly=True,
            wheelchair_accessible=True,
            senior_tips="Battery-operated golf carts are available for senior pilgrims inside the temple complex. Free wheelchair counters are located near Sugriva Qila entrance.",
            meta_title="Ayodhya Ram Mandir from Hyderabad: Flights, Budget in INR, VIP Darshan & Best Season",
            meta_description="How to visit Ayodhya Ram Mandir from Hyderabad. Direct flights to AYJ, expected INR budget, Hanuman Garhi, Sarayu Aarti, and Telugu tour assistance.",
            hero_image="https://images.unsplash.com/photo-1544735716-392fe2489ffa?auto=format&fit=crop&w=1200&q=80",
            highlights_json=json.dumps([
                "Grand Ram Lalla Darshan in Garbhagriha",
                "Hanuman Garhi 76-Step Temple",
                "Kanak Bhavan - Palace of Sita Rama",
                "Evening Sarayu River Aarti & Deepotsav Ghats",
                "Comfortable golf cart escorts for elders"
            ]),
            faq_json=json.dumps([
                {
                    "question": "Is Ayodhya connected directly to Hyderabad by flight?",
                    "answer": "Yes, direct flights operate from Rajiv Gandhi International Airport (HYD) to Maharishi Valmiki International Airport in Ayodhya (AYJ)."
                }
            ])
        ),

        # 5. ARUNACHALAM
        Place(
            state_id=tamil_nadu.id,
            name="Arunachalam (Tiruvannamalai)",
            slug="arunachalam-tiruvannamalai",
            category="Pilgrimage",
            history_and_importance="The supreme Agni Kshetra (Fire Element) among the Pancha Bhoota Sthalas. The holy Arunachala Hill itself is worshipped as Lord Shiva. Millions of devotees undertake the sacred 14 km Giri Pradakshina, especially on monthly Pournami (Full Moon) nights. Also home to Sri Ramana Maharshi Ashram.",
            best_season="October to March and monthly Pournami (Full Moon) dates",
            nearest_airport="Chennai International Airport (MAA) / Bengaluru (BLR)",
            nearest_railway="Katpadi Junction (KPD) / Tiruvannamalai (TNM)",
            hyderabad_flight_options="Flight from Hyderabad (HYD) to Chennai or Bengaluru, followed by AC coach to Tiruvannamalai (3.5 hrs).",
            hyderabad_train_options="Direct overnight AC sleeper trains from Secunderabad/Kacheguda to Katpadi Junction (KPD), followed by a 1.5-hour AC bus drive.",
            hyderabad_road_options="Overnight luxury multi-axle AC sleeper bus directly from Hyderabad (KPHB / Lakdikapul) to Tiruvannamalai.",
            estimated_budget_min_inr=11500,
            estimated_budget_max_inr=19000,
            budget_breakdown_json=json.dumps({
                "transport_sc_to_katpadi": "₹2,500 - ₹5,000",
                "ac_hotel_4star_vellore": "₹4,000 - ₹7,000",
                "battery_cart_giri_pradakshina": "₹1,500",
                "telugu_satvik_meals": "₹2,500"
            }),
            currency_code="INR",
            currency_symbol="₹",
            telugu_food_rating=5,
            senior_friendly=True,
            wheelchair_accessible=True,
            senior_tips="For elderly pilgrims who cannot walk 14 km, battery-operated carts and dedicated AC cars are arranged for Giri Pradakshina stopping at all Ashta Lingams.",
            meta_title="Arunachalam Giri Pradakshina from Hyderabad: Pournami Dates, Budget, Train & Route Guide",
            meta_description="Planning Arunachalam Pournami Giri Pradakshina from Hyderabad? Complete guide on trains to Katpadi, budget in INR, Vellore Golden temple combo, and battery cart options for elders.",
            hero_image="https://images.unsplash.com/photo-1582510003544-4d00b7f74220?auto=format&fit=crop&w=1200&q=80",
            highlights_json=json.dumps([
                "Arunachaleswara Swamy Lingodbhava Darshan",
                "14 km Pournami Giri Pradakshina with Ashta Lingams",
                "Ramana Maharshi Ashram & Virupaksha Cave",
                "Vellore Sripuram Golden Temple Combo",
                "Battery car options for senior citizens"
            ]),
            faq_json=json.dumps([
                {
                    "question": "Can elderly parents complete Arunachalam Giri Pradakshina?",
                    "answer": "Yes. While walking is traditional, authorized battery-operated vehicles and AC cars are allowed to perform the 14 km pradakshina for senior citizens with darshan at all 8 lingams."
                }
            ])
        ),

        # 6. MUKTINATH (NEPAL)
        Place(
            state_id=gandaki.id,
            name="Muktinath Temple (Nepal)",
            slug="muktinath-nepal",
            category="Pilgrimage",
            history_and_importance="The sacred Divya Desam temple situated at 12,172 feet in the Mustang district of Nepal. Revering Lord Sri Vishnu as Muktinath (Lord of Liberation). Revered by Hindus and Buddhists alike. Famous for 108 holy water spouts (Mukti Dhara) from ice-cold mountain springs and sacred Shaligram stones from Gandaki river.",
            best_season="March to May & September to November (Clear skies and mild temperatures)",
            nearest_airport="Pokhara Airport (PKR) / Jomsom Airport (JMO)",
            nearest_railway="Gorakhpur Junction (GKP) across Indian border",
            hyderabad_flight_options="Direct flight from Hyderabad (HYD) to Kathmandu (KTM), connecting domestic flight to Pokhara and Jomsom.",
            hyderabad_train_options="Hyderabad to Gorakhpur by train, cross Indo-Nepal border at Sonauli, coach to Pokhara.",
            hyderabad_road_options="Scenic mountain flight or 4x4 Jeep ride from Pokhara -> Jomsom -> Muktinath.",
            estimated_budget_min_inr=42000,
            estimated_budget_max_inr=75000,
            budget_breakdown_json=json.dumps({
                "international_flights_hyd_ktm": "₹16,000 - ₹24,000",
                "nepal_domestic_flights": "₹12,000 - ₹18,000",
                "hotels_pokhara_jomsom": "₹8,000 - ₹16,000",
                "acims_permit_food": "₹6,000"
            }),
            currency_code="NPR",
            currency_symbol="रू",
            telugu_food_rating=4,
            senior_friendly=True,
            wheelchair_accessible=False,
            senior_tips="High mountain altitude (3,710m). Horse riding or local motorcycle escorts are arranged from the vehicle stand right up to the 108 spouts. Carry thermal wear.",
            meta_title="Muktinath Nepal Yatra from Hyderabad: Flights, 108 Spouts, Budget in INR & Visa Rules",
            meta_description="Plan your sacred Muktinath Yatra from Hyderabad. Direct flights to Kathmandu, Pokhara, Jomsom route, expected INR budget, currency conversion, and Telugu pilgrim assistance.",
            hero_image="https://images.unsplash.com/photo-1544735716-392fe2489ffa?auto=format&fit=crop&w=1200&q=80",
            highlights_json=json.dumps([
                "Holy Bath under 108 Mukti Dhara (Water Spouts)",
                "Natural Flame & Water Temple (Jwala Mai)",
                "Pashupatinath Temple Darshan in Kathmandu",
                "Sacred Shaligram stones from Kali Gandaki River",
                "Pokhara Phewa Lake Boat Ride"
            ]),
            faq_json=json.dumps([
                {
                    "question": "Do Indian citizens need a visa or passport for Nepal Muktinath?",
                    "answer": "No visa is required. Indian citizens can enter Nepal using a valid Indian Passport or an original Election Voter ID Card."
                },
                {
                    "question": "Is Indian currency accepted in Nepal?",
                    "answer": "Yes, Indian Rupee notes of ₹100 denomination are accepted everywhere across Nepal. Currency conversion is 1 INR = 1.60 NPR."
                }
            ])
        ),

        # 7. TIRUPATI BALAJI
        Place(
            state_id=andhra_pradesh.id,
            name="Tirupati Balaji (Tirumala)",
            slug="tirupati-balaji",
            category="Pilgrimage",
            history_and_importance="The most visited sacred temple on earth. Lord Sri Venkateswara Swamy (Balaji) stands atop the sacred Seven Hills of Seshachalam. Known for granting all desires in Kali Yuga, world-famous Tirupati Laddu Prasadam, and peaceful Govinda chants.",
            best_season="September to February (Pleasant weather)",
            nearest_airport="Tirupati Airport (TIR)",
            nearest_railway="Tirupati Main (TPTY) / Renigunta (RU)",
            hyderabad_flight_options="Direct daily 1-hour flights from Hyderabad (HYD) to Tirupati (TIR) via Indigo / SpiceJet.",
            hyderabad_train_options="Secunderabad to Tirupati Vande Bharat Express (20701 - 8 hrs 15 mins) or Rayalaseema Express overnight.",
            hyderabad_road_options="Hyderabad -> Kurnool -> Kadapa -> Tirupati (National Highway 44 & 40 - 550 km, 9 hrs).",
            estimated_budget_min_inr=6500,
            estimated_budget_max_inr=16000,
            budget_breakdown_json=json.dumps({
                "transport_vande_bharat_flight": "₹2,500 - ₹7,000",
                "hotel_tirupati_ac": "₹2,000 - ₹5,000",
                "special_darshan_pass": "₹300 - ₹500",
                "food_and_prasadam": "₹1,500"
            }),
            currency_code="INR",
            currency_symbol="₹",
            telugu_food_rating=5,
            senior_friendly=True,
            wheelchair_accessible=True,
            senior_tips="TTD offers dedicated Senior Citizen / Physically Challenged Special Darshan queue at 10:00 AM and 3:00 PM with zero waiting time. Carry original Aadhaar card.",
            meta_title="Tirupati from Hyderabad: Vande Bharat Timings, VIP Darshan, Budget in INR & Senior Passes",
            meta_description="Complete guide from Hyderabad to Tirupati Balaji. Vande Bharat train schedule, flights from RGIA, TTD senior citizen quota, expected budget, and package details.",
            hero_image="https://images.unsplash.com/photo-1609766857041-ed402ea8069a?auto=format&fit=crop&w=1200&q=80",
            highlights_json=json.dumps([
                "Tirumala Lord Venkateswara VIP Darshan",
                "World Famous Tirupati Laddu Prasadam",
                "Padmavathi Ammavari Temple (Tiruchanur)",
                "Kapila Theertham & Sri Kalahasti Combo",
                "Special dedicated Senior Citizen Queue"
            ]),
            faq_json=json.dumps([
                {
                    "question": "What is the fastest way to visit Tirupati from Hyderabad?",
                    "answer": "Take the morning Vande Bharat Express from Secunderabad (departs 6:00 AM, reaches Tirupati 2:15 PM) or the direct 1-hour morning flight from RGIA."
                }
            ])
        ),

        # 8. UJJAIN MAHAKALESHWAR
        Place(
            state_id=madhya_pradesh.id,
            name="Ujjain Mahakaleshwar",
            slug="ujjain-mahakaleshwar",
            category="Pilgrimage",
            history_and_importance="The only south-facing (Dakshinamurti) Jyotirlinga among the twelve. Revered as the Master of Time and Death (Mahakal). World-renowned for the sacred dawn Bhasma Aarti (worship with holy ash). Also features the expansive Mahakal Lok Corridor and Ram Ghat on the Shipra River.",
            best_season="October to March",
            nearest_airport="Devi Ahilyabai Holkar Airport, Indore (IDR)",
            nearest_railway="Ujjain Junction (UJN)",
            hyderabad_flight_options="Direct flight from Hyderabad (HYD) to Indore (IDR) (1 hour 25 mins), followed by a smooth 45-minute expressway drive to Ujjain.",
            hyderabad_train_options="Direct train from Secunderabad to Ujjain via Hyderabad-Jaipur Special or Indore Express.",
            hyderabad_road_options="Indore Airport to Ujjain 4-lane highway (55 km).",
            estimated_budget_min_inr=14500,
            estimated_budget_max_inr=26000,
            budget_breakdown_json=json.dumps({
                "flights_hyd_to_indore": "₹5,500 - ₹11,000",
                "ac_hotel_ujjain": "₹4,000 - ₹7,000",
                "bhasma_aarti_vip": "₹1,500",
                "satvik_meals_and_cabs": "₹3,500"
            }),
            currency_code="INR",
            currency_symbol="₹",
            telugu_food_rating=4,
            senior_friendly=True,
            wheelchair_accessible=True,
            senior_tips="Pre-register for Bhasma Aarti online or through tour operators to ensure entry into the sanctum sanctorum. Wheelchair accessibility available in Mahakal Lok corridor.",
            meta_title="Ujjain Mahakal from Hyderabad: Flight to Indore, Bhasma Aarti Booking, Budget in INR (2026)",
            meta_description="How to visit Ujjain Mahakaleshwar Jyotirlinga from Hyderabad. Indore direct flights, Bhasma Aarti pass rules, Omkareshwar combo, expected budget, and family travel tips.",
            hero_image="https://images.unsplash.com/photo-1608958435020-e8a7109ba809?auto=format&fit=crop&w=1200&q=80",
            highlights_json=json.dumps([
                "Sacred Morning Bhasma Aarti Darshan",
                "Grand Mahakal Lok Corridor Walk",
                "Kal Bhairav Liquor Offering Shrine",
                "Harsiddhi Mata Shakti Peeth",
                "Omkareshwar Island Jyotirlinga Combo"
            ]),
            faq_json=json.dumps([
                {
                    "question": "Can Ujjain and Omkareshwar be covered in a weekend from Hyderabad?",
                    "answer": "Yes. Take a Friday evening flight from Hyderabad to Indore, attend Saturday morning Bhasma Aarti in Ujjain, visit Omkareshwar on Sunday, and fly back to Hyderabad Sunday night."
                }
            ])
        )
    ]

    for p in places_data:
        db.add(p)

    db.commit()
    print(f"Successfully seeded {len(places_data)} destinations across {db.query(State).count()} states and {db.query(Country).count()} countries!")
    db.close()

if __name__ == "__main__":
    seed_data()
