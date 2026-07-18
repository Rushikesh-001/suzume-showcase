"""
Cinematic Suzume Reel - COMPOSITED RENDER
Uses moviepy composite system: background clips + text ImageClips.
Much faster than frame-by-frame generation.
"""
import os, sys, numpy as np
from PIL import Image, ImageDraw, ImageFont
from moviepy import (
    VideoClip, ImageClip, AudioClip,
    CompositeVideoClip, concatenate_videoclips,
    AudioFileClip, CompositeAudioClip, ColorClip, vfx
)

OUTPUT_DIR = os.path.dirname(os.path.abspath(__file__))
WIDTH, HEIGHT = 1920, 1080
FPS = 30
DURATION = 75

# Fonts
FONT_SEMIBOLD = "C:/Windows/Fonts/seguisb.ttf"
FONT_BOLD = "C:/Windows/Fonts/segoeuib.ttf"
FONT_REG = "C:/Windows/Fonts/segoeui.ttf"
FONT = FONT_SEMIBOLD if os.path.exists(FONT_SEMIBOLD) else FONT_REG if os.path.exists(FONT_REG) else None
print(f"Font: {FONT}")

# ============ FAST BACKGROUNDS (numpy) ============

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


def add_noise(img, amount=5):
    """Add film grain."""
    noise = np.random.normal(0, amount, img.shape)
    return np.clip(img.astype(np.float32) + noise, 0, 255).astype(np.uint8)


def radial_glow(w, h, cx, cy, radius, color, intensity=0.3):
    """Create radial glow overlay."""
    y, x = np.mgrid[0:h, 0:w]
    dist = np.sqrt((x-cx)**2 + (y-cy)**2)
    glow = np.exp(-dist / (radius/3)) * intensity
    return np.clip(glow[:,:,np.newaxis] * np.array(color, dtype=np.float32), 0, 255).astype(np.uint8)


# ============ PRERENDER BACKGROUNDS ============

print("Pre-rendering backgrounds...")
bg_scenes = {}

