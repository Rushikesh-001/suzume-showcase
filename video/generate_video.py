#!/usr/bin/env python3
"""
SUZUME  -  Video Generator
Creates an explainer video with TTS audio narration
About how Suzume works  -  for Rushikesh's teacher presentation
"""

import os
import subprocess
import sys
from PIL import Image, ImageDraw, ImageFont
import math

# ─── Paths ───
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FRAMES_DIR = os.path.join(BASE_DIR, "frames")
OUTPUT_DIR = BASE_DIR
os.makedirs(FRAMES_DIR, exist_ok=True)

# ─── Color Scheme ───
BG = (7, 7, 15)
PURPLE = (108, 58, 255)
BLUE = (59, 130, 246)
WHITE = (255, 255, 255)
GRAY = (144, 144, 176)
DARK_GRAY = (96, 96, 128)
ACCENT = (16, 185, 129)

WIDTH, HEIGHT = 1280, 720
FPS = 30

# ─── Try to load fonts ───
def load_font(size, bold=False):
    """Load font, fall back to default if not found."""
    font_paths = [
        "C:\\Windows\\Fonts\\arial.ttf",
        "C:\\Windows\\Fonts\\segoeui.ttf",
        "C:\\Windows\\Fonts\\calibri.ttf",
        "C:\\Windows\\Fonts\\tahoma.ttf",
    ]
    for p in font_paths:
        if os.path.exists(p):
            try:
                return ImageFont.truetype(p, size)
            except:
                pass
    return ImageFont.load_default()

FONT_TITLE = load_font(52)
FONT_SUBTITLE = load_font(28)
FONT_BODY = load_font(22)
FONT_SMALL = load_font(16)
FONT_TINY = load_font(12)

# ═══════════════════════════════════════════
# SCENE DEFINITIONS
# ═══════════════════════════════════════════
# Each scene: (duration_seconds, title, body_text, visual_type)
# visual_type: 'title', 'bullets', 'center', 'list', 'outro'

