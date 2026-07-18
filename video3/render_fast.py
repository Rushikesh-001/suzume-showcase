"""
Cinematic Suzume Reel - OPTIMIZED RENDER
Uses numpy vectorized ops + FFmpeg for speed.
"""
import os, sys, json, subprocess, struct, math, asyncio
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from moviepy import (
    VideoClip, ImageClip, AudioClip,
    CompositeVideoClip, concatenate_videoclips,
    AudioFileClip, CompositeAudioClip
)

OUTPUT_DIR = os.path.dirname(os.path.abspath(__file__))
MEDIA_DIR = os.path.dirname(OUTPUT_DIR)  # suzume-showcase/

WIDTH, HEIGHT = 1920, 1080
FPS = 30
DURATION = 75

# Fonts
FONT_SEMIBOLD = "C:/Windows/Fonts/seguisb.ttf"
FONT_BOLD = "C:/Windows/Fonts/segoeuib.ttf"
FONT_REG = "C:/Windows/Fonts/segoeui.ttf"
FONT = FONT_SEMIBOLD if os.path.exists(FONT_SEMIBOLD) else FONT_REG if os.path.exists(FONT_REG) else None

print(f"Font: {FONT}")

# ============ NUMPY FAST GRADIENT ============

def fast_gradient(w, h, colors, direction="radial"):
    """Create gradient using numpy (1000x faster than PIL pixel loop)."""
    y, x = np.mgrid[0:h, 0:w]
    
    if direction == "radial":
        cx, cy = w / 2, h / 2
        t = np.sqrt((x - cx)**2 + (y - cy)**2)
        t = t / np.sqrt(cx**2 + cy**2)
    elif direction == "horizontal":
        t = x / w
    elif direction == "vertical":
        t = y / h
    elif direction == "diagonal":
        t = (x + y) / (w + h)
    else:
        t = np.zeros((h, w))
    
    t = np.clip(t, 0, 1)
    
    # Interpolate between colors
    n_colors = len(colors)
    if n_colors == 2:
        c1, c2 = np.array(colors[0]), np.array(colors[1])
        result = c1 + (c2 - c1) * t[:, :, np.newaxis]
    else:
        # Multi-stop gradient
        result = np.zeros((h, w, 3))
        for i in range(n_colors - 1):
            c1, c2 = np.array(colors[i]), np.array(colors[i+1])
            pos = i / (n_colors - 1)
            next_pos = (i + 1) / (n_colors - 1)
            mask = (t >= pos) & (t <= next_pos)
            local_t = (t[mask] - pos) / (next_pos - pos)
            result[mask] = c1 + (c2 - c1) * local_t[:, np.newaxis]
    
    return np.clip(result, 0, 255).astype(np.uint8)


def fast_noise(img, amount=8):
    """Add film grain using numpy."""
    noise = np.random.normal(0, amount, img.shape)
    return np.clip(img.astype(np.float32) + noise, 0, 255).astype(np.uint8)


def fast_bloom(img, intensity=0.3):
    """Simple bloom via PIL GaussianBlur."""
    pil = Image.fromarray(img)
    blurred = pil.filter(ImageFilter.GaussianBlur(15))
    blended = Image.blend(pil, blurred, intensity)
    return np.array(blended)


# Text cache - huge speedup since same text is rendered many times
_text_cache = {}