# Opening
bg = make_bg([(5,5,20), (15,10,35), (8,5,25)], "radial")
bg = add_noise(bg, 6)
glow = radial_glow(WIDTH, HEIGHT, WIDTH//2, HEIGHT//2, 400, (80,40,150), 0.25)
bg = np.clip(bg.astype(np.float32) * 0.75 + glow * 0.25, 0, 255).astype(np.uint8)
Image.fromarray(bg).save(os.path.join(OUTPUT_DIR, "_bg_opening.png"))
bg_scenes["opening"] = True
print("  Opening ✓")

# About
bg = make_bg([(5,5,20), (12,8,32), (10,6,28)], "diagonal")
bg = add_noise(bg, 5)
glow = radial_glow(WIDTH, HEIGHT, 200, HEIGHT//2, 500, (40,60,140), 0.3)
bg = np.clip(bg.astype(np.float32) * 0.7 + glow * 0.3, 0, 255).astype(np.uint8)
Image.fromarray(bg).save(os.path.join(OUTPUT_DIR, "_bg_about.png"))
bg_scenes["about"] = True
print("  About ✓")

# Capabilities
bg = make_bg([(10,5,25), (22,10,38), (5,5,15)], "horizontal")
bg = add_noise(bg, 4)
# Grid
bg[::120,:,:] = np.clip(bg[::120,:,:].astype(np.float32)+15,0,255).astype(np.uint8)
bg[:,::120,:] = np.clip(bg[:,::120,:].astype(np.float32)+15,0,255).astype(np.uint8)
Image.fromarray(bg).save(os.path.join(OUTPUT_DIR, "_bg_caps.png"))
bg_scenes["caps"] = True
print("  Capabilities ✓")

# Design
bg = make_bg([(5,10,25), (10,20,45), (5,8,20)], "diagonal")
bg = add_noise(bg, 5)
glow = radial_glow(WIDTH, HEIGHT, WIDTH//2, HEIGHT-100, 600, (80,40,30), 0.25)
bg = np.clip(bg.astype(np.float32) * 0.75 + glow * 0.25, 0, 255).astype(np.uint8)
Image.fromarray(bg).save(os.path.join(OUTPUT_DIR, "_bg_design.png"))
bg_scenes["design"] = True
print("  Design ✓")

# Finale
bg = make_bg([(15,10,25), (25,15,40), (10,8,20)], "radial")
bg = add_noise(bg, 3)
glow = radial_glow(WIDTH, HEIGHT, WIDTH//2, HEIGHT//2, 300, (200,150,50), 0.4)
bg = np.clip(bg.astype(np.float32) * 0.6 + glow * 0.4, 0, 255).astype(np.uint8)
Image.fromarray(bg).save(os.path.join(OUTPUT_DIR, "_bg_finale.png"))
bg_scenes["finale"] = True
print("  Finale ✓")


# ============ TEXT RENDERER (cached) ============

_text_cache = {}

def render_text(text, font_size=48, color=(245,245,255), shadow_alpha=180,
                max_width=1600, pos="center", font_path=None):
    """Render text to RGBA numpy array (cached)."""
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
    
    # Word wrap
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
        if pos == "center":
            x = (cw-lw)//2
        elif pos == "left":
            x = 20
        else:
            x = cw-lw-20
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
    """Create an ImageClip with text, proper timing."""
    txt = render_text(text, font_size, color, 
                      shadow_alpha=180 if shadow else 0,
                      pos="center" if position[0]=="center" else "left",
                      font_path=font_path)
    
    tw, th = txt.shape[1], txt.shape[0]
    
    # Resolve position to actual (x,y)
    if position[0] == "center":
        x = WIDTH // 2 - tw // 2
    elif isinstance(position[0], (int, float)):
        x = int(position[0])
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
    
    # Crossfade in using opacity manipulation
    if fade_in > 0:
        clip = clip.with_effects([vfx.FadeIn(fade_in)])
    
    return clip


# ============ BUILD COMPOSITE ============

print("\nBuilding composite scenes...")
all_clips = []

# == SCENE 1: Opening (0-10s) ==
bg1 = ImageClip(os.path.join(OUTPUT_DIR, "_bg_opening.png")).with_duration(10)
all_clips.append(bg1)

# SUZUME title
title = make_text_clip("S U Z U M E", 72, (255,195,80), 1.0, 9.0,
                       position=("center", "center"), fade_in=2.0, offset_y=-120,
                       font_path=FONT_BOLD)
all_clips.append(title)

# Subtitle
subtitle = make_text_clip("Beyond Code", 32, (180,180,210), 4.0, 6.0,
                          position=("center", "center"), fade_in=1.5, offset_y=40)
all_clips.append(subtitle)

# == SCENE 2: About (10-20s) ==
bg2 = ImageClip(os.path.join(OUTPUT_DIR, "_bg_about.png")).with_start(10).with_duration(10)
all_clips.append(bg2)

about_texts = [
    ("Suzume is not just artificial intelligence.", 48, (230,220,210), 10.5),
    ("Suzume is a creator.", 44, (255,195,80), 14.0),
    ("A builder.", 44, (80,180,255), 16.5),
    ("An orchestrator of digital worlds.", 38, (230,220,210), 18.5),
]
for text, fs, color, st in about_texts:
    i = about_texts.index((text, fs, color, st))
    clip = make_text_clip(text, fs, color, st, 2.5,
                          position=(120, 200 + i*100), fade_in=1.5,
                          shadow=True)
    all_clips.append(clip)

# == SCENE 3: Capabilities (20-31s) ==
bg3 = ImageClip(os.path.join(OUTPUT_DIR, "_bg_caps.png")).with_start(20).with_duration(11)
all_clips.append(bg3)

caps = [
    ("✦ Full-Stack Engineering", (255,195,80), 20.3),
    ("✦ 3D & Cinematic Visuals", (100,220,255), 21.5),
    ("✦ AI-Powered Automation", (80,180,255), 22.7),
    ("✦ Cross-Platform Systems", (200,155,60), 23.9),
]
for text, color, st in caps:
    i = caps.index((text, color, st))
    clip = make_text_clip(text, 34, color, st, 4.0,
                          position=(150, 200 + i*120), fade_in=1.2,
                          shadow=True)
    all_clips.append(clip)

# == SCENE 4: Design (31-42s) ==
bg4 = ImageClip(os.path.join(OUTPUT_DIR, "_bg_design.png")).with_start(31).with_duration(11)
all_clips.append(bg4)

quotes = [
    ("Every pixel, designed with intention.", 31.5),
    ("Every frame, animated with purpose.", 34.5),
    ("Every line of code, crafted to inspire.", 37.5),
]
for text, st in quotes:
    i = quotes.index((text, st))
    clip = make_text_clip(text, 36, (230,220,210), st, 4.0,
                          position=("center", 250 + i*130), fade_in=1.8,
                          shadow=True)
    all_clips.append(clip)

# == SCENE 5: Finale (42-75s) ==
bg5 = ImageClip(os.path.join(OUTPUT_DIR, "_bg_finale.png")).with_start(42).with_duration(33)
all_clips.append(bg5)

final_title = make_text_clip("S U Z U M E", 72, (255,195,80), 43.0, 32.0,
                             position=("center", "center"), fade_in=2.0, offset_y=-100,
                             font_path=FONT_BOLD)
all_clips.append(final_title)

welcome = make_text_clip("Welcome to the future of creation.", 28, (230,220,210), 45.0, 30.0,
                         position=("center", "center"), fade_in=2.0, offset_y=80)
all_clips.append(welcome)

tagline = make_text_clip("suzume", 24, (160,155,170), 47.0, 28.0,
                         position=("center", "center"), fade_in=2.0, offset_y=150)
all_clips.append(tagline)


# ============ COMPOSITE VIDEO ============

print(f"\nCompositing {len(all_clips)} clips...")
final = CompositeVideoClip(all_clips, size=(WIDTH, HEIGHT))

# Audio
print("Loading audio...")
audio_clips = []

bgm_path = os.path.join(OUTPUT_DIR, "bgm_cinematic.wav")
if os.path.exists(bgm_path):
    bgm = AudioFileClip(bgm_path).with_volume_scaled(0.55)
    audio_clips.append(bgm)

# Tight TTS schedule - gaps reduced to ~0.7s for natural flow
# tts_07 added for finale climax (aligns with BGM climax section 55-70s)
tts_schedule = [
    (1.5, "tts_01.wav"),   # "In a world..." ends ~7.6
    (8.3, "tts_02.wav"),   # "Suzume is not just..." ends ~17.3
    (18.0, "tts_03.wav"),  # "Full stack..." ends ~26.1
    (26.8, "tts_04.wav"),  # "Every pixel..." ends ~35.3
    (36.0, "tts_05.wav"),  # "From concept..." ends ~42.1
    (42.8, "tts_06.wav"),  # "Welcome to the future..." ends ~48.1
    (48.8, "tts_07.wav"),  # "Your vision, brought to life..." ends ~53.0
]
for st, fname in tts_schedule:
    path = os.path.join(OUTPUT_DIR, fname)
    if os.path.exists(path):
        try:
            clip = AudioFileClip(path).with_start(st)
            audio_clips.append(clip)
        except Exception as e:
            print(f"  Error loading TTS {fname}: {e}")

if audio_clips:
    final = final.with_audio(CompositeAudioClip(audio_clips))

# Render!
out_path = os.path.join(OUTPUT_DIR, "suzume_cinematic.mp4")
print(f"\nRendering to: {out_path}")
print("(this takes a few minutes for 1080p 75s)")

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
print(f"\n✓ Video: {out_path}")
print(f"  Size: {size:.1f} MB")
