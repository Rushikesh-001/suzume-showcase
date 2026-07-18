"""
Cinematic Suzume Reel Generator
Creates a goosebumps-inducing cinematic video with:
- Animated text overlays
- Gradient backgrounds with parallax
- Smooth transitions
- TTS voiceover + BGM mixing
- Instagram-style vertical (or 16:9) format
"""
import os
import sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import moviepy as mp
from moviepy import (
    VideoClip, ImageClip, AudioClip, 
    CompositeVideoClip, concatenate_videoclips,
    AudioFileClip, CompositeAudioClip
)
import asyncio
import subprocess
import json

OUTPUT_DIR = os.path.dirname(os.path.abspath(__file__))
WIDTH, HEIGHT = 1920, 1080
FPS = 30
DURATION = 75  # 75 seconds total

# Font setup - use a good modern font
FONT_PATH = None
# Try common Windows fonts
potential_fonts = [
    "C:/Windows/Fonts/consolab.ttf",  # Consolas Bold
    "C:/Windows/Fonts/CALIBRIB.TTF",  # Calibri Bold
    "C:/Windows/Fonts/segoeuib.ttf",   # Segoe UI Bold
    "C:/Windows/Fonts/segoeui.ttf",    # Segoe UI
    "C:/Windows/Fonts/arialbd.ttf",    # Arial Bold
    "C:/Windows/Fonts/ARIAL.TTF",       # Arial
    "C:/Windows/Fonts/BRADHITC.TTF",   # Bradley Hand (for style)
]
for f in potential_fonts:
    if os.path.exists(f):
        FONT_PATH = f
        break

print(f"Using font: {FONT_PATH}")

# Color palette - cinematic dark + warm gold + cool blue
COLORS = {
    "bg_dark": (5, 5, 15),
    "bg_mid": (10, 8, 25),
    "accent_gold": (255, 195, 80),
    "accent_gold_dim": (200, 155, 60),
    "accent_blue": (80, 180, 255),
    "accent_cyan": (100, 220, 255),
    "text_white": (245, 245, 255),
    "text_warm": (230, 220, 210),
    "text_dim": (160, 155, 170),
    "glow_purple": (120, 60, 200),
    "glow_teal": (30, 180, 200),
}