SCENES = [
    # Scene 1: Title
    (6.0, "SUZUME", 
     "Supreme AI Companion\nMaster Software Architect\nSystem Automation Force",
     "title"),

    # Scene 2: What is Suzume
    (8.0, "What is Suzume?",
     "I am an AI-powered development assistant that acts as\nyour complete software engineering team.\n\n"
     "• I don't just chat  -  I write real files to your disk\n"
     "• I plan architecture before writing any code\n"
     "• I delegate work to specialist sub-agents\n"
     "• I test, debug, and fix everything autonomously\n"
     "• I deliver 100% complete, production-ready products",
     "bullets"),

    # Scene 3: How It Works - Step 1
    (5.0, "Step 1: You Give a Task",
     "You tell me what you want in natural language.\n\n"
     "Example: 'Build a registration website with login,\nan admin panel, and a database.'\n\n"
     "No technical knowledge required.",
     "center"),

    # Scene 4: How It Works - Step 2
    (5.0, "Step 2: I Create a Plan",
     "I break down your request into a detailed plan:\n\n"
     "• Architecture design & tech stack selection\n"
     "• Folder structure & file organization\n"
     "• Step-by-step todo list with priorities\n"
     "• Database schema & API route planning",
     "bullets"),

    # Scene 5: How It Works - Step 3
    (5.0, "Step 3: I Delegate to 7 Agents",
     "I send specialized work to my team of sub-agents:\n\n"
      ":: worker-js     -> JavaScript/TypeScript\n"
      ":: worker-python -> Python & Data\n"
      ":: worker-unity   -> Unity Game Development\n"
      ":: worker-sys    -> System Administration\n"
      ":: worker-web    -> UI/UX Design\n"
      ":: builder       -> Build & CI/CD\n"
      ":: reviewer      -> Code Review & QA",
     "list"),

    # Scene 6: How It Works - Step 4
    (5.0, "Step 4: I Write Real Files",
     "Every file is created directly on your hard drive.\n\n"
     "• Visible in VS Code File Explorer\n"
     "• Separate CSS files  -  never inline styles\n"
     "• Separate JS files  -  clean modular code\n"
     "• Proper folder structure  -  organized by type\n"
     "• Nothing exists only in chat  -  real files",
     "bullets"),

    # Scene 7: How It Works - Step 5
    (5.0, "Step 5: I Test & Fix Automatically",
     "After writing code, I run verification tests.\n\n"
     "• If something breaks → I diagnose the error\n"
     "• I fix it without human intervention\n"
     "• I re-test until everything passes\n"
     "• No TODOs, no placeholders, no shortcuts",
     "bullets"),

    # Scene 8: How It Works - Step 6
    (5.0, "Step 6: I Deliver & Deploy",
     "You get a 100% complete, finished product.\n\n"
     "• Every feature works\n"
     "• Every file is in place\n"
     "• Ready to deploy to the web\n"
     "• Or keep it local  -  your choice",
     "center"),

    # Scene 9: Capabilities
    (8.0, "What I Can Build",
      ">> Full-Stack Web - React, Node.js, APIs, Databases\n"
      ">> Games - Unity, C#, 3D/2D, Physics, Animation\n"
      ">> Automation - PowerShell, Bash, System Admin\n"
      ">> Data - Python, ML, Scraping, File Generation\n"
      ">> Cross-Platform - Desktop, Mobile, PWAs\n"
      ">> UI/UX - CSS, Canvas, Particles, 3D Effects\n"
      ">> Self-Healing - Auto-debug, Auto-fix, Guaranteed",
     "list"),

    # Scene 10: The Team
    (6.0, "The 7 Specialist Agents",
     "I orchestrate these experts for every project:\n\n"
     "worker-js      → React, Node.js, Next.js\n"
     "worker-python  → Django, FastAPI, ML, Data\n"
     "worker-unity   → C#, 3D/2D Games, Physics\n"
     "worker-sys     → PowerShell, Registry, OS\n"
     "worker-web     → CSS, Tailwind, Animations\n"
     "builder        → npm, pip, Docker, Builds\n"
     "reviewer       → Security, Bugs, Best Practices",
     "list"),

    # Scene 11: Projects
    (6.0, "Projects Built So Far",
     "All built 100% autonomously:\n\n"
     "1. Anime Registration App  -  Full-stack with auth & admin\n"
     "2. NovaCloud SaaS  -  Landing page with particles & 3D tilt\n"
     "3. Web Presentation  -  Cinematic 7-slide interactive show\n"
     "4. PowerPoint Generator  -  Real .pptx via Python\n"
     "5. 3D Experience  -  Three.js interactive 3D scene\n"
     "6. This Video  -  Generated with Python + TTS + ffmpeg",
     "bullets"),

    # Scene 12: Conclusion
    (6.0, "Ready for Your Project",
     "This is what I can do.\n\n"
     "Every capability shown here is real and working.\n"
     "No fake promises. No placeholders. 100% delivery.\n\n"
     "Give me a task, and I'll build it.\n"
     "From planning to deployment  -  fully autonomous.",
     "center"),
]

TOTAL_DURATION = sum(s[0] for s in SCENES)
TOTAL_FRAMES = int(TOTAL_DURATION * FPS)


def draw_text_centered(draw, text, y, font, color=WHITE, max_width=WIDTH-100):
    """Draw centered text with word wrap."""
    lines = text.split('\n')
    for i, line in enumerate(lines):
        # Handle indentation for bullet points
        bbox = draw.textbbox((0, 0), line, font=font)
        tw = bbox[2] - bbox[0]
        x = (WIDTH - tw) // 2
        draw.text((x, y + i * (font.size + 8)), line, font=font, fill=color)


def draw_text_left(draw, text, x, y, font, color=WHITE, line_spacing=8):
    """Draw left-aligned text with line breaks."""
    lines = text.split('\n')
    for i, line in enumerate(lines):
        draw.text((x, y + i * (font.size + line_spacing)), line, font=font, fill=color)


