"""Launcher that ensures correct working directory for render."""
import os, sys, subprocess
script_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(script_dir)
print(f"Working directory: {os.getcwd()}")
sys.exit(subprocess.call([sys.executable, os.path.join(script_dir, "render_composited.py")]))
