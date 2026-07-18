"""
Generate premium TTS voiceover using edge-tts.
Microsoft Jenny (en-US-JennyNeural) - natural, warm female voice.
7 segments covering: opening, about, capabilities, demos, process, team, finale
"""
import asyncio
import edge_tts
import os

OUTPUT_DIR = os.path.dirname(os.path.abspath(__file__))

segments = [
    {
        "text": "In a world where building software means managing complexity, Suzume breaks through. Orchestrating seven AI agents to construct complete applications, from databases to deployment. No shortcuts. No placeholders. Just production ready code.",
        "filename": "tts_01.wav"
    },
    {
        "text": "Suzume is a supreme AI companion. A master software architect and system automation force. I build web applications, 3D experiences, automation systems, and AI pipelines from natural language descriptions. Seven specialist agents work under my orchestration, each handling their domain of expertise.",
        "filename": "tts_02.wav"
    },
    {
        "text": "Full stack web apps with React and Next.js. 3D interactive experiences with Three.js and WebGL. Game development with Unity. System automation with PowerShell. AI pipelines with Python and machine learning. I cover every layer of the stack from concept to deployment.",
        "filename": "tts_03.wav"
    },
    {
        "text": "Five working demos show what I can build. A responsive Snake game with touch controls and high score tracking. An interactive 3D demo with seven scenes and orbital camera controls. A premium SaaS landing page with particle systems and glassmorphism design. A pixel art creator with undo, redo and PNG export. A live markdown editor with syntax toolbar and instant preview.",
        "filename": "tts_04.wav"
    },
    {
        "text": "Every project follows the same workflow. You give a task in natural language. I analyze and design the architecture. Seven agents work in parallel. Every file is tested. Every bug is fixed autonomously. The result is delivered complete, deployed, and working. No human intervention needed.",
        "filename": "tts_05.wav"
    },
    {
        "text": "My team includes seven specialists. Worker JS for frontend and Node APIs. Worker Python for backend and data processing. Worker Unity for 3D games and HDRP rendering. Worker Sys for system automation. Worker Web for CSS and UI design. Builder for compilation and dependency management. Reviewer for code quality and security audits.",
        "filename": "tts_06.wav"
    },
    {
        "text": "Your vision, built with precision. Your project, delivered with quality. Your ideas, brought to life. This is Suzume. Supreme AI companion. Master software architect. System automation force. Welcome to what is possible.",
        "filename": "tts_07.wav"
    }
]

async def generate_all():
    for seg in segments:
        out_path = os.path.join(OUTPUT_DIR, seg["filename"])
        print(f"Generating: {seg['filename']}...")
        communicate = edge_tts.Communicate(
            seg["text"],
            "en-US-JennyNeural",
            rate="-8%",
            volume="+20%",
            pitch="-3Hz"
        )
        await communicate.save(out_path)
        print(f"  Saved ({os.path.getsize(out_path)//1024}KB)")

if __name__ == "__main__":
    asyncio.run(generate_all())