def make_gradient_frame(w, h, colors, direction="horizontal"):
    """Create a smooth gradient background."""
    img = Image.new("RGB", (w, h))
    pixels = img.load()
    for y in range(h):
        for x in range(w):
            if direction == "horizontal":
                t = x / w
            elif direction == "vertical":
                t = y / h
            elif direction == "diagonal":
                t = (x + y) / (w + h)
            elif direction == "radial":
                cx, cy = w//2, h//2
                t = min(1.0, ((x-cx)**2 + (y-cy)**2)**0.5 / ((w//2)**2 + (h//2)**2)**0.5)
            else:
                t = 0
            
            # Interpolate between colors
            if t < 0.5:
                t2 = t * 2
                c1, c2 = colors[0], colors[1]
            else:
                t2 = (t - 0.5) * 2
                c1, c2 = colors[1], colors[2] if len(colors) > 2 else colors[1]
            
            r = int(c1[0] + (c2[0] - c1[0]) * t2)
            g = int(c1[1] + (c2[1] - c1[1]) * t2)
            b = int(c1[2] + (c2[2] - c1[2]) * t2)
            pixels[x, y] = (min(255, r), min(255, g), min(255, b))
    return img


def add_noise(img, amount=15):
    """Add subtle film grain."""
    arr = np.array(img, dtype=np.float32)
    noise = np.random.normal(0, amount, arr.shape)
    arr = np.clip(arr + noise, 0, 255).astype(np.uint8)
    return Image.fromarray(arr)


def add_glow(img, radius=20):
    """Add a bloom/glow effect."""
    blurred = img.filter(ImageFilter.GaussianBlur(radius))
    # Blend original with blurred glow
    return Image.blend(img, blurred, 0.3)


def create_text_image(text, font_size=48, color=COLORS["text_white"], 
                       shadow=True, glow=False, max_width=1600,
                       align="center", font_path=None, bold=False):
    """Render text to PIL image with effects."""
    font_path = font_path or FONT_PATH
    if font_path:
        try:
            font = ImageFont.truetype(font_path, font_size)
        except:
            font = ImageFont.load_default()
    else:
        font = ImageFont.load_default()
    
    # Measure text
    bbox = font.getbbox(text)
    text_w = bbox[2] - bbox[0]
    text_h = bbox[3] - bbox[1]
    
    # Handle multiline
    if text_w > max_width:
        # Simple word wrap
        words = text.split(" ")
        lines = []
        current_line = ""
        for word in words:
            test_line = current_line + " " + word if current_line else word
            bbox = font.getbbox(test_line)
            tw = bbox[2] - bbox[0]
            if tw > max_width and current_line:
                lines.append(current_line)
                current_line = word
            else:
                current_line = test_line
        if current_line:
            lines.append(current_line)
    else:
        lines = [text]
    
    # Calculate dimensions
    line_height = int(text_h * 1.5)
    total_h = len(lines) * line_height + 20
    max_line_w = 0
    for line in lines:
        bbox = font.getbbox(line)
        max_line_w = max(max_line_w, bbox[2] - bbox[0])
    
    img_w = min(max_line_w + 80, max_width)
    img_h = total_h + 40
    
    img = Image.new("RGBA", (img_w, img_h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    for i, line in enumerate(lines):
        y_pos = 20 + i * line_height
        if align == "center":
            bbox = font.getbbox(line)
            lw = bbox[2] - bbox[0]
            x_pos = (img_w - lw) // 2
        elif align == "left":
            x_pos = 20
        else:
            bbox = font.getbbox(line)
            lw = bbox[2] - bbox[0]
            x_pos = img_w - lw - 20
        
        if shadow:
            draw.text((x_pos + 3, y_pos + 3), line, font=font, fill=(0, 0, 0, 180))
        if glow:
            for dx, dy in [(0,0), (1,0), (-1,0), (0,1), (0,-1)]:
                draw.text((x_pos + dx*2, y_pos + dy*2), line, font=font, fill=(*color[:3], 80))
        
        draw.text((x_pos, y_pos), line, font=font, fill=color)
    
    return img


def create_particle_frame(w, h, t, color_center=(255, 195, 80), 
                           color_edge=(80, 180, 255), num_particles=80):
    """Create a frame with floating particles."""
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    np.random.seed(42)
    particles = []
    for i in range(num_particles):
        px = np.random.rand() * w
        py = np.random.rand() * h
        ps = 1 + np.random.rand() * 4  # size
        pspeed = 0.1 + np.random.rand() * 0.3
        pangle = np.random.rand() * 2 * np.pi
        particles.append([px, py, ps, pspeed, pangle])
    
    for p in particles:
        px, py, ps, pspeed, pangle = p
        # Movement
        px += np.cos(pangle + t * 0.2) * pspeed
        py += np.sin(pangle + t * 0.15) * pspeed * 0.5
        # Wrap around
        px = px % w
        py = py % h
        
        # Color gradient based on position
        dist = ((px - w/2)**2 + (py - h/2)**2)**0.5 / ((w/2)**2 + (h/2)**2)**0.5
        r = int(color_center[0] + (color_edge[0] - color_center[0]) * dist)
        g = int(color_center[1] + (color_edge[1] - color_center[1]) * dist)
        b = int(color_center[2] + (color_edge[2] - color_center[2]) * dist)
        
        # Opacity pulse
        alpha = int(150 + 105 * np.sin(t * 0.5 + i))
        alpha = max(0, min(255, alpha))
        
        draw.ellipse([px-ps, py-ps, px+ps, py+ps], fill=(r, g, b, alpha))
    
    return img


def create_cinematic_frame(t, scenes_data):
    """Main frame generator - called by moviepy for each frame."""
    # Determine which scene we're in
    for scene in scenes_data:
        if scene["start"] <= t < scene["end"]:
            return scene["generator"](t, scene)
    
    # Fallback
    img = Image.new("RGB", (WIDTH, HEIGHT), COLORS["bg_dark"])
    return np.array(img)


# ==================== SCENE GENERATORS ====================

def scene_01_opening(t, scene):
    """Opening: Mysterious title reveal with particles."""
    local_t = t - scene["start"]
    dur = scene["end"] - scene["start"]
    
    # Gradient background
    img = make_gradient_frame(WIDTH, HEIGHT, 
        [COLORS["bg_dark"], (15, 10, 30), (5, 5, 20)],
        "radial")
    
    # Add film grain
    img = add_noise(img, 8)
    
    # Add glow in center
    glow = Image.new("RGB", (WIDTH, HEIGHT), (0, 0, 0))
    draw_glow = ImageDraw.Draw(glow)
    for r in range(100, 0, -5):
        alpha = int(3 * (1 - r/100))
        draw_glow.ellipse([WIDTH//2 - r*3, HEIGHT//2 - r*2, 
                          WIDTH//2 + r*3, HEIGHT//2 + r*2], 
                         fill=(60, 30, 100, alpha))
    glow = glow.filter(ImageFilter.GaussianBlur(20))
    img = Image.blend(img, glow, 0.3)
    
    # Convert to RGBA for compositing
    img = img.convert("RGBA")
    
    # Particles overlay
    particles = create_particle_frame(WIDTH, HEIGHT, t, 
        (255, 195, 80), (80, 180, 255), 60)
    img = Image.alpha_composite(img, particles)
    
    # "SUZUME" title - fade in with glow
    progress = min(1.0, local_t / 3.0)
    alpha = int(255 * progress)
    
    title_font_size = 80
    try:
        title_font = ImageFont.truetype(FONT_PATH, title_font_size) if FONT_PATH else ImageFont.load_default()
    except:
        title_font = ImageFont.load_default()
    
    # Title background glow
    glow_radius = int(30 * (1 + 0.5 * np.sin(t * 0.3)))
    glow_layer = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    draw = ImageDraw.Draw(glow_layer)
    
    # Draw "S U Z U M E" with letter spacing
    title_text = "S U Z U M E"
    bbox = title_font.getbbox(title_text)
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]
    tx = (WIDTH - tw) // 2
    ty = HEIGHT // 2 - 120
    
    if progress > 0:
        # Glow behind text
        glow_color = (255, 195, 80, int(60 * alpha / 255))
        for dx, dy in [(0,0), (3,0), (-3,0), (0,3), (0,-3), (5,0), (-5,0)]:
            draw.text((tx + dx + glow_radius, ty + dy + glow_radius), 
                     title_text, font=title_font, fill=glow_color)
        
        # Main text
        gold_color = (255, 195, 80, alpha)
        draw.text((tx + glow_radius, ty + glow_radius), title_text, font=title_font, fill=gold_color)
    
    # Subtitle
    sub_progress = max(0, min(1.0, (local_t - 2.0) / 2.0))
    sub_alpha = int(255 * sub_progress)
    if sub_alpha > 0:
        sub_text = "Beyond Code"
        sub_font_size = 32
        try:
            sub_font = ImageFont.truetype(FONT_PATH, sub_font_size) if FONT_PATH else ImageFont.load_default()
        except:
            sub_font = ImageFont.load_default()
        bbox = sub_font.getbbox(sub_text)
        stw = bbox[2] - bbox[0]
        sx = (WIDTH - stw) // 2
        sy = ty + th + 40
        draw.text((sx, sy), sub_text, font=sub_font, fill=(180, 180, 200, sub_alpha))
    
    img = Image.alpha_composite(img, glow_layer)
    return np.array(img)[:, :, :3]  # Return RGB


def scene_02_about(t, scene):
    """About Suzume with animated text reveals."""
    local_t = t - scene["start"]
    dur = scene["end"] - scene["start"]
    
    # Dark cinematic background with blue undertones
    img = make_gradient_frame(WIDTH, HEIGHT,
        [(5, 5, 20), (10, 8, 30), (8, 5, 25)],
        "diagonal")
    img = add_noise(img, 6)
    
    # Side glow
    glow = Image.new("RGB", (WIDTH, HEIGHT), (0, 0, 0))
    draw = ImageDraw.Draw(glow)
    draw.ellipse([-200, 0, 600, HEIGHT], fill=(40, 60, 120, 30))
    glow = glow.filter(ImageFilter.GaussianBlur(40))
    img = Image.blend(img, glow, 0.4)
    
    img = img.convert("RGBA")
    
    # Text animations
    texts = [
        ("Suzume is not just artificial intelligence.", 0.5, 48, COLORS["text_warm"]),
        ("Suzume is a creator.", 4.0, 44, COLORS["accent_gold"]),
        ("A builder.", 6.5, 44, COLORS["accent_blue"]),
        ("An orchestrator of digital worlds.", 8.5, 38, COLORS["text_warm"]),
    ]
    
    overlay = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    
    for text, start_t, font_size, color in texts:
        p = max(0, min(1.0, (local_t - start_t) / 1.5))
        if p <= 0:
            continue
        
        alpha = int(255 * p)
        # Slide in from left
        offset_x = int(80 * (1 - p))
        
        try:
            font = ImageFont.truetype(FONT_PATH, font_size) if FONT_PATH else ImageFont.load_default()
        except:
            font = ImageFont.load_default()
        
        bbox = font.getbbox(text)
        tw = bbox[2] - bbox[0]
        th = bbox[3] - bbox[1]
        
        x = 120 + offset_x
        y = 180 + texts.index((text, start_t, font_size, color)) * 100
        
        # Shadow
        draw.text((x + 2, y + 2), text, font=font, fill=(0, 0, 0, alpha))
        # Text
        draw.text((x, y), text, font=font, fill=(*color, alpha))
    
    img = Image.alpha_composite(img, overlay)
    return np.array(img)[:, :, :3]


def scene_03_capabilities(t, scene):
    """Showcase capabilities with visual effects."""
    local_t = t - scene["start"]
    dur = scene["end"] - scene["start"]
    
    # Dark background with purple/gold gradient
    img = make_gradient_frame(WIDTH, HEIGHT,
        [(10, 5, 25), (20, 10, 35), (5, 5, 15)],
        "horizontal")
    img = add_noise(img, 5)
    
    # Add subtle grid lines
    draw_grid = ImageDraw.Draw(img)
    for i in range(0, WIDTH, 120):
        if i % 240 == 0:
            draw_grid.line([(i, 0), (i, HEIGHT)], fill=(40, 30, 60, 20), width=1)
    for i in range(0, HEIGHT, 120):
        if i % 240 == 0:
            draw_grid.line([(0, i), (WIDTH, i)], fill=(40, 30, 60, 20), width=1)
    
    img = img.convert("RGBA")
    overlay = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    
    # Capability items with staggered animation
    capabilities = [
        ("✦ Full-Stack Engineering", 0.3, COLORS["accent_gold"]),
        ("✦ 3D & Cinematic Visuals", 1.5, COLORS["accent_cyan"]),
        ("✦ AI-Powered Automation", 2.7, COLORS["accent_blue"]),
        ("✦ Cross-Platform Systems", 3.9, COLORS["accent_gold_dim"]),
    ]
    
    for text, start_t, color in capabilities:
        p = max(0, min(1.0, (local_t - start_t) / 1.2))
        if p <= 0:
            continue
        
        alpha = int(255 * p)
        try:
            font = ImageFont.truetype(FONT_PATH, 34) if FONT_PATH else ImageFont.load_default()
        except:
            font = ImageFont.load_default()
        
        bbox = font.getbbox(text)
        tw = bbox[2] - bbox[0]
        th = bbox[3] - bbox[1]
        x = 150
        y = 200 + capabilities.index((text, start_t, color)) * 120
        
        # Glow on reveal
        if p < 0.5:
            glow_alpha = int(80 * (1 - p * 2))
            for dx, dy in [(0,0), (2,0), (-2,0), (0,2), (0,-2)]:
                draw.text((x + dx, y + dy), text, font=font, 
                         fill=(*color[:3], glow_alpha))
        
        # Shadow
        draw.text((x + 2, y + 2), text, font=font, fill=(0, 0, 0, alpha))
        # Main text
        draw.text((x, y), text, font=font, fill=(*color, alpha))
        
        # Decorative line
        line_alpha = int(180 * p)
        draw.line([(x, y + th + 10), (x + min(tw, 300 * p), y + th + 10)], 
                  fill=(*color[:3], line_alpha), width=2)
    
    # Right side decorative element
    center_x, center_y = WIDTH - 300, HEIGHT // 2
    for r in range(200, 50, -15):
        c_alpha = int(8 + 4 * np.sin(t * 0.3 + r * 0.1))
        draw.ellipse([center_x - r, center_y - r, center_x + r, center_y + r],
                    outline=(60, 40, 100, c_alpha), width=1)
    
    img = Image.alpha_composite(img, overlay)
    return np.array(img)[:, :, :3]


def scene_04_design(t, scene):
    """Design philosophy - cinematic sequence."""
    local_t = t - scene["start"]
    dur = scene["end"] - scene["start"]
    
    # Blue/teal gradient background
    img = make_gradient_frame(WIDTH, HEIGHT,
        [(5, 10, 25), (10, 20, 40), (5, 8, 20)],
        "diagonal")
    img = add_noise(img, 7)
    
    # Warm glow from bottom
    glow = Image.new("RGB", (WIDTH, HEIGHT), (0, 0, 0))
    draw = ImageDraw.Draw(glow)
    draw.ellipse([-400, HEIGHT//2, WIDTH+400, HEIGHT+200], fill=(80, 40, 30, 40))
    glow = glow.filter(ImageFilter.GaussianBlur(60))
    img = Image.blend(img, glow, 0.3)
    
    img = img.convert("RGBA")
    overlay = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    
    # Central quote
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
        
        alpha = int(255 * p)
        try:
            font = ImageFont.truetype(FONT_PATH, 36) if FONT_PATH else ImageFont.load_default()
        except:
            font = ImageFont.load_default()
        
        bbox = font.getbbox(quote)
        tw = bbox[2] - bbox[0]
        x = (WIDTH - tw) // 2
        y = 250 + i * 130
        
        # Fade up with slight scale
        offset_y = int(30 * (1 - p))
        
        # Text glow
        if p < 0.4:
            glow_a = int(60 * (1 - p / 0.4))
            for dx, dy in [(0,0), (3,0), (-3,0), (0,3), (0,-3)]:
                draw.text((x + dx, y + offset_y + dy), quote, font=font,
                         fill=(200, 200, 255, glow_a))
        
        # Shadow
        draw.text((x + 2, y + offset_y + 2), quote, font=font, fill=(0, 0, 0, alpha))
        # Text
        draw.text((x, y + offset_y), quote, font=font, fill=(*COLORS["text_warm"], alpha))
    
    # Bottom accent line with pulse
    line_progress = max(0, min(1.0, (local_t) / 2.0))
    if line_progress > 0:
        line_alpha = int(150 * line_progress)
        line_x = int(WIDTH * 0.3 * (1 - line_progress) + WIDTH * 0.1)
        draw.line([(line_x, 680), (WIDTH - 200, 680)], 
                  fill=(*COLORS["accent_gold"], line_alpha), width=2)
    
    img = Image.alpha_composite(img, overlay)
    return np.array(img)[:, :, :3]


def scene_05_finale(t, scene):
    """Finale: Emotional climax with SUZUME logo."""
    local_t = t - scene["start"]
    dur = scene["end"] - scene["start"]
    
    # Warm golden background
    img = make_gradient_frame(WIDTH, HEIGHT,
        [(15, 10, 25), (25, 15, 35), (10, 8, 20)],
        "radial")
    img = add_noise(img, 4)
    
    # Golden glow in center
    glow = Image.new("RGB", (WIDTH, HEIGHT), (0, 0, 0))
    draw = ImageDraw.Draw(glow)
    for r in range(200, 0, -10):
        alpha = int(5 * (1 - r/200))
        draw.ellipse([WIDTH//2 - r*2, HEIGHT//2 - r*2, 
                     WIDTH//2 + r*2, HEIGHT//2 + r*2],
                    fill=(200, 150, 50, alpha))
    glow = glow.filter(ImageFilter.GaussianBlur(30))
    img = Image.blend(img, glow, 0.5)
    
    img = img.convert("RGBA")
    overlay = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    
    # "SUZUME" large title
    title_font_size = 72
    try:
        title_font = ImageFont.truetype(FONT_PATH, title_font_size) if FONT_PATH else ImageFont.load_default()
    except:
        title_font = ImageFont.load_default()
    
    # Pulse effect
    pulse = 1.0 + 0.03 * np.sin(t * 0.5)
    
    title = "S U Z U M E"
    bbox = title_font.getbbox(title)
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]
    tx = (WIDTH - tw) // 2
    ty = HEIGHT // 2 - 100
    
    # Progress: 0 at start, 1 at end (stays visible)
    progress = min(1.0, local_t / 2.0)
    alpha = int(255 * progress)
    
    if alpha > 0:
        # Multiple glow layers
        for radius in [8, 4, 2]:
            glow_color = (255, 195, 80, int(40 * alpha / 255))
            draw.text((tx + radius, ty + radius), title, font=title_font, fill=glow_color)
        
        # Gold gradient text
        draw.text((tx, ty), title, font=title_font, fill=(*COLORS["accent_gold"], alpha))
        
        # Subtitle
        sub_progress = max(0, min(1.0, (local_t - 1.5) / 2.0))
        if sub_progress > 0:
            sub_alpha = int(255 * sub_progress)
            try:
                sub_font = ImageFont.truetype(FONT_PATH, 28) if FONT_PATH else ImageFont.load_default()
            except:
                sub_font = ImageFont.load_default()
            
            subtitle = "Welcome to the future of creation."
            bbox = sub_font.getbbox(subtitle)
            stw = bbox[2] - bbox[0]
            sx = (WIDTH - stw) // 2
            sy = ty + th + 50
            
            # Fade in
            draw.text((sx, sy), subtitle, font=sub_font, fill=(*COLORS["text_warm"], sub_alpha))
            
            # Bottom tagline
            tagline = "suzume"
            bbox = sub_font.getbbox(tagline)
            ttw = bbox[2] - bbox[0]
            tgx = (WIDTH - ttw) // 2
            tgy = sy + 60
            tag_alpha = int(200 * sub_progress)
            draw.text((tgx, tgy), tagline, font=sub_font, fill=(*COLORS["text_dim"], tag_alpha))
    
    # Decorative orbs floating
    img = Image.alpha_composite(img, overlay)
    
    # Final particles
    particles = create_particle_frame(WIDTH, HEIGHT, t * 0.5,
        (255, 200, 100), (100, 200, 255), 40)
    img = Image.alpha_composite(img, particles)
    
    return np.array(img)[:, :, :3]


# ==================== MAIN RENDER ====================

def ensure_tts():
    """Generate TTS files if they don't exist."""
    tts_files = [
        "tts_01.wav", "tts_02.wav", "tts_03.wav",
        "tts_04.wav", "tts_05.wav", "tts_06.wav"
    ]
    missing = [f for f in tts_files if not os.path.exists(os.path.join(OUTPUT_DIR, f))]
    if missing:
        print(f"Generating TTS files: {missing}")
        from generate_tts import generate_all
        asyncio.run(generate_all())
    else:
        print("All TTS files exist.")


def get_tts_audio():
    """Load TTS audio clips with proper timing."""
    clips = []
    
    # TTS timing (start time in video, filename)
    tts_schedule = [
        (1.5, "tts_01.wav"),   # "In a world..."
        (11.0, "tts_02.wav"),  # "Suzume is not just..."
        (21.0, "tts_03.wav"),  # "Full stack applications..."
        (31.0, "tts_04.wav"),  # "Every pixel designed..."
        (41.0, "tts_05.wav"),  # "From concept to deployment..."
        (52.0, "tts_06.wav"),  # "Welcome to the future..."
    ]
    
    for start_time, filename in tts_schedule:
        path = os.path.join(OUTPUT_DIR, filename)
        if os.path.exists(path):
            try:
                clip = AudioFileClip(path)
                # Position at start_time
                clip = clip.with_start(start_time)
                clips.append(clip)
                print(f"  Loaded TTS: {filename} ({clip.duration:.1f}s @ {start_time:.1f}s)")
            except Exception as e:
                print(f"  Error loading {filename}: {e}")
    
    return clips


def get_bgm():
    """Load or generate background music."""
    bgm_path = os.path.join(OUTPUT_DIR, "bgm_cinematic.wav")
    if not os.path.exists(bgm_path):
        print("Generating BGM...")
        from generate_audio import generate_bgm, save_wav, SAMPLE_RATE
        bgm_data = generate_bgm(duration=DURATION)
        save_wav(bgm_path, bgm_data)
    
    try:
        bgm = AudioFileClip(bgm_path)
        print(f"BGM loaded: {bgm.duration:.1f}s")
        return bgm
    except Exception as e:
        print(f"Error loading BGM: {e}")
        return None


def render_video():
    """Main render function."""
    print("=" * 60)
    print("SUZUME CINEMATIC REEL GENERATOR")
    print("=" * 60)
    
    # Ensure TTS files exist
    # ensure_tts()
    
    # Define scenes
    scenes_data = [
        {
            "name": "Opening",
            "start": 0,
            "end": 10,
            "generator": scene_01_opening,
        },
        {
            "name": "About",
            "start": 10,
            "end": 20,
            "generator": scene_02_about,
        },
        {
            "name": "Capabilities",
            "start": 20,
            "end": 31,
            "generator": scene_03_capabilities,
        },
        {
            "name": "Design",
            "start": 31,
            "end": 42,
            "generator": scene_04_design,
        },
        {
            "name": "Finale",
            "start": 42,
            "end": DURATION,
            "generator": scene_05_finale,
        },
    ]
    
    print(f"\nTotal duration: {DURATION}s at {FPS}fps")
    print(f"Resolution: {WIDTH}x{HEIGHT}")
    print(f"Scenes: {len(scenes_data)}")
    print()
    
    # Create video clip
    def make_frame(t):
        return create_cinematic_frame(t, scenes_data)
    
    print("Creating VideoClip...")
    video = VideoClip(make_frame, duration=DURATION)
    video = video.with_fps(FPS)
    
    # Audio: TTS + BGM
    print("Loading audio tracks...")
    audio_clips = []
    
    bgm = get_bgm()
    if bgm:
        # Reduce BGM volume to -18dB (leave room for voice)
        bgm = bgm.with_volume_scaled(0.35)
        audio_clips.append(bgm)
    
    tts_clips = get_tts_audio()
    audio_clips.extend(tts_clips)
    
    if audio_clips:
        print(f"Compositing {len(audio_clips)} audio tracks...")
        final_audio = CompositeAudioClip(audio_clips)
        video = video.with_audio(final_audio)
    
    # Output
    output_path = os.path.join(OUTPUT_DIR, "suzume_cinematic.mp4")
    print(f"\nRendering to: {output_path}")
    print("This may take several minutes...")
    
    # Write with high quality settings
    video.write_videofile(
        output_path,
        codec="libx264",
        audio_codec="aac",
        fps=FPS,
        bitrate="15000k",       # High video bitrate for quality
        audio_bitrate="320k",   # High quality stereo audio
        preset="medium",
        ffmpeg_params=[
            "-pix_fmt", "yuv420p",
            "-profile:v", "high",
            "-level", "4.1",
            "-movflags", "+faststart",
        ]
    )
    
    print(f"\n✓ Video rendered: {output_path}")
    
    # Get file size
    size_mb = os.path.getsize(output_path) / (1024 * 1024)
    print(f"  File size: {size_mb:.1f} MB")
    
    return output_path


if __name__ == "__main__":
    render_video()
