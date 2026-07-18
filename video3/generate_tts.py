"""
Ultra-compact TTS segments. Each under 10 seconds. No overlap.
"""
import asyncio
import edge_tts
import os

OUTPUT_DIR = os.path.dirname(os.path.abspath(__file__))

segments = [
    {
        "text": "Suzume directs seven AI agents to build complete applications. From databases to deployment. Production ready, every time.",
        "filename": "tts_01.wav"
    },
    {
        "text": "A supreme AI companion and master architect. Building web apps, 3D experiences, and automation from natural language.",
        "filename": "tts_02.wav"
    },
    {
        "text": "Full stack web with React. 3D with Three.js. Games with Unity. AI with Python. Every layer of the stack.",
        "filename": "tts_03.wav"
    },
    {
        "text": "Five demos built autonomously. A snake game. A 3D experience. A SaaS page. A pixel editor. A markdown tool.",
        "filename": "tts_04.wav"
    },
    {
        "text": "You give a task. I design the architecture. Seven agents work in parallel. Each file tested. Deployed live.",
        "filename": "tts_05.wav"
    },
    {
        "text": "Seven agents. JS for frontend. Python for backend. Unity for games. Sys for automation. Web for design.",
        "filename": "tts_06.wav"
    },
    {
        "text": "Your vision, built with precision. Your project, delivered with quality. Suzume. Supreme AI.",
        "filename": "tts_07.wav"
    }
]

async def generate_all():
    for seg in segments:
        out_path = os.path.join(OUTPUT_DIR, seg["filename"])
        communicate = edge_tts.Communicate(
            seg["text"],
            "en-US-JennyNeural",
            rate="+5%",
            volume="+15%"
        )
        await communicate.save(out_path)
        size_kb = os.path.getsize(out_path) // 1024
        print(f"{seg['filename']}: {size_kb}KB")

if __name__ == "__main__":
    asyncio.run(generate_all())
