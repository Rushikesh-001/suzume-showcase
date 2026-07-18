"""Quick test render - 5 seconds only."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from render_cinematic import *

OUTPUT_DIR = os.path.dirname(os.path.abspath(__file__))

print("Testing render...")
scenes_data = [
    {"name": "Opening", "start": 0, "end": 5, "generator": scene_01_opening},
]

def make_frame(t):
    return create_cinematic_frame(t, scenes_data)

video = VideoClip(make_frame, duration=5).with_fps(10)

# Test output
out = os.path.join(OUTPUT_DIR, "test_render.mp4")
video.write_videofile(out, codec="libx264", fps=10, bitrate="5000k",
    ffmpeg_params=["-pix_fmt", "yuv420p"])

size = os.path.getsize(out) / 1024
print(f"✓ Test render: {size:.0f}KB")
print("Full render is safe to proceed!")