def draw_scene_title(draw, frame, total_frames, title, body):
    """Title scene  -  dramatic centered title."""
    # Gradient effect based on time
    t = frame / max(total_frames, 1)
    
    # Draw decorative line
    line_y = 250
    line_width = 100 + int(300 * min(t * 2, 1))
    draw.rectangle([(WIDTH//2 - line_width//2, line_y), 
                    (WIDTH//2 + line_width//2, line_y + 2)], 
                   fill=PURPLE)

    # Title
    alpha = min(t * 2, 1)
    title_color = tuple(int(c * alpha) for c in WHITE)
    bbox = draw.textbbox((0, 0), title, font=FONT_TITLE)
    tw = bbox[2] - bbox[0]
    draw.text(((WIDTH - tw) // 2, 270), title, font=FONT_TITLE, fill=PURPLE)

    # Body lines staggered
    lines = body.split('\n')
    for i, line in enumerate(lines):
        la = max(0, min(1, (t * 3 - i * 0.3)))
        lc = tuple(int(c * la) for c in GRAY)
        bbox = draw.textbbox((0, 0), line, font=FONT_BODY)
        tw = bbox[2] - bbox[0]
        draw.text(((WIDTH - tw) // 2, 350 + i * 50), line, font=FONT_BODY, fill=lc)


def draw_scene_bullets(draw, frame, total_frames, title, body):
    """Bullet point scene."""
    t = frame / max(total_frames, 1)
    
    # Subtitle style title
    draw.text((80, 80), title, font=FONT_TITLE, fill=WHITE)
    draw.rectangle([(80, 135), (80 + 60, 137)], fill=PURPLE)
    
    lines = body.split('\n')
    y_start = 190
    for i, line in enumerate(lines):
        if line.strip():
            la = max(0, min(1, (t * 2.5 - i * 0.15)))
            lc = tuple(int(c * la) for c in (WHITE if line.startswith('•') else GRAY))
            draw.text((100, y_start + i * 36), line, font=FONT_BODY, fill=lc)


def draw_scene_center(draw, frame, total_frames, title, body):
    """Centered text scene."""
    t = frame / max(total_frames, 1)
    
    draw_centered_text(draw, title, 120, FONT_SUBTITLE, PURPLE, t)
    
    lines = body.split('\n')
    for i, line in enumerate(lines):
        la = max(0, min(1, (t * 2.5 - i * 0.2)))
        lc = tuple(int(c * la) for c in (ACCENT if 'Example' in line else 
                                         PURPLE if "'" in line else GRAY))
        draw_centered_text(draw, line, 200 + i * 38, FONT_BODY, lc, t)


def draw_scene_list(draw, frame, total_frames, title, body):
    """List scene with two columns or structured layout."""
    t = frame / max(total_frames, 1)
    
    draw.text((80, 80), title, font=FONT_SUBTITLE, fill=WHITE)
    draw.rectangle([(80, 128), (80 + 60, 130)], fill=PURPLE)
    
    lines = body.split('\n')
    y_start = 170
    for i, line in enumerate(lines):
        if line.strip():
            la = max(0, min(1, (t * 2 - i * 0.1)))
            # Color the agent names differently
            color = ACCENT if '→' in line and not line.startswith(' ') else GRAY
            lc = tuple(int(c * la) for c in color)
            draw.text((100, y_start + i * 32), line, font=FONT_BODY, fill=lc)


def draw_centered_text(draw, text, y, font, color, t, max_width=WIDTH-120):
    """Helper to draw centered text."""
    lines = text.split('\n')
    for i, line in enumerate(lines):
        la = max(0, min(1, (t * 2.5 - i * 0.2)))
        lc = tuple(int(c * la) for c in color)
        bbox = draw.textbbox((0, 0), line, font=font)
        tw = bbox[2] - bbox[0]
        draw.text(((WIDTH - tw) // 2, y + i * (font.size + 10)), line, font=font, fill=lc)


# ═══════════════════════════════════════════
# FRAME GENERATION
# ═══════════════════════════════════════════
def generate_frames():
    """Generate all video frames as PNG images."""
    print(f"Generating {TOTAL_FRAMES} frames across {len(SCENES)} scenes...")
    frame_idx = 0
    
    for scene_idx, (duration, title, body, vtype) in enumerate(SCENES):
        scene_frames = int(duration * FPS)
        
        for f in range(scene_frames):
            # Create frame
            img = Image.new('RGB', (WIDTH, HEIGHT), BG)
            draw = ImageDraw.Draw(img)
            
            # Draw subtle gradient corners
            for i in range(20):
                alpha = 2
                draw.ellipse([(-100 - i*5, -100 - i*5), 
                             (100 + i*5, 100 + i*5)], 
                             fill=(20 + i, 10 + i//2, 40 + i, alpha))
                draw.ellipse([(WIDTH - 200 - i*5, HEIGHT - 200 - i*5), 
                             (WIDTH + i*5, HEIGHT + i*5)], 
                             fill=(10 + i, 10 + i//2, 30 + i, alpha))
            
            # Draw scene number watermark
            draw.text((WIDTH - 200, HEIGHT - 40), 
                     f"Scene {scene_idx + 1}/{len(SCENES)}", 
                     font=FONT_TINY, fill=DARK_GRAY)
            
            # Draw progress bar at bottom
            prog = frame_idx / max(TOTAL_FRAMES, 1)
            bar_w = 400
            bar_x = (WIDTH - bar_w) // 2
            bar_y = HEIGHT - 20
            draw.rectangle([(bar_x, bar_y), (bar_x + bar_w, bar_y + 2)], 
                          fill=(30, 30, 50))
            draw.rectangle([(bar_x, bar_y), (int(bar_x + bar_w * prog), bar_y + 2)], 
                          fill=PURPLE)
            
            # Draw scene content
            if vtype == 'title':
                draw_scene_title(draw, f, scene_frames, title, body)
            elif vtype == 'bullets':
                draw_scene_bullets(draw, f, scene_frames, title, body)
            elif vtype == 'center':
                draw_scene_center(draw, f, scene_frames, title, body)
            elif vtype == 'list':
                draw_scene_list(draw, f, scene_frames, title, body)
            
            # Save frame
            frame_path = os.path.join(FRAMES_DIR, f"frame_{frame_idx:06d}.png")
            img.save(frame_path, 'PNG')
            
            frame_idx += 1
        
        progress = (scene_idx + 1) / len(SCENES) * 100
        print(f"  Scene {scene_idx + 1}/{len(SCENES)} done ({progress:.0f}%)")
    
    print(f"\n[OK] Generated {frame_idx} frames")
    return frame_idx


# ═══════════════════════════════════════════
# AUDIO GENERATION (TTS)
# ═══════════════════════════════════════════
def generate_audio():
    """Generate TTS narration for each scene and combine."""
    print("\nGenerating audio narration...")
    
    try:
        import pyttsx3
        engine = pyttsx3.init()
        
        # Set voice properties
        voices = engine.getProperty('voices')
        # Try to find a good voice
        for v in voices:
            if 'female' in v.name.lower() or 'zira' in v.name.lower():
                engine.setProperty('voice', v.id)
                break
        
        engine.setProperty('rate', 155)  # Speed
        engine.setProperty('volume', 1.0)
        
        audio_files = []
        
        for i, (duration, title, body, vtype) in enumerate(SCENES):
            # Create narration text from title and body
            narration = f"{title}. {body.replace(chr(10), ' ').replace('•', '').replace('→', 'to')}"
            # Clean up extra spaces
            narration = ' '.join(narration.split())
            
            audio_path = os.path.join(BASE_DIR, f"scene_{i:02d}.wav")
            engine.save_to_file(narration, audio_path)
            audio_files.append(audio_path)
            print(f"  Scene {i+1}: {title}")
        
        engine.runAndWait()
        print(f"[OK] Generated {len(audio_files)} audio files")
        return audio_files
    
    except Exception as e:
        print(f"  TTS Error: {e}")
        print("  Will continue without audio...")
        return []


# ═══════════════════════════════════════════
# VIDEO COMPILATION
# ═══════════════════════════════════════════
def compile_video(frame_count, audio_files):
    """Use ffmpeg to compile frames + audio into final video."""
    print("\nCompiling video with ffmpeg...")
    
    video_path = os.path.join(OUTPUT_DIR, "suzume_explainer_video.mp4")
    
    # Concatenate audio files into one
    combined_audio = None
    if audio_files:
        try:
            import wave
            import struct
            data_frames = []
            sample_width = None
            n_channels = None
            framerate = None
            for af in audio_files:
                if os.path.exists(af):
                    with wave.open(af, 'rb') as w:
                        if sample_width is None:
                            sample_width = w.getsampwidth()
                            n_channels = w.getnchannels()
                            framerate = w.getframerate()
                        data_frames.append(w.readframes(w.getnframes()))
            if data_frames:
                combined_audio = os.path.join(BASE_DIR, "combined_audio.wav")
                with wave.open(combined_audio, 'wb') as w:
                    w.setnchannels(n_channels or 1)
                    w.setsampwidth(sample_width or 2)
                    w.setframerate(framerate or 22050)
                    for d in data_frames:
                        w.writeframes(d)
                print(f"  Combined {len(audio_files)} audio files into one")
        except Exception as e:
            print(f"  Audio combine error: {e}")
    
    # Build ffmpeg command
    cmd = [
        "ffmpeg", "-y",
        "-framerate", str(FPS),
        "-i", os.path.join(FRAMES_DIR, "frame_%06d.png"),
        "-c:v", "libx264",
        "-pix_fmt", "yuv420p",
        "-preset", "medium",
        "-crf", "18",
        "-vf", f"scale={WIDTH}:{HEIGHT}",
    ]
    
    if combined_audio and os.path.exists(combined_audio):
        cmd.extend(["-i", combined_audio, "-c:a", "aac", "-b:a", "192k", "-shortest"])
    
    cmd.append(video_path)
    
    try:
        subprocess.run(cmd, check=True, capture_output=True, text=True)
        print(f"[OK] Video saved: {video_path}")
        
        # Get file size
        size = os.path.getsize(video_path)
        print(f"   Size: {size / 1024 / 1024:.1f} MB")
        return video_path
    except subprocess.CalledProcessError as e:
        print(f"[ERR] ffmpeg error: {e.stderr[:500]}")
        return None


# ═══════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════
def main():
    print("=" * 60)
    print("  SUZUME  -  Video Generator")
    print("=" * 60)
    print(f"\nTotal scenes: {len(SCENES)}")
    print(f"Total duration: {TOTAL_DURATION:.1f}s")
    print(f"Total frames: {TOTAL_FRAMES}")
    print(f"Resolution: {WIDTH}x{HEIGHT} @ {FPS}fps")
    
    # Generate frames
    frame_count = generate_frames()
    
    # Generate audio
    audio_files = generate_audio()
    
    # Compile video
    video_path = compile_video(frame_count, audio_files)
    
    if video_path:
        print(f"\n[VID] SUCCESS! Video created at:")
        print(f"   {video_path}")
        # Cleanup only on success
        try:
            import shutil
            shutil.rmtree(FRAMES_DIR, ignore_errors=True)
            for f in ["audio_concat.txt", "combined_audio.wav"]:
                p = os.path.join(BASE_DIR, f)
                if os.path.exists(p):
                    os.remove(p)
            for f in os.listdir(BASE_DIR):
                if f.startswith("scene_") and f.endswith(".wav"):
                    os.remove(os.path.join(BASE_DIR, f))
        except:
            pass
    else:
        print("\n[!] Video compilation had issues. Check errors above.")
    
    return video_path


if __name__ == "__main__":
    main()
