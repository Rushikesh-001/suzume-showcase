"""
Cinematic BGM Generator for Suzume Reel
Generates an emotional, goosebumps-inducing soundtrack using pure synthesis.
"""
import numpy as np
import struct
import os
import math

SAMPLE_RATE = 48000
DURATION = 80  # seconds

def save_wav(filename, data, sample_rate=SAMPLE_RATE):
    """Save numpy array as WAV file."""
    data = np.clip(data, -1.0, 1.0)
    data_int = (data * 32767).astype(np.int16)
    with open(filename, 'wb') as f:
        # RIFF header
        f.write(b'RIFF')
        f.write(struct.pack('<I', 36 + len(data_int) * 2))
        f.write(b'WAVE')
        # fmt chunk
        f.write(b'fmt ')
        f.write(struct.pack('<I', 16))  # chunk size
        f.write(struct.pack('<H', 1))   # PCM
        f.write(struct.pack('<H', 1))   # mono
        f.write(struct.pack('<I', sample_rate))
        f.write(struct.pack('<I', sample_rate * 2))  # byte rate
        f.write(struct.pack('<H', 2))   # block align
        f.write(struct.pack('<H', 16))  # bits per sample
        # data chunk
        f.write(b'data')
        f.write(struct.pack('<I', len(data_int) * 2))
        f.write(data_int.tobytes())

