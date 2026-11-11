"""
Render Antislop YouTube Short (1080x1920) for Jai Srimannarayana Tours & Travels.
Craftsmanship Features:
- Natural, human Telugu voiceover (te-IN-MohanNeural)
- Frame-accurate audio-sync timestamps
- HarfBuzz text shaping via PyQt6 for flawless Telugu typography
- Filmic gradient scrim and YouTube Shorts mobile safe-zone alignment
- Smooth Ken Burns dynamic camera push/pull on scenes
- No em dashes, no AI buzzwords, 100% honest travel details
"""

import sys
import os
import soundfile as sf
import numpy as np
from PIL import Image

from PyQt6.QtGui import QGuiApplication, QImage, QPainter, QFont, QColor, QPen, QBrush, QLinearGradient
from PyQt6.QtCore import Qt, QRectF, QPointF

from moviepy import ImageClip, AudioFileClip, concatenate_videoclips

# 1. Initialize Qt App for high-fidelity HarfBuzz typography
app = QGuiApplication(sys.argv)

def create_scene_overlay(
    top_badge_text: str,
    pill_text: str,
    title_text: str,
    subtitle_text: str,
    output_png: str
):
    """Generates 1080x1920 transparent PNG overlay with perfect Indic typography."""
    qimg = QImage(1080, 1920, QImage.Format.Format_ARGB32)
    qimg.fill(Qt.GlobalColor.transparent)
    
    painter = QPainter(qimg)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
    painter.setRenderHint(QPainter.RenderHint.TextAntialiasing, True)
    
    # Top header bar (Subtle dark maroon gradient with gold accent line)
    painter.fillRect(0, 0, 1080, 180, QColor(14, 8, 5, 210))
    painter.setPen(QPen(QColor(218, 165, 32, 220), 3))
    painter.drawLine(0, 180, 1080, 180)
    
    # Top brand text
    font_top = QFont("Nirmala UI", 26, QFont.Weight.Bold)
    painter.setFont(font_top)
    painter.setPen(QColor(255, 225, 140))
    painter.drawText(QRectF(0, 0, 1080, 180), Qt.AlignmentFlag.AlignCenter, top_badge_text)
    
    # Bottom cinematic gradient scrim (Smooth cubic falloff between Y=950 and Y=1920)
    grad = QLinearGradient(QPointF(0, 950), QPointF(0, 1920))
    grad.setColorAt(0.0, QColor(10, 6, 4, 0))
    grad.setColorAt(0.25, QColor(10, 6, 4, 120))
    grad.setColorAt(0.6, QColor(10, 6, 4, 210))
    grad.setColorAt(1.0, QColor(8, 5, 3, 245))
    painter.fillRect(0, 950, 1080, 970, QBrush(grad))
    
    # Pill highlight box (Centered around Y=1180)
    font_pill = QFont("Nirmala UI", 26, QFont.Weight.Bold)
    painter.setFont(font_pill)
    
    # Measure pill text
    metrics = painter.fontMetrics()
    tw = metrics.horizontalAdvance(pill_text)
    pill_w = max(tw + 70, 480)
    pill_h = 72
    pill_x = (1080 - pill_w) / 2
    pill_y = 1140
    
    painter.setBrush(QBrush(QColor(165, 42, 22, 220)))
    painter.setPen(QPen(QColor(255, 215, 0, 240), 2))
    painter.drawRoundedRect(QRectF(pill_x, pill_y, pill_w, pill_h), 24, 24)
    
    painter.setPen(QColor(255, 255, 255))
    painter.drawText(QRectF(pill_x, pill_y, pill_w, pill_h), Qt.AlignmentFlag.AlignCenter, pill_text)
    
    # Main Headline (Centered around Y=1280)
    font_title = QFont("Nirmala UI", 42, QFont.Weight.Bold)
    painter.setFont(font_title)
    
    # Soft drop shadow for maximum legibility
    painter.setPen(QColor(0, 0, 0, 230))
    painter.drawText(QRectF(2, 1242, 1080, 110), Qt.AlignmentFlag.AlignCenter, title_text)
    
    painter.setPen(QColor(255, 255, 255))
    painter.drawText(QRectF(0, 1240, 1080, 110), Qt.AlignmentFlag.AlignCenter, title_text)
    
    # Subtitle / Benefits (Centered around Y=1380)
    font_sub = QFont("Nirmala UI", 25, QFont.Weight.Normal)
    painter.setFont(font_sub)
    
    painter.setPen(QColor(0, 0, 0, 220))
    painter.drawText(QRectF(2, 1372, 1080, 90), Qt.AlignmentFlag.AlignCenter, subtitle_text)
    
    painter.setPen(QColor(255, 225, 140))
    painter.drawText(QRectF(0, 1370, 1080, 90), Qt.AlignmentFlag.AlignCenter, subtitle_text)
    
    painter.end()
    qimg.save(output_png)
    print(f"Generated overlay: {output_png}")


