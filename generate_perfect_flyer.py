import os
from PIL import Image, ImageDraw, ImageFont, ImageFilter

def create_business_flyer():
    # Target resolution: 1200 x 2150 (HD Flyer)
    W, H = 1200, 2150
    flyer = Image.new("RGB", (W, H), color=(255, 253, 247))
    draw = ImageDraw.Draw(flyer)

    # Load Fonts
    font_path = r"C:\Windows\Fonts\Nirmala.ttc"
    font_invoc = ImageFont.truetype(font_path, 22)
    font_brand = ImageFont.truetype(font_path, 44)
    font_sub_brand = ImageFont.truetype(font_path, 26)
    font_tour_h1 = ImageFont.truetype(font_path, 48)
    font_tour_h2 = ImageFont.truetype(font_path, 30)
    font_bus_tag = ImageFont.truetype(font_path, 28)
    font_price_main = ImageFont.truetype(font_path, 38)
    font_price_sub = ImageFont.truetype(font_path, 26)
    font_sec_head = ImageFont.truetype(font_path, 28)
    font_kshetra_title = ImageFont.truetype(font_path, 23)
    font_kshetra_desc = ImageFont.truetype(font_path, 19)
    font_incl_head = ImageFont.truetype(font_path, 24)
    font_incl_body = ImageFont.truetype(font_path, 21)
    font_terms = ImageFont.truetype(font_path, 19)
    font_footer_phone = ImageFont.truetype(font_path, 44)
    font_footer_web = ImageFont.truetype(font_path, 30)

    # Color Palette
    BG_CREAM = (255, 252, 245)
    MAROON_DEEP = (130, 20, 20)
    MAROON_DARK = (100, 10, 10)
    GOLD_ACCENT = (212, 160, 23)
    GOLD_LIGHT = (250, 235, 180)
    ORANGE_TEMPLE = (217, 85, 0)
    TEXT_DARK = (30, 30, 30)
    TEXT_MUTED = (90, 80, 80)
    WHITE = (255, 255, 255)

    # 1. Outer Border / Frame
    draw.rectangle([(15, 15), (W - 15, H - 15)], outline=MAROON_DEEP, width=5)
    draw.rectangle([(25, 25), (W - 25, H - 25)], outline=GOLD_ACCENT, width=3)

    # 2. Top Header - Invocation & Brand
    # Sacred Top Strip
    draw.rectangle([(28, 28), (W - 28, 70)], fill=MAROON_DARK)
    invoc_text = "||  శ్రీరస్తు  •  శుభమస్తు  •  శ్రీ వేంకటేశ్వర ప్రసన్నః  ||"
    draw.text((W // 2, 49), invoc_text, font=font_invoc, fill=GOLD_LIGHT, anchor="mm")

    # Load original image to crop the deities banner and the bus
    orig_path = "WhatsApp Image 2026-11-11 at 9.48.42 AM.jpeg"
    if os.path.exists(orig_path):
        orig_img = Image.open(orig_path)
        # Crop top deities banner: (0, 0, 592, 110)
        deities_crop = orig_img.crop((10, 5, 582, 110))
        # Resize to fit width nicely (approx 700x125 centered)
        deities_resized = deities_crop.resize((750, 130), Image.Resampling.LANCZOS)
        flyer.paste(deities_resized, ((W - 750) // 2, 80))

    # Brand Title Box
    y_brand = 220
    draw.text((W // 2, y_brand), "జై శ్రీమన్నారాయణ టూర్స్ & ట్రావెల్స్", font=font_brand, fill=MAROON_DEEP, anchor="mm")
    draw.text((W // 2, y_brand + 40), "JAI SRIMANNARAYANA TOURS & TRAVELS  •  HYDERABAD", font=font_sub_brand, fill=ORANGE_TEMPLE, anchor="mm")

    # 3. Main Tour Banner Box
    y_tour_box = 285
    tour_box_h = 135
    draw.rectangle([(35, y_tour_box), (W - 35, y_tour_box + tour_box_h)], fill=MAROON_DEEP)
    draw.rectangle([(40, y_tour_box + 5), (W - 40, y_tour_box + tour_box_h - 5)], outline=GOLD_ACCENT, width=2)
    
    # Tour Title inside box
    draw.text((W // 2, y_tour_box + 40), "7 జ్యోతిర్లింగాలు  &  5 ద్వారకలు", font=font_tour_h1, fill=GOLD_LIGHT, anchor="mm")
    draw.text((W // 2, y_tour_box + 90), "శ్రీ క్షేత్ర పండరీపురం • కొల్హాపూర్ • షిర్డీ మహా పుణ్యక్షేత్ర దర్శన యాత్ర", font=font_tour_h2, fill=WHITE, anchor="mm")

    # 4. Bus & Travel Info Section
    y_bus_sec = 430
    if os.path.exists(orig_path):
        # Crop the bus illustration: (40, 160, 550, 390)
        bus_crop = orig_img.crop((50, 165, 545, 385))
        bus_resized = bus_crop.resize((480, 220), Image.Resampling.LANCZOS)
        flyer.paste(bus_resized, (50, y_bus_sec))

    # Right of Bus: Highlights Card
    h_card_x1 = 550
    h_card_y1 = y_bus_sec
    h_card_x2 = W - 45
    h_card_y2 = y_bus_sec + 220
    draw.rectangle([(h_card_x1, h_card_y1), (h_card_x2, h_card_y2)], fill=GOLD_LIGHT, outline=GOLD_ACCENT, width=2)

    # Text inside Highlight Card
    draw.text((h_card_x1 + 20, h_card_y1 + 25), "ప్రయాణ వివరాలు & రుసుము", font=font_sec_head, fill=MAROON_DEEP)
    draw.text((h_card_x1 + 20, h_card_y1 + 65), "📅 బయలుదేరు తేదీ: 28 నవంబర్ 2026", font=font_price_sub, fill=TEXT_DARK)
    draw.text((h_card_x1 + 20, h_card_y1 + 105), "📍 బోర్డింగ్: సిద్దిపేట & హైదరాబాద్ నుండి", font=font_price_sub, fill=TEXT_DARK)
    draw.text((h_card_x1 + 20, h_card_y1 + 145), "🚌 వాహనం: లగ్జరీ 2+1 AC స్లీపర్ కోచ్ బస్సు", font=font_price_sub, fill=TEXT_DARK)
    
    # Red Highlight for Price
    draw.rectangle([(h_card_x1 + 15, h_card_y1 + 175), (h_card_x2 - 15, h_card_y2 - 10)], fill=MAROON_DEEP)
    draw.text(((h_card_x1 + h_card_x2) // 2, h_card_y1 + 195), "ప్యాకేజీ ధర: ఒక్కరికి ₹32,000/- మాత్రమే", font=font_price_sub, fill=GOLD_LIGHT, anchor="mm")

    # 5. The 20 Sacred Kshetras (Corrected Telugu Spellings, 2 Beautiful Columns)
    y_kshetra_sec = 665
    draw.rectangle([(35, y_kshetra_sec), (W - 35, y_kshetra_sec + 50)], fill=MAROON_DEEP)
    draw.text((W // 2, y_kshetra_sec + 25), "దర్శనీయ 20 దివ్య పుణ్యక్షేత్రాల వివరాలు (పూర్తి దర్శన మార్గం)", font=font_sec_head, fill=GOLD_LIGHT, anchor="mm")

    # 2 Columns for 20 Places
    col1_x = 50
    col2_x = 615
    col_w = 535
    row_h = 44
    y_start_places = y_kshetra_sec + 65

    col1_places = [
        ("1", "తుల్జాపూర్", "శ్రీ భవానీ మాత దర్శనం (శక్తిపీఠం)"),
        ("2", "కొల్హాపూర్", "శ్రీ మహాలక్ష్మి అమ్మవారి దివ్య దర్శనం"),
        ("3", "పండరీపురం", "శ్రీ విఠల్ రుక్మిణి మందిరం, చంద్రభాగా స్నానం"),
        ("4", "ఘృశ్నేశ్వర్", "12వ జ్యోతిర్లింగం & ఎల్లోరా కైలాస మందిరం"),
        ("5", "త్రయంబకేశ్వరం", "నాసిక్ వద్ద గోదావరి ఉద్భవ పవిత్ర జ్యోతిర్లింగం"),
        ("6", "భీమాశంకరం", "పూణే వద్ద పవిత్ర భీమాశంకర్ జ్యోతిర్లింగం"),
        ("7", "ఎల్లోరా గుహలు", "చారిత్రక గుహాలయాలు & కైలాస క్షేత్రం"),
        ("8", "సోమనాథ్", "ప్రథమ ద్వాదశ జ్యోతిర్లింగం, సౌరాష్ట్ర గుజరాత్"),
        ("9", "నాగేశ్వర్", "దారుకావనం పవిత్ర నాగేశ్వర జ్యోతిర్లింగం"),
        ("10", "ద్వారకాధీశ మందిరం", "గోమతి ద్వారక, మోక్షపురి దర్శనం")
    ]

    col2_places = [
        ("11", "బేట్ ద్వారక", "సముద్రంలో శ్రీకృష్ణ భగవానుని అంతఃపురం"),
        ("12", "కాంక్రోలి ద్వారక", "రాజస్థాన్ ద్వారకాధీశ దివ్య మందిరం"),
        ("13", "శ్రీనాథ్ ద్వారక", "నాథద్వారా శ్రీనాథ్‌జీ దర్శనం"),
        ("14", "డాకోర్ ద్వారక", "శ్రీ రణఛోడ్‌రాయ్‌జీ దివ్య మందిరం"),
        ("15", "రాంబోడ", "ప్రసిద్ధ శ్రీ రాంబోడ హనుమాన్ మందిరం"),
        ("16", "నిష్కళంక్ మహాదేవ్", "సముద్ర తీరంలో కొలియాక్ స్వయంభూ శివలింగం"),
        ("17", "షిర్డీ", "శ్రీ సాయిబాబా పవిత్ర సమాధి మందిర దర్శనం"),
        ("18", "ఉజ్జయిని మహాకాళేశ్వర్", "ప్రసిద్ధ జ్యోతిర్లింగం & క్షిప్రా నదీ తీరం"),
        ("19", "ఓంకారేశ్వర్", "నర్మదా నదీ ద్వీప పవిత్ర జ్యోతిర్లింగం"),
        ("20", "పర్లి వైదినాథ్", "వైద్యనాథ జ్యోతిర్లింగ క్షేత్రం, మహారాష్ట్ర")
    ]

    # Render Column 1
    for i, (num, name, desc) in enumerate(col1_places):
        curr_y = y_start_places + (i * row_h)
        # Background stripe
        bg_col = (255, 248, 235) if i % 2 == 0 else WHITE
        draw.rectangle([(col1_x, curr_y), (col1_x + col_w, curr_y + row_h - 4)], fill=bg_col, outline=(235, 215, 180), width=1)
        # Number badge
        draw.rectangle([(col1_x + 4, curr_y + 4), (col1_x + 36, curr_y + row_h - 8)], fill=ORANGE_TEMPLE)
        draw.text((col1_x + 20, curr_y + row_h // 2 - 2), num, font=font_kshetra_title, fill=WHITE, anchor="mm")
        # Place Name & Desc
        draw.text((col1_x + 45, curr_y + row_h // 2 - 2), f"{name} - {desc}", font=font_kshetra_title, fill=TEXT_DARK, anchor="lm")

    # Render Column 2
    for i, (num, name, desc) in enumerate(col2_places):
        curr_y = y_start_places + (i * row_h)
        bg_col = (255, 248, 235) if i % 2 == 0 else WHITE
        draw.rectangle([(col2_x, curr_y), (col2_x + col_w, curr_y + row_h - 4)], fill=bg_col, outline=(235, 215, 180), width=1)
        draw.rectangle([(col2_x + 4, curr_y + 4), (col2_x + 36, curr_y + row_h - 8)], fill=ORANGE_TEMPLE)
        draw.text((col2_x + 20, curr_y + row_h // 2 - 2), num, font=font_kshetra_title, fill=WHITE, anchor="mm")
        draw.text((col2_x + 45, curr_y + row_h // 2 - 2), f"{name} - {desc}", font=font_kshetra_title, fill=TEXT_DARK, anchor="lm")

    # 6. Inclusions & Facilities Card (సౌకర్యాలు)
    y_incl_sec = y_start_places + (10 * row_h) + 15
    draw.rectangle([(35, y_incl_sec), (W - 35, y_incl_sec + 270)], fill=WHITE, outline=GOLD_ACCENT, width=2)
    
    # Header of Inclusions
    draw.rectangle([(37, y_incl_sec + 2), (W - 37, y_incl_sec + 45)], fill=GOLD_LIGHT)
    draw.text((W // 2, y_incl_sec + 23), "⭐ ప్యాకేజీలో కల్పించబడు ప్రత్యేక సౌకర్యాలు & సేవా విశేషాలు ⭐", font=font_sec_head, fill=MAROON_DEEP, anchor="mm")

    # 4 Pillars Grid inside Inclusions
    inc_items = [
        ("🍲 100% సాత్విక భోజనం:", "మా తెలుగు వంట మనుషులతో ఉదయం టీ, వేడి టిఫిన్, మధ్యాహ్నం సంపూర్ణ భోజనం, రాత్రి చపాతీ లేదా భోజనం."),
        ("🏨 పరిశుభ్రమైన వసతి:", "డీలక్స్ AC హోటల్ రూమ్స్ (నలుగురు యాత్రికులకు కలిపి ఒక విశాలమైన అటాచ్డ్ బాత్‌రూమ్ గది)."),
        ("💧 స్వచ్ఛమైన తాగునీరు:", "ప్రతి రోజూ ప్రతి ఒక్క యాత్రికునికి 1 లీటర్ స్వచ్ఛమైన మినరల్ వాటర్ బాటిల్ అందించబడును."),
        ("🧓 మాతృ-పితృ సేవ:", "వృద్ధులకు ప్రత్యేక శ్రద్ధ, కుటుంబ సభ్యుల వంటి సహాయ సహకారాలు, ప్రశాంతమైన దర్శన సమయాలు.")
    ]

    for idx, (title, desc) in enumerate(inc_items):
        item_y = y_incl_sec + 55 + (idx * 50)
        draw.text((55, item_y + 12), title, font=font_incl_head, fill=ORANGE_TEMPLE, anchor="lm")
        draw.text((330, item_y + 12), desc, font=font_incl_body, fill=TEXT_DARK, anchor="lm")

    # 7. Terms & Conditions Box (ముఖ్య గమనికలు)
    y_terms_sec = y_incl_sec + 285
    draw.rectangle([(35, y_terms_sec), (W - 35, y_terms_sec + 195)], fill=(255, 245, 245), outline=MAROON_DEEP, width=1)
    
    draw.text((55, y_terms_sec + 25), "ముఖ్య గమనిక & యాత్రా నిబంధనలు:", font=font_incl_head, fill=MAROON_DEEP)
    
    terms = [
        "1. సీట్ నిర్ధారణ కొరకు ₹10,000/- అడ్వాన్స్ చెల్లించి మీ పేరు నమోదు చేసుకోగలరు.",
        "2. అన్ని రోజులకు కలిపి డ్రైవర్ బత్తా ₹300/-, వంట సిబ్బందికి ₹200/- ఒకేసారి మాత్రమే చెల్లించవలెను.",
        "3. స్థానిక ప్రయాణ ఖర్చులు (ఆటోలు, రోప్‌వేలు, పడవలు) మరియు దేవాలయ ప్రత్యేక దర్శన టిక్కెట్లు యాత్రికులవే.",
        "4. యాత్ర ప్రశాంతంగా, సజావుగా సాగేందుకు టూర్ మేనేజర్ సూచించిన సమయపాలన పాటించగలరు."
    ]
    for idx, t in enumerate(terms):
        draw.text((55, y_terms_sec + 60 + (idx * 32)), t, font=font_terms, fill=TEXT_DARK)

    # 8. Grand Bottom Contact & Website Footer
    y_footer = y_terms_sec + 210
    draw.rectangle([(28, y_footer), (W - 28, H - 28)], fill=MAROON_DEEP)
    draw.rectangle([(32, y_footer + 4), (W - 32, H - 32)], outline=GOLD_ACCENT, width=2)

    # Contact line
    draw.text((W // 2, y_footer + 50), "📞 వివరాలు & బుకింగ్స్ కొరకు సంప్రదించండి: రమేష్", font=font_tour_h2, fill=GOLD_LIGHT, anchor="mm")
    draw.text((W // 2, y_footer + 105), "ఫోన్ / WhatsApp: 9030780132", font=font_footer_phone, fill=WHITE, anchor="mm")
    
    # Official Website Line
    draw.rectangle([(150, y_footer + 145), (W - 150, y_footer + 205)], fill=ORANGE_TEMPLE, outline=GOLD_LIGHT, width=2)
    draw.text((W // 2, y_footer + 175), "🌐 అధికారిక వెబ్‌సైట్: https://jaisrimannarayana.netlify.app", font=font_footer_web, fill=WHITE, anchor="mm")

    # Save outputs
    local_path = os.path.join("static", "images", "telugu_7jyotirlinga_business_flyer.jpg")
    flyer.save(local_path, format="JPEG", quality=95, optimize=True)
    
    art_path = r"C:\Users\Krishna\.gemini\antigravity\brain\07429a57-70c2-42e3-acfc-b368133aefc7\telugu_7jyotirlinga_business_flyer.jpg"
    flyer.save(art_path, format="JPEG", quality=95, optimize=True)
    
    print(f"[SUCCESS] Master Telugu Business Flyer created:")
    print(f"  Local:    {local_path} ({os.path.getsize(local_path) / 1024:.1f} KB)")
    print(f"  Artifact: {art_path}")

create_business_flyer()
