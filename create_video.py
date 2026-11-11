"""
Render high-definition YouTube Short (1080x1920) for Kashi Yatra Oct 25th.
Combines:
- 3 AI-generated devotional visuals
- Edge-TTS Telugu voiceover (te-IN-MohanNeural)
- Devotional banners, subtitles, and contact graphics
- Outputs kashi_yatra_oct25.mp4
"""

import os
import shutil
from PIL import Image, ImageDraw, ImageFont
import soundfile as sf
import moviepy as mp
from moviepy import ImageClip, AudioFileClip, concatenate_videoclips

# Image source paths
img_brain_dir = r"C:\Users\Krishna\.gemini\antigravity\brain\07429a57-70c2-42e3-acfc-b368133aefc7"
img1_src = os.path.join(img_brain_dir, "kashi_ganga_aarti_1791554360025.jpg")
img2_src = os.path.join(img_brain_dir, "elderly_pilgrims_care_1791554415786.jpg")
img3_src = os.path.join(img_brain_dir, "ayodhya_ram_mandir_1791554385289.jpg")

# Copy to local workspace
shutil.copy(img1_src, "scene1_ganga.jpg")
shutil.copy(img2_src, "scene2_elderly.jpg")
shutil.copy(img3_src, "scene3_ayodhya.jpg")

print("Images copied to workspace.")

# Get audio duration
audio_path = "voiceover.mp3"
data, samplerate = sf.read(audio_path)
total_duration = len(data) / samplerate
clip_duration = total_duration / 3.0

print(f"Total duration: {total_duration:.2f}s | Per clip: {clip_duration:.2f}s")

# Create graphic overlays for each scene (1080x1920)
def process_scene_image(img_path, top_text, main_title, subtitle, badge_text, output_path):
    img = Image.open(img_path).convert("RGBA")
    img = img.resize((1080, 1920), Image.Resampling.LANCZOS)
    
    # Overlay layer
    overlay = Image.new("RGBA", (1080, 1920), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    
    # Top header banner (Dark maroon with gold border)
    draw.rectangle([(0, 0), (1080, 170)], fill=(20, 10, 5, 230))
    draw.line([(0, 170), (1080, 170)], fill=(255, 204, 0, 255), width=4)
    
    # Bottom text banner (Gradient dark scrim)
    for y in range(1300, 1920):
        alpha = int(220 * (y - 1300) / (1920 - 1300))
        draw.line([(0, y), (1080, y)], fill=(10, 5, 2, alpha))
    
    # Accent badge box
    draw.rounded_rectangle([(80, 1340), (1000, 1430)], radius=20, fill=(218, 165, 32, 240), outline=(255, 255, 255, 255), width=3)
    
    # Try loading bold system font or fallback
    try:
        font_header = ImageFont.truetype("arialbd.ttf", 46)
        font_badge = ImageFont.truetype("arialbd.ttf", 44)
        font_title = ImageFont.truetype("arialbd.ttf", 62)
        font_sub = ImageFont.truetype("arial.ttf", 44)
    except Exception:
        font_header = font_badge = font_title = font_sub = ImageFont.load_default()
    
    # Draw texts
    # Header
    draw.text((540, 85), top_text, fill=(255, 215, 0), font=font_header, anchor="mm")
    
    # Badge
    draw.text((540, 1385), badge_text, fill=(20, 10, 0), font=font_badge, anchor="mm")
    
    # Main Title
    draw.text((540, 1550), main_title, fill=(255, 255, 255), font=font_title, anchor="mm")
    
    # Subtitle
    draw.text((540, 1700), subtitle, fill=(255, 220, 120), font=font_sub, anchor="mm")
    
    # Final composite
    final_img = Image.alpha_composite(img, overlay).convert("RGB")
    final_img.save(output_path, quality=95)
    print(f"Created styled slide: {output_path}")

# Slide 1: Ganga Aarti & Kashi Launch
process_scene_image(
    "scene1_ganga.jpg",
    "JAI SRIMANNARAYANA TOURS & TRAVELS",
    "DIVYA KASHI YATRA",
    "HYDERABAD DEPARTURE: OCT 25TH",
    "VIP SPARSHA DARSHAN & GANGA AARTI",
    "slide1_rendered.jpg"
)

# Slide 2: Telugu Satvik Meals & Senior Citizen Care
process_scene_image(
    "scene2_elderly.jpg",
    "AUTHENTIC TELUGU PILGRIMAGE CARE",
    "100% SATVIK TELUGU BHOJANAM",
    "Ground Floor AC Rooms & Wheelchair Escort",
    "TELUGU CHEF TRAVELING WITH GROUP",
    "slide2_rendered.jpg"
)

# Slide 3: Ayodhya Ram Mandir & Urgent Booking CTA
process_scene_image(
    "scene3_ayodhya.jpg",
    "AYODHYA RAM LALLA DARSHAN",
    "CALL / WHATSAPP: 9030780132",
    "Ramesh (@telugutravellerramesh5846)",
    "LIMITED SEATS: ONLY 30 PILGRIMS",
    "slide3_rendered.jpg"
)

# Assemble Video using MoviePy
print("Assembling video clips with MoviePy...")
clip1 = ImageClip("slide1_rendered.jpg").with_duration(clip_duration)
clip2 = ImageClip("slide2_rendered.jpg").with_duration(clip_duration)
clip3 = ImageClip("slide3_rendered.jpg").with_duration(clip_duration + (total_duration - (clip_duration * 3)))

video = concatenate_videoclips([clip1, clip2, clip3], method="compose")

# Attach Telugu Neural Voiceover
audio = AudioFileClip(audio_path)
video = video.with_audio(audio)

output_video_path = "kashi_yatra_oct25.mp4"
print(f"Rendering video to {output_video_path}...")

video.write_videofile(
    output_video_path,
    fps=24,
    codec="libx264",
    audio_codec="aac",
    bitrate="4000k",
    preset="medium"
)

print(f"SUCCESS: Video exported to {os.path.abspath(output_video_path)}")
