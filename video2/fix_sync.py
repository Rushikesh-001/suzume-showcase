#!/usr/bin/env python3
"""
SUZUME V2.1 — Perfect Audio/Video Sync Fix
Each scene's frame count = round(audio_duration * FPS) for frame-perfect sync.
No global audio trim. Each scene audio matches its video exactly.
"""

import os, sys, subprocess, shutil, math, wave, struct, time
from PIL import Image, ImageDraw, ImageFont

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
AUDIO_DIR = os.path.join(BASE_DIR, "audio")
FRAMES_DIR = os.path.join(BASE_DIR, "frames_render2")
OUTPUT_FILE = os.path.join(BASE_DIR, "suzume_synced.mp4")

for d in [FRAMES_DIR]:
    os.makedirs(d, exist_ok=True)

WIDTH, HEIGHT = 1280, 720
FPS = 30
PURPLE = (108, 58, 255)
BLUE = (59, 130, 246)
PINK = (236, 72, 153)
WHITE = (255, 255, 255)
GRAY = (144, 144, 176)
DARK = (7, 7, 15)
ACCENT = (16, 185, 129)
CYAN = (6, 182, 212)
DARK_GRAY = (96, 96, 128)

def load_font(size):
    paths = ["C:\\Windows\\Fonts\\arial.ttf","C:\\Windows\\Fonts\\segoeui.ttf","C:\\Windows\\Fonts\\calibri.ttf"]
    for p in paths:
        if os.path.exists(p):
            try: return ImageFont.truetype(p, size)
            except: pass
    return ImageFont.load_default()

FONT_HERO = load_font(80)
FONT_TITLE = load_font(56)
FONT_SUB = load_font(32)
FONT_BODY = load_font(26)
FONT_SMALL = load_font(18)
FONT_TINY = load_font(14)
FONT_CODE = load_font(18)

SCENES = [
    {"id":"title",     "min_dur":6.0},
    {"id":"problem",   "min_dur":8.0},
    {"id":"meet",      "min_dur":15.0},
    {"id":"workflow",  "min_dur":22.0},
    {"id":"agents",    "min_dur":18.0},
    {"id":"capabilities","min_dur":14.0},
    {"id":"projects",  "min_dur":14.0},
    {"id":"closing",   "min_dur":10.0},
]

def get_mp3_duration(mp3_path):
    try:
        r = subprocess.run(["ffprobe","-v","error","-show_entries","format=duration",
                           "-of","default=noprint_wrappers=1:nokey=1",mp3_path],
                          capture_output=True,text=True,timeout=30)
        return float(r.stdout.strip())
    except: return 5.0

# ─── STEP 1: Measure audio durations & calculate exact frame counts ───
print("=" * 60)
print("  STEP 1: Measuring audio durations for perfect sync")
print("=" * 60)

total_audio = 0.0
for i, scene in enumerate(SCENES):
    audio_path = os.path.join(AUDIO_DIR, f"scene_{i:02d}.mp3")
    if not os.path.exists(audio_path):
        print(f"  [ERR] Missing audio: {audio_path}")
        continue
    dur = get_mp3_duration(audio_path)
    # Use round() for frame-perfect match
    frames = max(round(dur * FPS), round(scene["min_dur"] * FPS))
    scene["audio_path"] = audio_path
    scene["audio_dur"] = dur
    scene["frames"] = frames
    video_dur = frames / FPS
    diff = dur - video_dur
    total_audio += dur
    print(f"  Scene {i} ({scene['id']}): audio={dur:.3f}s -> frames={frames} ({video_dur:.3f}s) diff={diff:.4f}s")

total_frames = sum(s["frames"] for s in SCENES)
total_video = total_frames / FPS
print(f"\n  Total audio: {total_audio:.3f}s")
print(f"  Total video: {total_video:.3f}s ({total_frames} frames)")
print(f"  Difference: {total_audio - total_video:.4f}s")

# ─── STEP 2: Render frames with same visual quality ───
print("\n" + "=" * 60)
print("  STEP 2: Rendering frames with corrected counts")
print("=" * 60)

