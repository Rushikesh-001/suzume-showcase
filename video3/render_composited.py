"""
Cinematic Suzume Reel v3 - AVENGERS-STYLE TRAILER
Dramatic pacing, letterbox bars, epic text reveals.
"""
import os, sys, numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from moviepy import (
    VideoClip, ImageClip, AudioClip,
    CompositeVideoClip, concatenate_videoclips,
    AudioFileClip, CompositeAudioClip, ColorClip, vfx
)

OUTPUT_DIR = os.path.dirname(os.path.abspath(__file__))
SCREENSHOTS_DIR = os.path.join(OUTPUT_DIR, "screenshots")
WIDTH, HEIGHT = 1920, 1080
FPS = 30
LETTERBOX = 80  # black bar height top/bottom for 2.35:1 cinematic look

FONT_SEMIBOLD = "C:/Windows/Fonts/seguisb.ttf"
FONT_BOLD = "C:/Windows/Fonts/segoeuib.ttf"
FONT_LIGHT = "C:/Windows/Fonts/segoeuil.ttf"
FONT = FONT_SEMIBOLD if os.path.exists(FONT_SEMIBOLD) else FONT_LIGHT

def make_bg(colors, direction="radial", w=WIDTH, h=HEIGHT):
    y, x = np.mgrid[0:h, 0:w]
    if direction == "radial":
        cx, cy = w/2, h/2
        t = np.sqrt((x-cx)**2 + (y-cy)**2) / np.sqrt(cx**2 + cy**2)
    elif direction == "horizontal":
        t = x / w
    elif direction == "diagonal":
        t = (x + y) / (w + h)
    else:
        t = np.zeros((h, w))
    t = np.clip(t, 0, 1)
    result = np.zeros((h, w, 3))
    n = len(colors)
    for i in range(n-1):
        c1, c2 = np.array(colors[i]), np.array(colors[i+1])
        pos, npos = i/(n-1), (i+1)/(n-1)
        mask = (t >= pos) & (t <= npos)
        lt = np.zeros_like(t)
        lt[mask] = (t[mask] - pos) / (npos - pos)
        for c in range(3):
            result[:,:,c][mask] = c1[c] + (c2[c] - c1[c]) * lt[mask]
    return np.clip(result, 0, 255).astype(np.uint8)

def radial_glow(w, h, cx, cy, radius, color, intensity=0.3):
    y, x = np.mgrid[0:h, 0:w]
    dist = np.sqrt((x-cx)**2 + (y-cy)**2)
    glow = np.exp(-dist / (radius/3)) * intensity
    return np.clip(glow[:,:,np.newaxis] * np.array(color, dtype=np.float32), 0, 255).astype(np.uint8)

