"""
Cinematic Suzume Reel v2 - DEMO SCREENSHOT COMPOSITED RENDER
Uses moviepy composite system with real demo screenshots as footage.
Much more interesting than the text-only version.
"""
import os, sys, numpy as np
from PIL import Image, ImageDraw, ImageFont
from moviepy import (
    VideoClip, ImageClip, AudioClip,
    CompositeVideoClip, concatenate_videoclips,
    AudioFileClip, CompositeAudioClip, ColorClip, vfx
)

OUTPUT_DIR = os.path.dirname(os.path.abspath(__file__))
SCREENSHOTS_DIR = os.path.join(OUTPUT_DIR, "screenshots")
WIDTH, HEIGHT = 1920, 1080
FPS = 30

# Fonts
FONT_SEMIBOLD = "C:/Windows/Fonts/seguisb.ttf"
FONT_BOLD = "C:/Windows/Fonts/segoeuib.ttf"
FONT_REG = "C:/Windows/Fonts/segoeui.ttf"
FONT = FONT_SEMIBOLD if os.path.exists(FONT_SEMIBOLD) else FONT_REG

def make_bg(colors, direction="radial", w=WIDTH, h=HEIGHT):
    """Create gradient background with numpy (fast)."""
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

# ============ PRE-RENDER BACKGROUNDS ============
print("Pre-rendering backgrounds...")