def create_text_overlay(text, font_size=48, color=(245,245,255), 
                         shadow_alpha=180, max_width=1600, pos="center",
                         font_path=None):
    """Create text as RGBA numpy array for compositing (cached)."""
    cache_key = (text, font_size, color, shadow_alpha, max_width, pos, font_path)
    if cache_key in _text_cache:
        return _text_cache[cache_key].copy()
    
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
    current = ""
    for word in words:
        test = current + " " + word if current else word
        bbox = font.getbbox(test)
        if bbox and (bbox[2] - bbox[0]) > max_width and current:
            lines.append(current)
            current = word
        else:
            current = test
    if current:
        lines.append(current)
    
    # Calculate dimensions
    line_h = 0
    for line in lines:
        bbox = font.getbbox(line)
        line_h = max(line_h, bbox[3] - bbox[1])
    
    spacing = int(line_h * 0.3)
    total_h = len(lines) * line_h + (len(lines) - 1) * spacing + 40
    max_w = 0
    for line in lines:
        bbox = font.getbbox(line)
        max_w = max(max_w, bbox[2] - bbox[0])
    
    canvas_w = min(max_w + 80, max_width)
    canvas_h = total_h + 20
    
    pil_img = Image.new("RGBA", (canvas_w, canvas_h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(pil_img)
    
    for i, line in enumerate(lines):
        bbox = font.getbbox(line)
        lw = bbox[2] - bbox[0]
        if pos == "center":
            x = (canvas_w - lw) // 2
        elif pos == "left":
            x = 20
        else:
            x = canvas_w - lw - 20
        
        y = 10 + i * (line_h + spacing)
        
        if shadow_alpha > 0:
            draw.text((x + 2, y + 2), line, font=font, fill=(0, 0, 0, shadow_alpha))
        draw.text((x, y), line, font=font, fill=(*color, 255))
    
    result = np.array(pil_img)
    _text_cache[cache_key] = result.copy()
    return result


def paste_text(bg, text_img, x, y, alpha=1.0):
    """Composite text RGBA onto background RGB."""
    h, w = text_img.shape[:2]
    if alpha < 1.0:
        text_img = text_img.copy()
        text_img[:, :, 3] = (text_img[:, :, 3] * alpha).astype(np.uint8)
    
    # Ensure within bounds
    y1, y2 = y, min(y + h, bg.shape[0])
    x1, x2 = x, min(x + w, bg.shape[1])
    th = y2 - y1
    tw = x2 - x1
    
    if th <= 0 or tw <= 0:
        return bg
    
    rgb = text_img[:th, :tw, :3]
    a = text_img[:th, :tw, 3:4] / 255.0
    
    bg[y1:y2, x1:x2] = (bg[y1:y2, x1:x2] * (1 - a) + rgb * a).astype(np.uint8)
    return bg


# ============ BACKGROUND PRE-RENDERING ============

bg_cache = {}

def get_bg(name, colors, direction="radial"):
    """Get or create cached background."""
    key = (name, tuple(tuple(c) for c in colors), direction)
    if key not in bg_cache:
        bg_cache[key] = fast_gradient(WIDTH, HEIGHT, colors, direction)
    return bg_cache[key].copy()


def add_glow_overlay(bg, center_x, center_y, radius, color, alpha=0.3):
    """Add a radial glow using numpy."""
    y, x = np.mgrid[0:bg.shape[0], 0:bg.shape[1]]
    dist = np.sqrt((x - center_x)**2 + (y - center_y)**2)
    glow = np.exp(-dist / (radius / 3)) * alpha
    glow = np.clip(glow, 0, 1)
    c = np.array(color, dtype=np.float32)
    bg_float = bg.astype(np.float32)
    blended = bg_float * (1 - glow[:, :, np.newaxis]) + c * glow[:, :, np.newaxis]
    return np.clip(blended, 0, 255).astype(np.uint8)


# ============ SCENE FRAME GENERATORS ============

def scene_opening(t, scene):
    """Opening: Mysterious reveal with SUZUME title."""
    local_t = t - scene["start"]
    
    bg = get_bg("opening", 
        [(5, 5, 20), (15, 10, 35), (8, 5, 25)],
        "radial")
    bg = fast_noise(bg, 6)
    bg = add_glow_overlay(bg, WIDTH//2, HEIGHT//2, 400, (80, 40, 150), 0.25)
    
    # Title reveal
    progress = min(1.0, local_t / 3.0)
    title_alpha = int(255 * progress)
    
    if title_alpha > 0:
        # "S U Z U M E"
        title = create_text_overlay("S U Z U M E", 72, (255, 195, 80), 
                                     shadow_alpha=180, font_path=FONT_BOLD)
        tx = (WIDTH - title.shape[1]) // 2
        ty = HEIGHT // 2 - 120
        bg = paste_text(bg, title, tx, ty, alpha=progress)
        
        # Subtitle
        sub_progress = max(0, min(1.0, (local_t - 3.0) / 2.0))
        if sub_progress > 0:
            sub = create_text_overlay("Beyond Code", 32, (180, 180, 210),
                                      shadow_alpha=120)
            sx = (WIDTH - sub.shape[1]) // 2
            sy = ty + 100
            bg = paste_text(bg, sub, sx, sy, alpha=sub_progress)
    
    # Floating particles (perlin-like simple)
    np.random.seed(int(t * 10) % 1000)
    particles = np.random.rand(50, 2)
    particles[:, 0] = (particles[:, 0] * WIDTH + t * 20) % WIDTH
    particles[:, 1] = (particles[:, 1] * HEIGHT + t * 5) % HEIGHT
    
    for p in particles:
        px, py = int(p[0]), int(p[1])
        if 5 < px < WIDTH-5 and 5 < py < HEIGHT-5:
            alpha = int(80 + 60 * np.sin(t * 0.5 + px * 0.01))
            bg[py-2:py+3, px-2:px+3] = np.clip(
                bg[py-2:py+3, px-2:px+3].astype(np.float32) + 
                np.array([[[255, 200, 100]]]) * 0.3, 0, 255).astype(np.uint8)
    
    return bg


def scene_about(t, scene):
    """About Suzume with animated text."""
    local_t = t - scene["start"]
    
    bg = get_bg("about", [(5, 5, 20), (12, 8, 32), (10, 6, 28)], "diagonal")
    bg = fast_noise(bg, 5)
    bg = add_glow_overlay(bg, 200, HEIGHT//2, 500, (40, 60, 140), 0.3)
    
    texts = [
        ("Suzume is not just artificial intelligence.", 0.5, 48, (230, 220, 210)),
        ("Suzume is a creator.", 4.0, 44, (255, 195, 80)),
        ("A builder.", 6.5, 44, (80, 180, 255)),
        ("An orchestrator of digital worlds.", 8.5, 38, (230, 220, 210)),
    ]
    
    for text_str, start_t, fs, color in texts:
        p = max(0, min(1.0, (local_t - start_t) / 1.5))
        if p <= 0:
            continue
        offset_x = int(80 * (1 - p))
        
        txt = create_text_overlay(text_str, fs, color, shadow_alpha=150,
                                   max_width=1400, pos="left")
        x = 120 + offset_x
        y = 200 + texts.index((text_str, start_t, fs, color)) * 100
        bg = paste_text(bg, txt, x, y, alpha=p)
    
    return bg


def scene_capabilities(t, scene):
    """Capabilities showcase."""
    local_t = t - scene["start"]
    
    bg = get_bg("caps", [(10, 5, 25), (22, 10, 38), (5, 5, 15)], "horizontal")
    bg = fast_noise(bg, 4)
    
    # Subtle grid
    bg[::120, :, :] = np.clip(bg[::120, :, :].astype(np.float32) + 15, 0, 255).astype(np.uint8)
    bg[:, ::120, :] = np.clip(bg[:, ::120, :].astype(np.float32) + 15, 0, 255).astype(np.uint8)
    
    caps = [
        ("✦ Full-Stack Engineering", 0.3, (255, 195, 80)),
        ("✦ 3D & Cinematic Visuals", 1.5, (100, 220, 255)),
        ("✦ AI-Powered Automation", 2.7, (80, 180, 255)),
        ("✦ Cross-Platform Systems", 3.9, (200, 155, 60)),
    ]
    
    for text_str, start_t, color in caps:
        p = max(0, min(1.0, (local_t - start_t) / 1.2))
        if p <= 0:
            continue
        
        txt = create_text_overlay(text_str, 34, color, shadow_alpha=140,
                                   max_width=800, pos="left")
        x = 150
        y = 200 + caps.index((text_str, start_t, color)) * 120
        bg = paste_text(bg, txt, x, y, alpha=p)
        
        # Decorative line
        if p > 0:
            line_len = int(min(txt.shape[1], 300 * p))
            line_color = np.array([*color, 180], dtype=np.uint8)
            line_y = y + txt.shape[0] + 10
            if line_y < HEIGHT:
                bg[line_y, x:x+line_len, :] = np.clip(
                    bg[line_y, x:x+line_len, :].astype(np.float32) * 0.5 + 
                    np.array(color, dtype=np.float32) * 0.5, 0, 255).astype(np.uint8)
    
    return bg


def scene_design(t, scene):
    """Design philosophy."""
    local_t = t - scene["start"]
    
    bg = get_bg("design", [(5, 10, 25), (10, 20, 45), (5, 8, 20)], "diagonal")
    bg = fast_noise(bg, 5)
    bg = add_glow_overlay(bg, WIDTH//2, HEIGHT-100, 600, (80, 40, 30), 0.25)
    
    quotes = [
        "Every pixel, designed with intention.",
        "Every frame, animated with purpose.",
        "Every line of code, crafted to inspire.",
    ]
    
    for i, quote in enumerate(quotes):
        start_t = 0.5 + i * 3.0
        p = max(0, min(1.0, (local_t - start_t) / 1.8))
        if p <= 0:
            continue
        
        offset_y = int(30 * (1 - p))
        txt = create_text_overlay(quote, 36, (230, 220, 210), shadow_alpha=150,
                                   max_width=1600, pos="center")
        tx = (WIDTH - txt.shape[1]) // 2
        ty = 250 + i * 130 + offset_y
        bg = paste_text(bg, txt, tx, ty, alpha=p)
    
    return bg


def scene_finale(t, scene):
    """Finale: Emotional climax."""
    local_t = t - scene["start"]
    
    bg = get_bg("finale", [(15, 10, 25), (25, 15, 40), (10, 8, 20)], "radial")
    bg = fast_noise(bg, 3)
    bg = add_glow_overlay(bg, WIDTH//2, HEIGHT//2, 300, (200, 150, 50), 0.4)
    
    progress = min(1.0, local_t / 2.0)
    
    if progress > 0:
        # SUZUME title
        pulse = 1.0 + 0.02 * np.sin(t * 0.5)
        title = create_text_overlay("S U Z U M E", int(72 * pulse), (255, 195, 80),
                                     shadow_alpha=180, font_path=FONT_BOLD)
        tx = (WIDTH - title.shape[1]) // 2
        ty = HEIGHT // 2 - 100
        bg = paste_text(bg, title, tx, ty, alpha=progress)
        
        # Tagline
        sub_progress = max(0, min(1.0, (local_t - 1.5) / 2.0))
        if sub_progress > 0:
            sub = create_text_overlay("Welcome to the future of creation.",
                                      28, (230, 220, 210), shadow_alpha=120)
            sx = (WIDTH - sub.shape[1]) // 2
            sy = ty + 120
            bg = paste_text(bg, sub, sx, sy, alpha=sub_progress)
            
            tag = create_text_overlay("suzume", 24, (160, 155, 170),
                                       shadow_alpha=80)
            tgx = (WIDTH - tag.shape[1]) // 2
            tgy = sy + 60
            bg = paste_text(bg, tag, tgx, tgy, alpha=sub_progress)
    
    return bg


# ============ MAIN RENDER ============

def render_full():
    print("=" * 60)
    print("SUZUME CINEMATIC REEL - OPTIMIZED RENDER")
    print("=" * 60)
    
    scenes = [
        ("Opening", scene_opening, 0, 10),
        ("About", scene_about, 10, 20),
        ("Capabilities", scene_capabilities, 20, 31),
        ("Design", scene_design, 31, 42),
        ("Finale", scene_finale, 42, DURATION),
    ]
    
    scenes_data = [
        {"name": n, "start": s, "end": e, "generator": g}
        for n, g, s, e in scenes
    ]
    
    print(f"Duration: {DURATION}s @ {FPS}fps = {DURATION * FPS} frames")
    print(f"Resolution: {WIDTH}x{HEIGHT}")
    print(f"Scenes: {len(scenes)}")
    print()
    
    def make_frame(t):
        for sc in scenes_data:
            if sc["start"] <= t < sc["end"]:
                return sc["generator"](t, sc)
        return fast_gradient(WIDTH, HEIGHT, [(5,5,20), (10,8,30)])
    
    print("Creating VideoClip...")
    video = VideoClip(make_frame, duration=DURATION).with_fps(FPS)
    
    # Audio
    print("Loading audio...")
    audio_clips = []
    
    bgm_path = os.path.join(OUTPUT_DIR, "bgm_cinematic.wav")
    if os.path.exists(bgm_path):
        bgm = AudioFileClip(bgm_path).with_volume_scaled(0.30)
        audio_clips.append(bgm)
        print(f"  BGM: {bgm.duration:.1f}s")
    
    tts_times = [
        (1.5, "tts_01.wav"),
        (11.0, "tts_02.wav"),
        (21.0, "tts_03.wav"),
        (31.0, "tts_04.wav"),
        (41.0, "tts_05.wav"),
        (52.0, "tts_06.wav"),
    ]
    
    for start_t, fname in tts_times:
        path = os.path.join(OUTPUT_DIR, fname)
        if os.path.exists(path):
            try:
                clip = AudioFileClip(path).with_start(start_t)
                audio_clips.append(clip)
                print(f"  TTS {fname}: @{start_t}s")
            except Exception as e:
                print(f"  Error: {e}")
    
    if audio_clips:
        final_audio = CompositeAudioClip(audio_clips)
        video = video.with_audio(final_audio)
    
    out_path = os.path.join(OUTPUT_DIR, "suzume_cinematic.mp4")
    print(f"\nRendering to: {out_path}")
    print("(this may take a few minutes...)\n")
    
    video.write_videofile(
        out_path,
        codec="libx264",
        audio_codec="aac",
        fps=FPS,
        bitrate="15000k",
        audio_bitrate="320k",
        preset="medium",
        ffmpeg_params=[
            "-pix_fmt", "yuv420p",
            "-profile:v", "high",
            "-movflags", "+faststart",
        ],
        logger=None  # Suppress output for cleaner logs
    )
    
    size = os.path.getsize(out_path) / (1024*1024)
    print(f"\n✓ Video: {out_path}")
    print(f"  Size: {size:.1f} MB")
    
    return out_path


if __name__ == "__main__":
    render_full()