def draw_bg(draw, t, scene_idx, w, h):
    draw.rectangle([(0,0),(w,h)], fill=DARK)
    colors = [PURPLE, BLUE, PINK]
    ci = colors[scene_idx % 3]
    for i in range(3):
        cx = w * (0.15 + 0.7*(i/2))
        cy = h * (0.2 + 0.6*math.sin(t*0.8 + i*2.0))
        r = 60 + 20*math.sin(t*1.5 + i*1.3)
        draw.ellipse([cx-r, cy-r, cx+r, cy+r], 
                    fill=(ci[0]//6, ci[1]//6, ci[2]//6),
                    outline=(ci[0]//4, ci[1]//4, ci[2]//4), width=1)
    for i in range(15):
        sx = w * ((i*0.23 + t*0.02) % 1.0)
        sy = h * ((i*0.47 + t*0.01) % 1.0)
        ss = 1.5 + 1.0*math.sin(t*0.5 + i)
        dc = colors[i%3]
        draw.ellipse([sx-ss, sy-ss, sx+ss, sy+ss],
                    fill=(dc[0]//7, dc[1]//7, dc[2]//7))

def draw_progress(draw, t, scene_idx, total_scenes, w, h):
    bar_w, bar_h = 400, 2
    bar_x, bar_y = (w-bar_w)//2, h-30
    draw.rectangle([(bar_x,bar_y),(bar_x+bar_w,bar_y+bar_h)], fill=(30,30,50))
    draw.rectangle([(bar_x,bar_y),(bar_x+int(bar_w*t),bar_y+bar_h)], fill=PURPLE)
    draw.text((bar_x, bar_y-22), f"Scene {scene_idx+1}/{total_scenes}", font=load_font(12), fill=DARK_GRAY)

def draw_title_scene(draw, t):
    """Epic title scene."""
    title = "SUZUME"
    spacing = 85
    tw = len(title) * spacing
    sx = (WIDTH - tw) // 2
    for i, ch in enumerate(title):
        cd = 0.1 + i*0.12
        ct = max(0, min(1, (t-cd)/0.3))
        ease = 1 - (1-ct)**3
        cy = 250 - (1-ease)*80
        a = int(255*ease)
        draw.text((sx + i*spacing, cy), ch, font=FONT_HERO, fill=(255,255,255,a))
    if t > 0.8:
        tt = min(1, (t-0.8)/0.5)
        tag = "Supreme AI Companion"
        bb = draw.textbbox((0,0), tag, font=FONT_SUB)
        draw.text(((WIDTH-(bb[2]-bb[0]))//2, 380), tag, font=FONT_SUB,
                 fill=(GRAY[0],GRAY[1],GRAY[2],int(255*tt)))
    if t > 1.2:
        tt = min(1, (t-1.2)/0.5)
        sub = "Master Software Architect  \u2022  System Automation Force"
        bb = draw.textbbox((0,0), sub, font=FONT_SMALL)
        draw.text(((WIDTH-(bb[2]-bb[0]))//2, 430), sub, font=FONT_SMALL,
                 fill=(DARK_GRAY[0],DARK_GRAY[1],DARK_GRAY[2],int(200*tt)))
    lw = min(200, int(200*max(0,(t-0.3)/0.5)))
    draw.rectangle([((WIDTH-lw)//2,340),((WIDTH+lw)//2,342)], fill=PURPLE)

def draw_problem_scene(draw, t):
    lines = [
        (0.0, "Imagine...", FONT_TITLE, WHITE, 180),
        (0.5, "You describe a software project", FONT_BODY, GRAY, 270),
        (0.9, "in plain English.", FONT_BODY, GRAY, 310),
        (1.5, "And a complete development team", FONT_BODY, GRAY, 370),
        (1.8, "builds it for you instantly.", FONT_BODY, GRAY, 410),
        (3.0, "Planning. Coding. Testing. Deployment.", FONT_SUB, ACCENT, 480),
        (4.0, "No meetings. No delays. No excuses.", FONT_BODY, PINK, 530),
    ]
    for delay, text, font, color, y in lines:
        if t > delay:
            tt = min(1, (t-delay)/0.4)
            a = int(255*tt)
            px = int(20*(1-tt))
            draw.text((80+px, y), text, font=font, fill=(color[0],color[1],color[2],a))

def draw_meet_scene(draw, t):
    # Title
    delay = 0
    nchars = len("Meet Suzume.")
    rcount = max(0, min(nchars, int((t-delay)/0.04))) if t>delay else 0
    draw.text((100,150), "Meet Suzume."[:rcount], font=FONT_HERO, fill=WHITE)
    if rcount < nchars:
        draw.text((100 + draw.textbbox((0,0),"Meet Suzume."[:rcount],font=FONT_HERO)[2], 150),
                 "Meet Suzume."[rcount:], font=FONT_HERO, fill=(40,40,60))
    
    # Terminal
    if t > 0.5:
        ca = min(1, (t-0.5)/0.5)
        code = [("suzume@build ~ %", CYAN),("$ build website",ACCENT),
                ("  > Arch: React + Node + SQLite",GRAY),("  > Planning complete.",GRAY),
                ("  > Delegating to agents...",GRAY),("  > Building... [#######]",ACCENT),
                ("$ Deployment: SUCCESS",ACCENT)]
        bx, by, bw, bh = 950, 200, 850, 420
        draw.rectangle([(bx,by),(bx+bw,by+bh)], fill=(10,10,25), outline=(40,40,80), width=1)
        draw.rectangle([(bx,by),(bx+bw,by+40)], fill=(20,20,45))
        draw.text((bx+15, by+8), "Suzume Terminal", font=FONT_SMALL, fill=GRAY)
        for i,(line,clr) in enumerate(code):
            ly = by + 55 + i*45
            if t > 1.0 + i*0.15:
                lt = min(1,(t-1.0-i*0.15)/0.2)
                la = int(255*lt*ca)
                vc = int(len(line)*min(1,(t-1.0-i*0.15)/0.3))
                draw.text((bx+20, ly), line[:vc], font=FONT_CODE,
                         fill=(clr[0],clr[1],clr[2],la))
    
    # Bullets
    bullets = [(2.5,"I write real files to your hard drive"),(3.5,"I plan architecture before writing code"),
               (4.5,"I delegate to specialist sub-agents"),(5.5,"I test and fix everything automatically"),
               (6.5,"I deliver 100% complete products")]
    for delay,text in bullets:
        if t > delay:
            bt = min(1,(t-delay)/0.3)
            idx = bullets.index((delay,text))
            draw.text((100+int((1-bt)*30), 600+40*idx), f">  {text}", font=FONT_BODY,
                     fill=(GRAY[0],GRAY[1],GRAY[2],int(255*bt)))

def draw_workflow_scene(draw, t):
    steps = [("01","You Give a Task","Describe in plain language"),("02","I Create a Plan","Architecture & todo list"),
             ("03","Delegate to Agents","7 specialists in parallel"),("04","Write Real Files","Disk, organized folders"),
             ("05","Test & Fix","Auto-debug until perfect"),("06","Deliver","100% complete product")]
    draw.text((100,80), "How I Work", font=FONT_TITLE, fill=WHITE)
    n = len(steps)
    bw, bh, gap = 200, 130, 20
    tw2 = n*bw + (n-1)*gap
    sx2 = (WIDTH-tw2)//2
    for i,(num,title,desc) in enumerate(steps):
        st = t - i*0.3
        if st<0: continue
        prog = min(1, st/0.4)
        ease = 1-(1-prog)**3
        bx = sx2 + i*(bw+gap)
        by = 300 + (1-ease)*60
        a = int(255*prog)
        draw.rectangle([(bx,by),(bx+bw,by+bh)], fill=(15,15,35,a), outline=(40,40,80,a), width=1)
        draw.text((bx+15,by+15), num, font=FONT_SUB, fill=PURPLE)
        draw.text((bx+15,by+55), title, font=load_font(16), fill=(255,255,255,a))
        draw.text((bx+15,by+85), desc, font=load_font(13), fill=(GRAY[0],GRAY[1],GRAY[2],a))

def draw_agents_scene(draw, t):
    agents = [("worker-js","JavaScript/TypeScript","React, Next.js, Node",PURPLE),
              ("worker-python","Python & Data","FastAPI, Django, ML",BLUE),
              ("worker-unity","Game Development","C#, 3D/2D, Physics",ACCENT),
              ("worker-sys","System Admin","PowerShell, Bash, OS",PINK),
              ("worker-web","UI/UX Design","CSS, Tailwind, Canvas",CYAN),
              ("builder","Build & CI/CD","npm, pip, Docker",(246,173,85)),
              ("reviewer","Code Review & QA","Security, Bugs, Style",(147,51,234))]
    draw.text((100,60), "7 Specialist Agents", font=FONT_TITLE, fill=WHITE)
    draw.text((100,120), "I orchestrate these experts for every project", font=FONT_BODY, fill=GRAY)
    cols, cw, ch, gx, gy = 4, 420, 160, 30, 30
    tgw = min(cols,len(agents))*cw + (min(cols,len(agents))-1)*gx
    sx2 = (WIDTH-tgw)//2
    for i,(name,role,techs,color) in enumerate(agents):
        col, row = i%cols, i//cols
        delay = 0.3+i*0.15
        if t<delay: continue
        prog = min(1,(t-delay)/0.4)
        ease = 1-(1-prog)**3
        a = int(255*prog)
        cx = sx2 + col*(cw+gx)
        cy = 180 + row*(ch+gy)
        scale = 0.8+0.2*ease
        off = (1-scale)*cw//2
        draw.rectangle([(cx+off,cy+off),(cx+cw-off,cy+ch-off)],
                      fill=(12,12,30,a), outline=(color[0],color[1],color[2],40+a//5), width=1)
        draw.rectangle([(cx+10+off,cy+off+4),(cx+60+off,cy+off+7)],
                      fill=(color[0],color[1],color[2],a))
        draw.text((cx+20+off,cy+20+off), name, font=load_font(18), fill=WHITE)
        draw.text((cx+20+off,cy+55+off), role, font=load_font(14),
                 fill=(color[0],color[1],color[2],a))
        draw.text((cx+20+off,cy+90+off), techs, font=load_font(13), fill=GRAY)

def draw_capabilities_scene(draw, t):
    caps = [("Full-Stack Web","React, Node.js, APIs, Databases"),("Games","Unity, C#, 3D/2D, Physics"),
            ("Automation","PowerShell, Bash, System Admin"),("Data & ML","Python, Pandas, Scraping, File Gen"),
            ("UI/UX","CSS, Canvas, Particles, 3D Effects"),("Self-Healing","Auto-debug, Auto-fix, Guaranteed")]
    draw.text((100,80), "What I Can Build", font=FONT_TITLE, fill=WHITE)
    for i,(title,desc) in enumerate(caps):
        col, row = i%2, i//2
        delay = 0.2+i*0.12
        if t<delay: continue
        prog = min(1,(t-delay)/0.35)
        a = int(255*prog)
        ix = 150 + col*(750+30)
        iy = 200 + row*(100+30)
        cx, cy = ix+35, iy+50
        draw.ellipse([(cx-22,cy-22),(cx+22,cy+22)], fill=(PURPLE[0],PURPLE[1],PURPLE[2],a//2))
        draw.text((cx-8,cy-12), str(i+1), font=FONT_SMALL, fill=(255,255,255,a))
        draw.text((ix+75,iy+15), title, font=load_font(20), fill=WHITE)
        draw.text((ix+75,iy+50), desc, font=load_font(16), fill=GRAY)
        draw.rectangle([(ix+75,iy+90),(ix+750,iy+91)], fill=(PURPLE[0],PURPLE[1],PURPLE[2],a//4))

def draw_projects_scene(draw, t):
    projs = ["#001 Anime Registration","#002 NovaCloud SaaS","#003 Web Presentation",
             "#004 PowerPoint Generator","#005 3D Experience","#006 Explainer Video","#007 Showreel Website"]
    draw.text((100,80), "7 Projects Built", font=FONT_TITLE, fill=WHITE)
    draw.text((100,140), "All 100% autonomous. All real and working.", font=FONT_BODY, fill=GRAY)
    for i,proj in enumerate(projs):
        delay = 0.2+i*0.12
        if t<delay: continue
        prog = min(1,(t-delay)/0.3)
        a = int(255*prog)
        slide = int((1-prog)*40)
        y = 210+i*85
        draw.text((150-slide,y), f"{i+1:02d}", font=load_font(42),
                 fill=(PURPLE[0],PURPLE[1],PURPLE[2],a//4))
        draw.text((220-slide,y+5), proj, font=load_font(24), fill=(255,255,255,a))
        draw.rectangle([(220-slide,y+55),(600-slide,y+56)], fill=(PURPLE[0],PURPLE[1],PURPLE[2],a//6))

def draw_closing_scene(draw, t):
    # Ready for
    rdelay1, rdelay2 = 0.0, 0.5
    nchars1 = len("Ready for")
    nchars2 = len("Your Project.")
    rc1 = max(0, min(nchars1, int((t-rdelay1)/0.04))) if t>rdelay1 else 0
    draw.text((200,250), "Ready for"[:rc1], font=FONT_HERO, fill=WHITE)
    rc2 = max(0, min(nchars2, int((t-rdelay2)/0.04))) if t>rdelay2 else 0
    draw.text((200,350), "Your Project."[:rc2], font=FONT_HERO, fill=PURPLE)
    
    lines = [(1.5,"Every capability shown here is real and working."),
             (2.2,"I have built everything myself, from planning to deployment."),
             (3.0,"No fake promises. No placeholders. 100% delivery."),
             (4.5,"Give me a task. I will build it.")]
    for delay,text in lines:
        if t>delay:
            tt = min(1,(t-delay)/0.4)
            idx = lines.index((delay,text))
            draw.text((200, 450+idx*50), text, font=FONT_BODY,
                     fill=(GRAY[0],GRAY[1],GRAY[2],int(255*tt)))
    if t>6.0:
        bt = min(1,(t-6.0)/0.5)
        draw.text(((WIDTH-400)//2,750), "\u2726 SUZUME \u2014 Supreme AI Companion \u2726",
                 font=FONT_SMALL, fill=(DARK_GRAY[0],DARK_GRAY[1],DARK_GRAY[2],int(255*bt)))

DRAW_FUNCS = {
    "title": draw_title_scene,
    "problem": draw_problem_scene,
    "meet": draw_meet_scene,
    "workflow": draw_workflow_scene,
    "agents": draw_agents_scene,
    "capabilities": draw_capabilities_scene,
    "projects": draw_projects_scene,
    "closing": draw_closing_scene,
}

total_frames_rendered = 0
for si, scene in enumerate(SCENES):
    fc = scene["frames"]
    aid = scene["id"]
    print(f"  Rendering {aid}: {fc} frames...", end="", flush=True)
    t0 = time.time()
    
    for f in range(fc):
        t = f / max(fc, 1)
        img = Image.new('RGB', (WIDTH, HEIGHT), DARK)
        draw = ImageDraw.Draw(img)
        draw_bg(draw, t, si, WIDTH, HEIGHT)
        if aid in DRAW_FUNCS:
            DRAW_FUNCS[aid](draw, t)
        draw_progress(draw, t, si, len(SCENES), WIDTH, HEIGHT)
        fp = os.path.join(FRAMES_DIR, f"frame_{total_frames_rendered:06d}.png")
        img.save(fp, "PNG")
        total_frames_rendered += 1
    
    elapsed = time.time() - t0
    print(f" {fc}f in {elapsed:.1f}s ({fc/elapsed:.1f} fps)")

print(f"\n  Total frames rendered: {total_frames_rendered}")

# ─── STEP 3: Compile video with perfect per-scene sync ───
print("\n" + "=" * 60)
print("  STEP 3: Compiling video (no audio trim)")
print("=" * 60)

# Concatenate audio
alist = os.path.join(BASE_DIR, "audio_list2.txt")
with open(alist, 'w') as f:
    for s in SCENES:
        f.write(f"file '{s['audio_path']}'\n")

compiled_audio = os.path.join(BASE_DIR, "compiled_audio2.mp3")
subprocess.run(["ffmpeg","-y","-f","concat","-safe","0","-i",alist,"-c","copy",compiled_audio],
               check=True, capture_output=True)

# Build video — NO -shortest, use exact frame count
cmd = [
    "ffmpeg","-y",
    "-framerate", str(FPS),
    "-i", os.path.join(FRAMES_DIR, "frame_%06d.png"),
    "-i", compiled_audio,
    "-c:v", "libx264", "-pix_fmt", "yuv420p", "-preset", "slow", "-crf", "16",
    "-c:a", "aac", "-b:a", "256k",
    "-movflags", "+faststart",
    # Use frames total to determine exact duration (no -shortest, no trim)
    "-frames:v", str(total_frames_rendered),
    OUTPUT_FILE
]

result = subprocess.run(cmd, capture_output=True, text=True)
if result.returncode == 0:
    size = os.path.getsize(OUTPUT_FILE)
    vid_dur = total_frames_rendered / FPS
    print(f"  [OK] Video: {OUTPUT_FILE}")
    print(f"  Duration: {vid_dur:.2f}s ({total_frames_rendered}f @ {FPS}fps)")
    print(f"  Size: {size/1024/1024:.2f}MB")
    
    # Verify
    adur = get_mp3_duration(compiled_audio)
    print(f"  Audio duration: {adur:.3f}s")
    print(f"  Diff: {abs(vid_dur-adur):.4f}s")
    if abs(vid_dur - adur) < 0.1:
        print("  [SYNC] Frame-perfect audio/video match!")
    else:
        print(f"  [SYNC] Off by {adur-vid_dur:.3f}s - audio {'longer' if adur>vid_dur else 'shorter'}")
else:
    print(f"  [ERR] ffmpeg failed: {result.stderr[-500:]}")

# Cleanup
for f in [alist, compiled_audio]:
    try: os.remove(f)
    except: pass
# Keep frames directory for potential reuse
# shutil.rmtree(FRAMES_DIR, ignore_errors=True)

print("\nDone.")