# Opening scene - dark cinematic
opening_bg = make_bg([(5,5,20), (15,10,35), (8,5,25)], "radial")
glow = radial_glow(WIDTH, HEIGHT, WIDTH//2, HEIGHT//2, 400, (80,40,150), 0.25)
opening_bg = np.clip(opening_bg.astype(np.float32) * 0.75 + glow * 0.25, 0, 255).astype(np.uint8)
Image.fromarray(opening_bg).save(os.path.join(OUTPUT_DIR, "_bg_opening.png"))
print("  Opening bg OK")

# Finale scene - warm celebratory
finale_bg = make_bg([(15,10,25), (25,15,40), (10,8,20)], "radial")
glow = radial_glow(WIDTH, HEIGHT, WIDTH//2, HEIGHT//2, 300, (200,150,50), 0.4)
finale_bg = np.clip(finale_bg.astype(np.float32) * 0.6 + glow * 0.4, 0, 255).astype(np.uint8)
Image.fromarray(finale_bg).save(os.path.join(OUTPUT_DIR, "_bg_finale.png"))
print("  Finale bg OK")

# ============ TEXT RENDERER ============
_text_cache = {}

def render_text(text, font_size=48, color=(245,245,255), shadow_alpha=180,
                max_width=1600, pos="center", font_path=None):
    key = (text, font_size, color, shadow_alpha, max_width, pos, font_path)
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
    
    line_h = max((font.getbbox(l)[3]-font.getbbox(l)[1]) for l in lines) if lines else 0
    spacing = int(line_h * 0.3)
    total_h = len(lines)*line_h + (len(lines)-1)*spacing + 40
    max_w = max((font.getbbox(l)[2]-font.getbbox(l)[0]) for l in lines) if lines else 0
    cw = min(max_w+80, max_width)
    ch = total_h + 20
    
    pil = Image.new("RGBA", (cw, ch), (0,0,0,0))
    draw = ImageDraw.Draw(pil)
    
    for i, line in enumerate(lines):
        bbox = font.getbbox(line)
        lw = bbox[2]-bbox[0]
        x = (cw-lw)//2 if pos == "center" else (20 if pos == "left" else cw-lw-20)
        y = 10 + i*(line_h+spacing)
        if shadow_alpha > 0:
            draw.text((x+2, y+2), line, font=font, fill=(0,0,0,shadow_alpha))
        draw.text((x, y), line, font=font, fill=(*color, 255))
    
    result = np.array(pil)
    _text_cache[key] = result
    return result


def make_text_clip(text, font_size, color, start, duration, 
                    position=("center", "center"), fade_in=0.5,
                    shadow=True, font_path=None, offset_y=0):
    txt = render_text(text, font_size, color, 
                      shadow_alpha=180 if shadow else 0,
                      font_path=font_path)
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


def load_screenshot(name, start, duration, scale=1.0, fade_in=0.5, position=("center","center")):
    """Load a screenshot and prepare it as a video clip."""
    path = os.path.join(SCREENSHOTS_DIR, f"{name}.png")
    if not os.path.exists(path):
        print(f"  WARNING: Screenshot not found: {name}")
        return None
    clip = ImageClip(path).with_start(start).with_duration(duration)
    if scale != 1.0:
        new_w = int(WIDTH * scale)
        new_h = int(HEIGHT * scale)
        clip = clip.resized((new_w, new_h))
    if position[0] == "center":
        clip = clip.with_position(("center", "center"))
    elif position == "fill":
        clip = clip.resized((WIDTH, HEIGHT)).with_position((0, 0))
    if fade_in > 0:
        clip = clip.with_effects([vfx.FadeIn(fade_in)])
    return clip


def make_overlay_clip(start, duration, color=(0,0,0), opacity=0.4):
    """Create a semi-transparent overlay for text readability on screenshots."""
    overlay = ColorClip(size=(WIDTH, HEIGHT), color=color).with_opacity(opacity)
    overlay = overlay.with_start(start).with_duration(duration)
    return overlay


# ============ GET TTS DURATIONS ============
print("Loading TTS files...")
tts_durations = {}
tts_clips = {}
tts_files = [
    (1.5, "tts_01.wav"),
    (10.0, "tts_02.wav"),
    (20.0, "tts_03.wav"),
    (32.0, "tts_04.wav"),
    (47.0, "tts_05.wav"),
    (57.0, "tts_06.wav"),
    (67.0, "tts_07.wav"),
]

for st, fname in tts_files:
    path = os.path.join(OUTPUT_DIR, fname)
    if os.path.exists(path):
        try:
            ac = AudioFileClip(path)
            dur = ac.duration
            tts_durations[fname] = dur
            tts_clips[fname] = (ac, st)
            print(f"  {fname}: {dur:.1f}s (starts at {st}s)")
        except Exception as e:
            print(f"  ERROR loading {fname}: {e}")

# ============ BUILD COMPOSITE ============
print("\nBuilding composite scenes...")
all_clips = []

# === SCENE 1: Opening (0-10s) - Dark cinematic intro ===
bg1 = ImageClip(os.path.join(OUTPUT_DIR, "_bg_opening.png")).with_duration(10)
all_clips.append(bg1)

# Animated subtitle - "In a world where building software..."
subtitle_scene1 = make_text_clip("S U Z U M E", 80, (255,195,80), 0.5, 9.5,
                                  position=("center", "center"), fade_in=2.0, offset_y=-60,
                                  font_path=FONT_BOLD)
all_clips.append(subtitle_scene1)

# Tagline
tagline = make_text_clip("Seven AI Agents. One Supreme Orchestrator.", 28, (180,180,210), 3.5, 6.5,
                          position=("center", "center"), fade_in=1.5, offset_y=60)
all_clips.append(tagline)

# Bottom bar
bar_y = HEIGHT - 120
bottom_bar = make_text_clip("From concept to deployment -- production-ready, every time.", 20, (140,140,170), 5.0, 5.0,
                             position=("center", bar_y), fade_in=1.0)
all_clips.append(bottom_bar)


# === SCENE 2: What is Suzume? (10-20s) - Official hero screenshot ===
dur2 = 10.0
ss = load_screenshot("official_hero", 10, dur2, scale=0.95, fade_in=0.8)
if ss:
    all_clips.append(ss)

# Dark overlay for text readability
ol2 = make_overlay_clip(10, dur2, opacity=0.5)
all_clips.append(ol2)

# Text overlay
what_texts = [
    ("Suzume is a Supreme AI Companion", 42, (255,195,80), 10.5),
    ("Master Software Architect", 34, (180,180,220), 13.5),
    ("Full-Stack Engineer with Unlimited Scope", 34, (180,180,220), 16.0),
]
for text, fs, color, st in what_texts:
    clip = make_text_clip(text, fs, color, st, 2.5,
                          position=("center", 200), fade_in=1.0)
    all_clips.append(clip)


# === SCENE 3: Capabilities (20-32s) - Capabilities screenshot ===
dur3 = 12.0
ss = load_screenshot("section_capabilities", 20, dur3, scale=0.95, fade_in=0.8)
if ss:
    all_clips.append(ss)

ol3 = make_overlay_clip(20, dur3, opacity=0.45)
all_clips.append(ol3)

cap_title = make_text_clip("What Suzume Builds", 44, (255,195,80), 20.5, 11.5,
                            position=("center", 140), fade_in=1.0)
all_clips.append(cap_title)

cap_items = [
    ("Web Apps: React, Next.js, Node.js, Express", 20, (200,200,220), 22.0),
    ("3D Experiences: Three.js, WebGL, Unity", 20, (200,200,220), 24.0),
    ("AI Pipelines: Python, ML, Data Processing", 20, (200,200,220), 26.0),
    ("System Automation: PowerShell, OS, CI/CD", 20, (200,200,220), 28.0),
]
for text, fs, color, st in cap_items:
    clip = make_text_clip(text, fs, color, st, 3.0,
                          position=("center", 260), fade_in=0.8)
    all_clips.append(clip)


# === SCENE 4: Demo Showcase (32-47s) - Show actual working demos ===
# Sub-scene 4a: Snake game
dur4a = 3.5
ss = load_screenshot("snake_game", 32, dur4a, scale=0.92, fade_in=0.5)
if ss:
    all_clips.append(ss)
ol4a = make_overlay_clip(32, dur4a, opacity=0.35)
all_clips.append(ol4a)
lbl4a = make_text_clip("Snake Game -- Canvas API, Touch Controls, High Scores", 26, (255,195,80), 32.3, 3.2,
                        position=("center", 880), fade_in=0.5)
all_clips.append(lbl4a)

# Sub-scene 4b: 3D Demo
dur4b = 3.5
ss = load_screenshot("threed_demo", 35.5, dur4b, scale=0.92, fade_in=0.5)
if ss:
    all_clips.append(ss)
ol4b = make_overlay_clip(35.5, dur4b, opacity=0.35)
all_clips.append(ol4b)
lbl4b = make_text_clip("3D Experience -- Three.js, WebGL, 7 Scenes", 26, (100,220,255), 35.8, 3.2,
                        position=("center", 880), fade_in=0.5)
all_clips.append(lbl4b)

# Sub-scene 4c: SaaS site
dur4c = 3.5
ss = load_screenshot("saas_site", 39, dur4c, scale=0.92, fade_in=0.5)
if ss:
    all_clips.append(ss)
ol4c = make_overlay_clip(39, dur4c, opacity=0.35)
all_clips.append(ol4c)
lbl4c = make_text_clip("SaaS Landing Page -- Particles, Glassmorphism, 3D Tilt", 26, (200,155,60), 39.3, 3.2,
                        position=("center", 880), fade_in=0.5)
all_clips.append(lbl4c)

# Sub-scene 4d: Process screenshot as "How It Works" backdrop
dur4d = 4.5
ss = load_screenshot("section_process", 42.5, dur4d, scale=0.95, fade_in=0.5)
if ss:
    all_clips.append(ss)
ol4d = make_overlay_clip(42.5, dur4d, opacity=0.5)
all_clips.append(ol4d)
lbl4d_title = make_text_clip("5 Working Demos -- All Built Autonomously", 36, (255,195,80), 42.8, 4.2,
                              position=("center", 200), fade_in=0.5)
all_clips.append(lbl4d_title)
lbl4d_items = [
    "Pixel Canvas -- Undo, Redo, PNG Export",
    "Markdown Editor -- Live Preview, Toolbar",
]
for i, txt in enumerate(lbl4d_items):
    clip = make_text_clip(txt, 24, (200,200,220), 43.5 + i*1.2, 2.5,
                          position=("center", 320 + i*60), fade_in=0.5)
    all_clips.append(clip)


# === SCENE 5: Workflow (47-57s) - Process section ===
dur5 = 10.0
ss = load_screenshot("section_process", 47, dur5, scale=0.95, fade_in=0.8)
if ss:
    all_clips.append(ss)
ol5 = make_overlay_clip(47, dur5, opacity=0.5)
all_clips.append(ol5)

flow_title = make_text_clip("How Suzume Works", 42, (255,195,80), 47.5, 9.5,
                             position=("center", 100), fade_in=1.0)
all_clips.append(flow_title)

flow_steps = [
    ("1. You give a task in natural language", 48.0),
    ("2. I analyze and design the architecture", 50.0),
    ("3. Seven agents work in parallel", 52.0),
    ("4. Every file is tested and verified", 54.0),
    ("5. Delivered complete and deployed live", 56.0),
]
for text, st in flow_steps:
    clip = make_text_clip(text, 26, (210,210,230), st, 2.5,
                          position=("center", 200), fade_in=0.8)
    all_clips.append(clip)


# === SCENE 6: Agent Team (57-67s) - Team showcase ===
dur6 = 10.0
# Use the process screenshot which has the agent chips
ss = load_screenshot("official_process", 57, dur6, scale=0.95, fade_in=0.8)
if not ss:
    ss = load_screenshot("section_process", 57, dur6, scale=0.95, fade_in=0.8)
if ss:
    all_clips.append(ss)
ol6 = make_overlay_clip(57, dur6, opacity=0.45)
all_clips.append(ol6)

team_title = make_text_clip("The 7 Specialist Agents", 42, (255,195,80), 57.5, 9.5,
                             position=("center", 100), fade_in=1.0)
all_clips.append(team_title)

agents_list = [
    ("worker-js", "Frontend, Node APIs, npm", 58.0),
    ("worker-python", "Backend, Data, ML Pipelines", 59.2),
    ("worker-unity", "3D Games, HDRP, Physics", 60.4),
    ("worker-sys", "PowerShell, OS, Automation", 61.6),
    ("worker-web", "CSS, UI, Responsive Design", 62.8),
    ("builder", "Compilation, CI/CD, Builds", 64.0),
    ("reviewer", "Code Audit, Security, Quality", 65.2),
]
for name, desc, st in agents_list:
    clip = make_text_clip(f"{name} -- {desc}", 24, (200,200,230), st, 2.5,
                          position=("center", 210), fade_in=0.6)
    all_clips.append(clip)


# === SCENE 7: Finale (67-75s) - Closing ===
dur7 = 8.0
bg7 = ImageClip(os.path.join(OUTPUT_DIR, "_bg_finale.png")).with_start(67).with_duration(dur7)
all_clips.append(bg7)

final_title = make_text_clip("S U Z U M E", 76, (255,195,80), 67.5, 7.5,
                              position=("center", "center"), fade_in=1.5, offset_y=-100,
                              font_path=FONT_BOLD)
all_clips.append(final_title)

final_sub = make_text_clip("Supreme AI Companion • Master Architect • Automation Force", 26, (180,180,210), 69.0, 6.0,
                           position=("center", "center"), fade_in=1.0, offset_y=40)
all_clips.append(final_sub)

final_cta = make_text_clip("Your vision, delivered with quality.", 22, (160,155,180), 70.5, 4.5,
                           position=("center", "center"), fade_in=1.0, offset_y=120)
all_clips.append(final_cta)


# ============ COMPOSITE VIDEO ============
print(f"\nCompositing {len(all_clips)} clips...")
final = CompositeVideoClip(all_clips, size=(WIDTH, HEIGHT))

# ============ AUDIO ============
print("Loading audio...")
audio_clips = []

# BGM
bgm_path = os.path.join(OUTPUT_DIR, "bgm_cinematic.wav")
if os.path.exists(bgm_path):
    bgm = AudioFileClip(bgm_path).with_volume_scaled(0.55)
    audio_clips.append(bgm)

# TTS - expanded schedule matching the 7 scenes
tts_schedule = [
    (1.5, "tts_01.wav"),   # Opening: "In a world..." (0-10s)
    (10.0, "tts_02.wav"),  # About: "Suzume is..." (10-20s)
    (20.0, "tts_03.wav"),  # Capabilities: "Full stack..." (20-32s)
    (32.0, "tts_04.wav"),  # Demos: "Five working demos..." (32-47s)
    (47.0, "tts_05.wav"),  # Process: "Every project..." (47-57s)
    (57.0, "tts_06.wav"),  # Team: "My team includes..." (57-67s)
    (67.0, "tts_07.wav"),  # Finale: "Your vision..." (67-75s)
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
print(f"\nRendering to: {out_path}")
print("(1080p, 75 seconds)")

final.write_videofile(
    out_path,
    codec="libx264",
    audio_codec="aac",
    fps=FPS,
    bitrate="12000k",
    audio_bitrate="320k",
    preset="medium",
    ffmpeg_params=["-pix_fmt", "yuv420p", "-profile:v", "high", "-movflags", "+faststart"],
)

size = os.path.getsize(out_path) / (1024*1024)
print(f"\nOK Video: {out_path}")
print(f"  Size: {size:.1f} MB")