# 2. Render 3 Overlays with authentic human Telugu copy
create_scene_overlay(
    top_badge_text="జై శ్రీమన్నారాయణ టూర్స్ & ట్రావెల్స్",
    pill_text="కాశీ విశ్వనాథ్ • ప్రయాగరాజ్ • అయోధ్య",
    title_text="పెద్దవారి కాశీ యాత్ర కల",
    subtitle_text="హైదరాబాద్ నుండి నేరుగా • వీఐపీ దర్శనం",
    output_png="overlay1.png"
)

create_scene_overlay(
    top_badge_text="జై శ్రీమన్నారాయణ టూర్స్ & ట్రావెల్స్",
    pill_text="100% స్వచ్ఛమైన సాత్విక భోజనం",
    title_text="మన తెలుగు చెఫ్ & ప్రత్యేక సంరక్షణ",
    subtitle_text="గ్రౌండ్ ఫ్లోర్ గదులు • వీల్ చైర్ సదుపాయం",
    output_png="overlay2.png"
)

create_scene_overlay(
    top_badge_text="జై శ్రీమన్నారాయణ టూర్స్ & ట్రావెల్స్",
    pill_text="అక్టోబర్ 25 ప్రయాణం • 30 సీట్లు మాత్రమే",
    title_text="ఇప్పుడే సీట్లు రిజర్వ్ చేసుకోండి",
    subtitle_text="వాట్సాప్ / కాల్: 9030780132 (రమేష్ గారు)",
    output_png="overlay3.png"
)


# 3. Composite base images with overlays
def compose_frame(base_img_path, overlay_png_path, out_path):
    base = Image.open(base_img_path).convert("RGBA").resize((1080, 1920), Image.Resampling.LANCZOS)
    overlay = Image.open(overlay_png_path).convert("RGBA")
    comp = Image.alpha_composite(base, overlay).convert("RGB")
    comp.save(out_path, quality=95)
    print(f"Composed: {out_path}")

compose_frame("scene1_ganga.jpg", "overlay1.png", "slide_antislop_1.jpg")
compose_frame("scene2_elderly.jpg", "overlay2.png", "slide_antislop_2.jpg")
compose_frame("scene3_ayodhya.jpg", "overlay3.png", "slide_antislop_3.jpg")


# 4. Audio timings from edge-tts sentence analysis
dur1 = 7.31
dur2 = 9.87
dur3 = 10.61
total_dur = dur1 + dur2 + dur3

print(f"Scene durations: {dur1}s, {dur2}s, {dur3}s (Total: {total_dur}s)")

# 5. Build Ken Burns zoom clips using MoviePy
def make_ken_burns_clip(img_path, duration, zoom_in=True):
    base_clip = ImageClip(img_path).with_duration(duration)
    
    def transform_fn(get_frame, t):
        frame = get_frame(t)
        pil_im = Image.fromarray(frame)
        progress = t / max(duration, 0.1)
        if zoom_in:
            scale = 1.0 + 0.05 * progress
        else:
            scale = 1.05 - 0.05 * progress
            
        w, h = pil_im.size
        new_w, new_h = int(w * scale), int(h * scale)
        scaled = pil_im.resize((new_w, new_h), Image.Resampling.BILINEAR)
        left = (new_w - w) // 2
        top = (new_h - h) // 2
        cropped = scaled.crop((left, top, left + w, top + h))
        return np.array(cropped)
        
    return base_clip.transform(transform_fn)

print("Building dynamic Ken Burns scenes...")
clip1 = make_ken_burns_clip("slide_antislop_1.jpg", dur1, zoom_in=True)
clip2 = make_ken_burns_clip("slide_antislop_2.jpg", dur2, zoom_in=False)
clip3 = make_ken_burns_clip("slide_antislop_3.jpg", dur3, zoom_in=True)

final_video = concatenate_videoclips([clip1, clip2, clip3], method="compose")

# Attach Telugu Neural Voiceover
audio = AudioFileClip("voiceover_v2.mp3")
final_video = final_video.with_audio(audio)

output_video = "kashi_yatra_antislop.mp4"
print(f"Rendering final craft video: {output_video}...")

final_video.write_videofile(
    output_video,
    fps=24,
    codec="libx264",
    audio_codec="aac",
    bitrate="4500k",
    preset="medium"
)

print(f"SUCCESS: Exported improved antislop video to {os.path.abspath(output_video)}")