print("Pre-rendering backgrounds...")
opening_bg = make_bg([(5,5,20), (15,10,35), (8,5,25)], "radial")
glow = radial_glow(WIDTH, HEIGHT, WIDTH//2, HEIGHT//2, 400, (80,40,150), 0.25)
opening_bg = np.clip(opening_bg.astype(np.float32) * 0.75 + glow * 0.25, 0, 255).astype(np.uint8)
Image.fromarray(opening_bg).save(os.path.join(OUTPUT_DIR, "_bg_opening.png"))
print("  Opening bg OK")

finale_bg = make_bg([(15,10,25), (25,15,40), (10,8,20)], "radial")
glow = radial_glow(WIDTH, HEIGHT, WIDTH//2, HEIGHT//2, 300, (200,150,50), 0.4)
finale_bg = np.clip(finale_bg.astype(np.float32) * 0.6 + glow * 0.4, 0, 255).astype(np.uint8)
Image.fromarray(finale_bg).save(os.path.join(OUTPUT_DIR, "_bg_finale.png"))
print("  Finale bg OK")

# Cinematic letterbox bars
def make_letterbox():
    """Create 21:9 cinematic black bars."""
    bar = ColorClip(size=(WIDTH, LETTERBOX), color=(0,0,0))
    top = bar.with_position((0, 0))
    bottom = bar.with_position((0, HEIGHT - LETTERBOX))
    return [top, bottom]

letterbox_clips = make_letterbox()

# ============ TEXT RENDERER ============
_text_cache = {}

def render_text(text, font_size=48, color=(245,245,255), shadow_alpha=180,
                max_width=1600, pos="center", font_path=None, glow_color=None):
    key = (text, font_size, color, shadow_alpha, max_width, pos, font_path, glow_color)
    if key in _text_cache:
        return _text_cache[key]
    
    fp = font_path or FONT
    if fp and os.path.exists(fp):
        try:
            font = ImageFont.truetype(fp, font_size)
        except:
            font = ImageFont.load_default()
    else:
        font = ImageFont.load_default()
    
    words = text.split()
    lines = []
    cur = ""
    for word in words:
        test = cur + " " + word if cur else word
        bbox = font.getbbox(test)
        if bbox and (bbox[2]-bbox[0]) > max_width and cur:
            lines.append(cur)
            cur = word
        else:
            cur = test
    if cur: lines.append(cur)
    
    try:
        # Fix for fonts that return 0 bbox
        bboxes = []
        for l in lines:
            bb = font.getbbox(l)
            bboxes.append(bb[3]-bb[1] if bb else font_size)
        line_h = max(bboxes) if bboxes else font_size
    except:
        line_h = font_size
    spacing = int(line_h * 0.3)
    total_h = len(lines)*line_h + (len(lines)-1)*spacing + 40
    try:
        max_w = max((font.getbbox(l)[2]-font.getbbox(l)[0]) for l in lines) if lines else 0
    except:
        max_w = max_width
    cw = max(min(max_w+120, max_width), 100)
    ch = max(total_h + 40, 60)
    
    pil = Image.new("RGBA", (cw, ch), (0,0,0,0))
    draw = ImageDraw.Draw(pil)
    
    for i, line in enumerate(lines):
        try:
            bbox = font.getbbox(line)
            lw = bbox[2]-bbox[0]
        except:
            lw = len(line) * font_size * 0.6
        x = (cw-lw)//2 if pos == "center" else (30 if pos == "left" else cw-lw-30)
        y = 20 + i*(line_h+spacing)
        # Outer glow
        if glow_color:
            for ox, oy in [(-3,-3),(3,-3),(-3,3),(3,3),(0,-4),(0,4),(-4,0),(4,0)]:
                draw.text((x+ox, y+oy), line, font=font, fill=(*glow_color, 60))
        # Shadow
        if shadow_alpha > 0:
            draw.text((x+3, y+3), line, font=font, fill=(0,0,0,shadow_alpha))
        draw.text((x, y), line, font=font, fill=(*color, 255))
    
    result = np.array(pil)
    _text_cache[key] = result
    return result

def make_text_clip(text, font_size, color, start, duration, 
                    position=("center", "center"), fade_in=0.5,
                    shadow=True, font_path=None, offset_y=0, glow_color=None):
    txt = render_text(text, font_size, color, 
                      shadow_alpha=180 if shadow else 0,
                      font_path=font_path, glow_color=glow_color)
    tw, th = txt.shape[1], txt.shape[0]
    
    if position[0] == "center":
        x = WIDTH // 2 - tw // 2
    else:
        x = int(position[0])
    
    if isinstance(position[1], (int, float)):
        y = int(position[1]) + offset_y
    elif position[1] == "center":
        y = HEIGHT // 2 - th // 2 + offset_y
    else:
        y = int(position[1]) + offset_y
    
    clip = ImageClip(txt).with_position((x, y))
    clip = clip.with_start(start).with_duration(duration)
    if fade_in > 0:
        clip = clip.with_effects([vfx.FadeIn(fade_in)])
    return clip

def load_screenshot(name, start, duration, fade_in=0.5):
    path = os.path.join(SCREENSHOTS_DIR, f"{name}.png")
    if not os.path.exists(path):
        print(f"  WARNING: Screenshot not found: {name}")
        return None
    clip = ImageClip(path).with_start(start).with_duration(duration)
    if fade_in > 0:
        clip = clip.with_effects([vfx.FadeIn(fade_in)])
    return clip

def make_overlay_clip(start, duration, color=(0,0,0), opacity=0.4):
    overlay = ColorClip(size=(WIDTH, HEIGHT), color=color).with_opacity(opacity)
    overlay = overlay.with_start(start).with_duration(duration)
    return overlay

# ============ GET TTS ============
print("Loading TTS files...")
tts_files = [
    (1.5, "tts_01.wav"),
    (11.5, "tts_02.wav"),
    (20.5, "tts_03.wav"),
    (31.5, "tts_04.wav"),
    (44.0, "tts_05.wav"),
    (54.5, "tts_06.wav"),
    (66.5, "tts_07.wav"),
]

# ============ BUILD COMPOSITE ============
print("\nBuilding cinematic composite...")
all_clips = []

# --- SCENE 1: EPIC OPENING (0-11.5s) ---
# Black screen first
black1 = ColorClip(size=(WIDTH, HEIGHT), color=(0,0,0)).with_duration(2.0)
all_clips.append(black1)

bg1 = ImageClip(os.path.join(OUTPUT_DIR, "_bg_opening.png")).with_start(2.0).with_duration(10.0)
all_clips.append(bg1)

# Cinematic chapter label
chapter1 = make_text_clip("01  ///  ORIGIN", 18, (180,180,210), 1.0, 8.0,
                           position=("center", 160), fade_in=0.5)
all_clips.append(chapter1)

# Main title - big dramatic reveal
main_title = make_text_clip("SUZUME", 120, (255,195,80), 2.5, 10.0,
                             position=("center", "center"), fade_in=2.0, offset_y=-60,
                             font_path=FONT_BOLD, glow_color=(200,150,50))
all_clips.append(main_title)

# Tagline
tagline1 = make_text_clip("SEVEN AGENTS. ONE ORCHESTRATOR.", 26, (200,200,230), 5.0, 6.0,
                           position=("center", "center"), fade_in=1.5, offset_y=80)
all_clips.append(tagline1)

# Bottom cinematic subtitle
sub1 = make_text_clip("Production-ready code, every time.", 20, (140,140,170), 7.0, 3.5,
                       position=("center", HEIGHT - LETTERBOX - 60), fade_in=1.0)
all_clips.append(sub1)

# Black transition out
black_out1 = ColorClip(size=(WIDTH, HEIGHT), color=(0,0,0)).with_start(11.5).with_duration(1.0)
all_clips.append(black_out1)

# --- SCENE 2: SUPREME AI (12-20.5s) ---
bg2_start = 12.0
ss = load_screenshot("official_hero", bg2_start, 8.5, fade_in=0.3)
if ss:
    all_clips.append(ss)
ol2 = make_overlay_clip(bg2_start, 8.5, opacity=0.55)
all_clips.append(ol2)

chapter2 = make_text_clip("02  ///  WHAT IS SUZUME", 18, (180,180,210), bg2_start + 0.3, 7.0,
                           position=("center", 160), fade_in=0.5)
all_clips.append(chapter2)

# Dramatic text reveals one by one
dramatic_texts = [
    ("Supreme AI Companion", 52, (255,195,80), bg2_start + 0.5),
    ("Master Software Architect", 40, (200,200,230), bg2_start + 3.0),
    ("System Automation Force", 40, (200,200,230), bg2_start + 5.5),
]
for text, fs, color, st in dramatic_texts:
    clip = make_text_clip(text, fs, color, st, 3.0,
                          position=("center", 340), fade_in=0.8)
    all_clips.append(clip)

# --- SCENE 3: CAPABILITIES (20.5-31.5s) ---
bg3_start = 20.5
ss = load_screenshot("section_capabilities", bg3_start, 11.0, fade_in=0.3)
if ss:
    all_clips.append(ss)
ol3 = make_overlay_clip(bg3_start, 11.0, opacity=0.5)
all_clips.append(ol3)

chapter3 = make_text_clip("03  ///  CAPABILITIES", 18, (180,180,210), bg3_start + 0.3, 9.0,
                           position=("center", 160), fade_in=0.5)
all_clips.append(chapter3)

cap_extra = [
    ("Full Stack Web: React, Next.js, Node.js", 30, (255,195,80), bg3_start + 0.8),
    ("3D Experiences: Three.js, WebGL, Unity", 28, (200,200,230), bg3_start + 2.8),
    ("AI Pipelines: Python, ML, Data Processing", 28, (200,200,230), bg3_start + 4.8),
    ("System Automation: PowerShell, OS, CI/CD", 28, (200,200,230), bg3_start + 6.8),
    ("Every layer of the stack.", 32, (180,180,220), bg3_start + 8.8),
]
for text, fs, color, st in cap_extra:
    clip = make_text_clip(text, fs, color, st, 2.5,
                          position=("center", 310), fade_in=0.6)
    all_clips.append(clip)

# --- SCENE 4: DEMO SHOWCASE (31.5-44s) ---
# Fast cuts of demos
demos = [
    ("snake_game", 31.5, "SNAKE GAME", "Canvas, Touch, High Scores"),
    ("threed_demo", 34.5, "3D EXPERIENCE", "Three.js, 7 Scenes, WebGL"),
    ("saas_site", 37.5, "SAAS LANDING", "Particles, Glassmorphism"),
]
for img, st, title, desc in demos:
    ss = load_screenshot(img, st, 3.0, fade_in=0.2)
    if ss:
        all_clips.append(ss)
    ol = make_overlay_clip(st, 3.0, opacity=0.45)
    all_clips.append(ol)
    
    t_clip = make_text_clip(title, 36, (255,195,80), st + 0.2, 2.5,
                             position=("center", 300), fade_in=0.4)
    all_clips.append(t_clip)
    d_clip = make_text_clip(desc, 22, (200,200,230), st + 0.5, 2.0,
                             position=("center", 360), fade_in=0.4)
    all_clips.append(d_clip)

# "All built autonomously" tag
bg4_start = 40.5
ss = load_screenshot("section_demos", bg4_start, 3.5, fade_in=0.3)
if ss:
    all_clips.append(ss)
ol4 = make_overlay_clip(bg4_start, 3.5, opacity=0.5)
all_clips.append(ol4)
auto_tag = make_text_clip("5 WORKING DEMOS  ///  ALL BUILT AUTONOMOUSLY", 28, (255,195,80), bg4_start + 0.3, 2.5,
                           position=("center", "center"), fade_in=0.5)
all_clips.append(auto_tag)

# --- SCENE 5: WORKFLOW (44-54.5s) ---
bg5_start = 44.0
ss = load_screenshot("section_process", bg5_start, 10.5, fade_in=0.3)
if ss:
    all_clips.append(ss)
ol5 = make_overlay_clip(bg5_start, 10.5, opacity=0.5)
all_clips.append(ol5)

chapter5 = make_text_clip("04  ///  HOW IT WORKS", 18, (180,180,210), bg5_start + 0.3, 8.0,
                           position=("center", 160), fade_in=0.5)
all_clips.append(chapter5)

steps = [
    ("YOU GIVE A TASK", bg5_start + 0.8),
    ("I DESIGN THE ARCHITECTURE", bg5_start + 2.5),
    ("7 AGENTS WORK IN PARALLEL", bg5_start + 4.5),
    ("EVERY FILE IS TESTED", bg5_start + 6.5),
    ("DELIVERED COMPLETE + DEPLOYED", bg5_start + 8.5),
]
for text, st in steps:
    clip = make_text_clip(text, 30, (255,195,80), st, 2.0,
                          position=("center", 310), fade_in=0.5)
    all_clips.append(clip)

# --- SCENE 6: AGENT TEAM (54.5-66.5s) ---
bg6_start = 54.5
ss = load_screenshot("section_process", bg6_start, 12.0, fade_in=0.3)
if ss:
    all_clips.append(ss)
ol6 = make_overlay_clip(bg6_start, 12.0, opacity=0.5)
all_clips.append(ol6)

chapter6 = make_text_clip("05  ///  THE TEAM", 18, (180,180,210), bg6_start + 0.3, 10.0,
                           position=("center", 120), fade_in=0.5)
all_clips.append(chapter6)

agents_data = [
    ("worker-js", "Frontend  |  Node.js  |  APIs", bg6_start + 0.8),
    ("worker-python", "Backend  |  Data  |  ML", bg6_start + 2.3),
    ("worker-unity", "3D Games  |  HDRP  |  Physics", bg6_start + 3.8),
    ("worker-sys", "PowerShell  |  OS  |  Automation", bg6_start + 5.3),
    ("worker-web", "CSS  |  UI  |  Design", bg6_start + 6.8),
    ("builder", "Compilation  |  CI/CD  |  Builds", bg6_start + 8.3),
    ("reviewer", "Code Audit  |  Security  |  QA", bg6_start + 9.8),
]
for i, (name, desc, st) in enumerate(agents_data):
    clip = make_text_clip(f"{name}  {desc}", 26, (200,200,230), st, 2.0,
                          position=("center", 230 + (i % 4) * 50), fade_in=0.4)
    all_clips.append(clip)

# --- SCENE 7: FINALE (66.5-80s) ---
bg7_start = 66.5
bg7 = ImageClip(os.path.join(OUTPUT_DIR, "_bg_finale.png")).with_start(bg7_start).with_duration(13.5)
all_clips.append(bg7)

# Cinematic ending
final_title = make_text_clip("SUZUME", 130, (255,195,80), bg7_start + 0.5, 10.0,
                              position=("center", "center"), fade_in=2.0, offset_y=-80,
                              font_path=FONT_BOLD, glow_color=(200,150,50))
all_clips.append(final_title)

final_tag = make_text_clip("Supreme AI  .  Master Architect  .  Automation Force", 26, (200,200,230), bg7_start + 3.0, 7.0,
                           position=("center", "center"), fade_in=1.0, offset_y=60)
all_clips.append(final_tag)

final_cta = make_text_clip("Your vision, delivered with quality.", 22, (160,155,180), bg7_start + 5.0, 5.0,
                           position=("center", "center"), fade_in=1.0, offset_y=140)
all_clips.append(final_cta)

# Add letterbox to ALL clips by including them at the end (they render on top)
for lb in letterbox_clips:
    # Extend letterbox to full duration
    lb = lb.with_duration(80)
    all_clips.append(lb)

# ============ COMPOSITE ============
print(f"\nCompositing {len(all_clips)} clips...")
final = CompositeVideoClip(all_clips, size=(WIDTH, HEIGHT))

# ============ AUDIO ============
print("Loading audio...")
audio_clips = []

bgm_path = os.path.join(OUTPUT_DIR, "bgm_cinematic.wav")
if os.path.exists(bgm_path):
    bgm = AudioFileClip(bgm_path).with_volume_scaled(0.65)
    audio_clips.append(bgm)

# TTS - non-overlapping
tts_schedule = [
    (1.5, "tts_01.wav"),
    (11.5, "tts_02.wav"),
    (20.5, "tts_03.wav"),
    (31.5, "tts_04.wav"),
    (44.0, "tts_05.wav"),
    (54.5, "tts_06.wav"),
    (66.5, "tts_07.wav"),
]
for st, fname in tts_schedule:
    path = os.path.join(OUTPUT_DIR, fname)
    if os.path.exists(path):
        try:
            ac = AudioFileClip(path).with_start(st)
            audio_clips.append(ac)
        except Exception as e:
            print(f"  Error loading TTS {fname}: {e}")

if audio_clips:
    final = final.with_audio(CompositeAudioClip(audio_clips))

# ============ RENDER ============
out_path = os.path.join(OUTPUT_DIR, "suzume_cinematic.mp4")
print(f"\nRendering cinematic trailer to: {out_path}")

final.write_videofile(
    out_path,
    codec="libx264",
    audio_codec="aac",
    fps=FPS,
    bitrate="14000k",
    audio_bitrate="320k",
    preset="medium",
    ffmpeg_params=["-pix_fmt", "yuv420p", "-profile:v", "high", "-movflags", "+faststart"],
)

size = os.path.getsize(out_path) / (1024*1024)
print(f"\nOK Video: {out_path}")
print(f"  Size: {size:.1f} MB")