def generate_bgm(duration=DURATION, sr=SAMPLE_RATE):
    """Generate a cinematic emotional soundtrack."""
    t = np.linspace(0, duration, int(sr * duration), endpoint=False)
    audio = np.zeros_like(t)
    
    # === STRUCTURE ===
    # 0-10s: Soft pad intro (mysterious, building)
    # 10-25s: Arpeggios enter (hope, emotion)
    # 25-40s: Full arrangement (power, grandeur)
    # 40-55s: Breakdown + build (introspection -> climax)
    # 55-70s: Climax (goosebumps moment)
    # 70-75s: Resolution (soft ending)
    
    # 1. Ambient Pad - detuned saw waves with slow LFO
    pad_notes = [55.0, 65.41, 73.42, 82.41, 98.0, 110.0]  # A1, C2, D2, E2, G2, A2
    pad = np.zeros_like(t)
    for note in pad_notes:
        for detune in [-0.3, 0, 0.3]:
            tone = np.sin(2 * np.pi * (note + detune) * t)
            # Add harmonics for richness
            tone += 0.3 * np.sin(2 * np.pi * (note + detune) * 2 * t)
            tone += 0.1 * np.sin(2 * np.pi * (note + detune) * 3 * t)
            # Apply low-pass envelope (soft attack)
            env = 1.0 / (len(pad_notes)) * 0.3
            pad += tone * env
    
    # Slow LFO for movement
    pad_lfo = 0.5 + 0.5 * np.sin(2 * np.pi * 0.08 * t)
    # Volume fade in (0-8s)
    fade_in = np.minimum(t / 8.0, 1.0)
    pad = pad * 0.25 * pad_lfo * fade_in
    
    # 2. Bass Drone - deep sub bass
    bass = np.sin(2 * np.pi * 55.0 * t) * 0.08
    bass += 0.04 * np.sin(2 * np.pi * 27.5 * t)  # subharmonic
    bass_env = np.minimum(1.0, t / 5.0) * np.exp(-t * 0.01)
    bass = bass * bass_env
    
    # 3. Arpeggiated Sequence (emotional rising pattern)
    arp_notes = [261.63, 329.63, 392.00, 440.00, 523.25, 587.33, 659.25, 783.99]  # C4, E4, G4, A4, C5, D5, E5, G5
    arp = np.zeros_like(t)
    arp_speed = 0.25  # quarter notes at 60bpm
    arp_pattern = [0, 1, 2, 3, 4, 5, 6, 7, 6, 5, 4, 3, 2, 1]
    
    for i, note_idx in enumerate(arp_pattern):
        start_time = 8.0 + i * arp_speed * 2  # start after intro
        if start_time > duration - 10:
            break
        note_samples = int(sr * arp_speed * 1.8)
        idx_start = int(start_time * sr)
        idx_end = min(idx_start + note_samples, len(t))
        if idx_start >= len(t):
            break
        n = idx_end - idx_start
        note_t = np.linspace(0, n/sr, n)
        freq = arp_notes[note_idx % len(arp_notes)]
        tone = np.sin(2 * np.pi * freq * note_t)
        # Add harmonics
        tone += 0.3 * np.sin(2 * np.pi * freq * 2 * note_t + 0.5)
        tone += 0.1 * np.sin(2 * np.pi * freq * 3 * note_t + 1.0)
        # Envelope: fast attack, slow decay
        note_env = np.exp(-note_t * 2.5)
        arp[idx_start:idx_end] += tone * 0.15 * note_env
    
    arp_gate = np.maximum(0, np.minimum(1.0, (t - 8.0) / 3.0))
    arp = arp * arp_gate
    
    # 4. Rising Strings (emotion builder) - filtered saw waves
    string_notes = [220.0, 261.63, 329.63, 392.00, 440.00, 523.25, 659.25, 783.99, 1046.50]
    strings = np.zeros_like(t)
    for i, note in enumerate(string_notes):
        start_s = 15.0 + i * 1.5
        if start_s > duration - 15:
            break
        note_samples = int(sr * 3.0)
        idx_start = int(start_s * sr)
        idx_end = min(idx_start + note_samples, len(t))
        if idx_start >= len(t):
            break
        n = idx_end - idx_start
        note_t = t[idx_start:idx_end] - t[idx_start]
        # Saw wave
        saw = 2 * (note_t * note - np.floor(0.5 + note_t * note))
        # Filter (simple moving average for low-pass)
        tone = saw * 0.08
        # Envelope
        env = np.minimum(1.0, note_t * 2.0) * np.exp(-note_t * 0.3)
        strings[idx_start:idx_end] += tone * env
    
    strings_gate = np.maximum(0, np.minimum(1.0, (t - 15.0) / 5.0)) * np.maximum(0, np.minimum(1.0, (duration - t) / 10.0))
    strings = strings * strings_gate * 0.8
    
    # 5. Piano-like chords (emotional weight)
    chord_notes_list = [
        [261.63, 329.63, 392.00],  # C major
        [220.00, 277.18, 329.63],  # A minor  
        [246.94, 311.13, 369.99],  # B minor
        [293.66, 369.99, 440.00],  # D major
        [261.63, 329.63, 392.00],  # C major
        [196.00, 246.94, 293.66],  # G major
        [174.61, 220.00, 261.63],  # F major
        [261.63, 329.63, 392.00],  # C major (resolution)
    ]
    chord_times = [10, 18, 26, 34, 42, 50, 58, 66]
    
    piano = np.zeros_like(t)
    for chord_idx, (notes, start_s) in enumerate(zip(chord_notes_list, chord_times)):
        for freq in notes:
            idx_start = int(start_s * sr)
            if idx_start >= len(t):
                break
            dur = 7.0
            idx_end = min(idx_start + int(sr * dur), len(t))
            n = idx_end - idx_start
            note_t = t[idx_start:idx_end] - t[idx_start]
            # Piano-like: fundamental + harmonics with fast decay
            tone = np.sin(2 * np.pi * freq * note_t)
            tone += 0.5 * np.sin(2 * np.pi * freq * 2 * note_t)
            tone += 0.25 * np.sin(2 * np.pi * freq * 3 * note_t)
            tone += 0.125 * np.sin(2 * np.pi * freq * 4 * note_t)
            # Percussive attack + slow decay
            env = 0.7 * np.exp(-note_t * 0.8) + 0.3 * np.exp(-note_t * 0.15)
            velocity = 0.08 + (0.04 if chord_idx % 2 == 0 else 0)
            piano[idx_start:idx_end] += tone * env * velocity
    
    # 6. Climax - Build to epic finale (55-70s)
    climax = np.zeros_like(t)
    climax_start = 50.0
    climax_t = t[int(climax_start * sr):] - climax_start
    if len(climax_t) > 0:
        # Big reese-like bass
        for detune in [-5, 0, 5]:
            tone = np.sin(2 * np.pi * (55.0 + detune) * climax_t)
            tone += 0.5 * np.sin(2 * np.pi * (55.0 + detune) * 2 * climax_t * 1.01)
            idx_start = int(climax_start * sr)
            idx_end = min(idx_start + len(climax_t), len(t))
            n = len(tone[:idx_end - idx_start])
            climax[idx_start:idx_start+n] += tone[:n] * 0.12
        
        # High shimmer
        shimmer = np.sin(2 * np.pi * 440.0 * climax_t * 3) * 0.03
        shimmer_env = np.minimum(1.0, climax_t * 0.5) * np.exp(-np.maximum(0, climax_t - 12.0) * 0.5)
        idx_start = int(climax_start * sr)
        idx_end = min(idx_start + len(shimmer), len(t))
        n = len(shimmer[:idx_end - idx_start])
        climax[idx_start:idx_start+n] += shimmer[:n] * shimmer_env[:n]
    
    climax_gate = np.maximum(0, np.minimum(1.0, (t - 48.0) / 4.0)) * np.maximum(0, np.minimum(1.0, (duration - t) / 8.0))
    climax = climax * climax_gate
    
    # 7. Percussion - subtle, building
    kick_times = [4.0, 8.0, 12.0, 16.0, 20.0, 24.0, 28.0, 32.0, 34.0, 36.0, 38.0, 40.0, 42.0, 44.0, 46.0, 48.0, 50.0, 52.0, 54.0, 56.0, 58.0, 60.0, 62.0, 64.0, 66.0, 68.0, 70.0]
    percussion = np.zeros_like(t)
    for kt in kick_times:
        if kt >= duration:
            break
        idx = int(kt * sr)
        if idx >= len(t):
            break
        n = min(int(sr * 0.15), len(t) - idx)
        if n <= 0:
            continue
        k_t = np.linspace(0, n/sr, n)
        # Kick: sine sweep
        kick = np.sin(2 * np.pi * (80.0 - 40.0 * k_t) * k_t)
        kick_env = np.exp(-k_t * 30.0)
        percussion[idx:idx+n] += kick * 0.2 * kick_env
    
    # Hi-hats (softer)
    hat_times = np.arange(8.0, duration - 5, 0.5)
    for ht in hat_times:
        idx = int(ht * sr)
        if idx >= len(t):
            break
        n = min(int(sr * 0.05), len(t) - idx)
        if n <= 0:
            continue
        h_t = np.linspace(0, n/sr, n)
        hat = np.sin(2 * np.pi * 8000 * h_t) * np.exp(-h_t * 200.0)
        percussion[idx:idx+n] += hat * 0.04
    
    # === MIX ===
    audio += pad * 0.5
    audio += bass * 0.6
    audio += arp * 0.5
    audio += strings * 0.35
    audio += piano * 0.4
    audio += climax * 0.5
    audio += percussion * 0.5
    
    # === MASTER ===
    # Soft limiter
    max_val = np.max(np.abs(audio))
    if max_val > 0.95:
        audio = audio / max_val * 0.95
    
    # Fade in/out
    fade_len = int(sr * 1.5)
    audio[:fade_len] *= np.linspace(0, 1, fade_len)
    audio[-fade_len:] *= np.linspace(1, 0, fade_len)
    
    return audio

if __name__ == "__main__":
    print("Generating cinematic BGM...")
    bgm = generate_bgm()
    save_wav("bgm_cinematic.wav", bgm)
    print(f"Done! Duration: {len(bgm)/SAMPLE_RATE:.1f}s")
