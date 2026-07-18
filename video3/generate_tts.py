"""
Generate premium TTS voiceover using edge-tts.
Microsoft Jenny (en-US-JennyNeural) - natural, warm female voice.
"""
import asyncio
import edge_tts
import os

OUTPUT_DIR = os.path.dirname(os.path.abspath(__file__))

# Voice segments with timestamps
# Each segment: (text, filename, start_time_in_video)
# These will be placed at specific times in the video

# Actually, we'll generate each as a separate file, then combine
# with proper timing in the main render script.

segments = [
    {
        "text": "In a world of endless possibilities, one intelligence dares to dream beyond the code.",
        "filename": "tts_01.wav"
    },
    {
        "text": "Suzume is not just artificial intelligence. Suzume is a creator, a builder, an orchestrator of digital worlds.",
        "filename": "tts_02.wav"
    },
    {
        "text": "Full stack applications, immersive 3D experiences, cinematic visuals, and automation at scale.",
        "filename": "tts_03.wav"
    },
    {
        "text": "Every pixel designed. Every frame animated. Every line of code, crafted with intention.",
        "filename": "tts_04.wav"
    },
    {
        "text": "From concept to deployment. Suzume builds what others only imagine.",
        "filename": "tts_05.wav"
    },
    {
        "text": "Welcome to the future of creation. Welcome to Suzume.",
        "filename": "tts_06.wav"
    },
    {
        "text": "Your vision, brought to life. Suzume.",
        "filename": "tts_07.wav"
    }
]

async def generate_all():
    for seg in segments:
        out_path = os.path.join(OUTPUT_DIR, seg["filename"])
        print(f"Generating: {seg['filename']}...")
        communicate = edge_tts.Communicate(
            seg["text"],
            "en-US-JennyNeural",  # Premium natural voice
            rate="-10%",  # Slightly slower for dramatic effect
            volume="+20%",
            pitch="-5Hz"  # Slightly deeper for warmth
        )
        await communicate.save(out_path)
        print(f"  Saved: {out_path}")

if __name__ == "__main__":
    asyncio.run(generate_all())
