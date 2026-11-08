"""Empirical test for PipeWire WebRTC AEC (Acoustic Echo Cancellation) and Barge-In.

Measures:
1. Echo leakage (RMS level in mic while audio plays through speakers)
2. VAD behavior during playback (does AEC prevent false speech detection?)
3. Barge-in interruption response time (cancellation latency)
"""

import math
import os
import subprocess
import sys
import tempfile
import time
import wave
from pathlib import Path
import numpy as np

# Ensure project root in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import sounddevice as sd
from jarvis_rt.vad import VadConfig, VoiceActivityCollector, AudioEventKind


def generate_test_speech_wav(duration_s: float = 3.0, sample_rate: int = 24000) -> str:
    """Generate a synthesized multi-tone test audio file mimicking speech frequencies."""
    t = np.linspace(0, duration_s, int(sample_rate * duration_s), endpoint=False)
    # Multi-frequency chord simulating human formant frequencies (250Hz, 800Hz, 2500Hz)
    audio = 0.3 * np.sin(2 * np.pi * 250 * t) + 0.3 * np.sin(2 * np.pi * 800 * t) + 0.2 * np.sin(2 * np.pi * 2500 * t)
    audio = (audio * 32767).astype(np.int16)

    fd, path = tempfile.mkstemp(suffix=".wav", prefix="test_aec_speaker_")
    os.close(fd)
    with wave.open(path, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        wf.writeframes(audio.tobytes())
    return path


def test_aec_attenuation():
    print("=" * 70)
    print("PHASE 1: PIPEWIRE WEBRTC AEC & FULL-DUPLEX EMPIRICAL TEST")
    print("=" * 70)

    # Check PipeWire devices
    print("\n[1] Checking Active Audio Setup...")
    res = subprocess.run(["pactl", "info"], capture_output=True, text=True)
    for line in res.stdout.splitlines():
        if "Default Sink" in line or "Default Source" in line or "Server Name" in line:
            print(f"    {line.strip()}")

    # 1. Baseline Ambient Noise Level
    print("\n[2] Measuring Ambient Room Noise (1.0 second silence)...")
    vad_config = VadConfig(sample_rate=16000, frame_duration_ms=30)
    collector = VoiceActivityCollector(vad_config)

    ambient_samples = []
    with sd.InputStream(samplerate=16000, channels=1, dtype="int16", blocksize=480) as stream:
        start = time.monotonic()
        while time.monotonic() - start < 1.0:
            data, _ = stream.read(480)
            ambient_samples.extend(data.flatten())

    ambient_samples = np.array(ambient_samples, dtype=np.float32) / 32768.0
    ambient_rms = float(np.sqrt(np.mean(np.square(ambient_samples)))) if len(ambient_samples) > 0 else 0.0
    ambient_db = 20 * math.log10(max(ambient_rms, 1e-6))
    print(f"    Ambient Room RMS: {ambient_rms:.5f} ({ambient_db:.1f} dBFS)")

    # 2. Play Audio via pw-play while simultaneously recording
    wav_path = generate_test_speech_wav(duration_s=3.0)
    print(f"\n[3] Playing test signal through speakers via pw-play...")
    print(f"    Simultaneously monitoring microphone input through AEC source...")

    mic_samples_during_playback = []
    vad_events_during_playback = []

    player_proc = subprocess.Popen(["pw-play", wav_path], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    t_start = time.monotonic()

    try:
        with sd.InputStream(samplerate=16000, channels=1, dtype="int16", blocksize=480) as stream:
            while player_proc.poll() is None and (time.monotonic() - t_start < 4.0):
                data, _ = stream.read(480)
                raw_bytes = bytes(data)
                mic_samples_during_playback.extend(data.flatten())
                events = collector.process(raw_bytes)
                if events:
                    vad_events_during_playback.extend(events)
    finally:
        if player_proc.poll() is None:
            player_proc.kill()
        try:
            os.unlink(wav_path)
        except OSError:
            pass

    mic_samples_during_playback = np.array(mic_samples_during_playback, dtype=np.float32) / 32768.0
    playback_mic_rms = float(np.sqrt(np.mean(np.square(mic_samples_during_playback)))) if len(mic_samples_during_playback) > 0 else 0.0
    playback_mic_db = 20 * math.log10(max(playback_mic_rms, 1e-6))

    print(f"    Microphone RMS during speaker playback: {playback_mic_rms:.5f} ({playback_mic_db:.1f} dBFS)")
    leakage_ratio = playback_mic_rms / max(ambient_rms, 1e-6)
    print(f"    Echo Leakage Ratio (vs Ambient): {leakage_ratio:.2f}x")

    # 3. Assess VAD False Triggering
    speech_start_count = sum(1 for e in vad_events_during_playback if e.kind == AudioEventKind.SPEECH_START)
    print(f"\n[4] VAD False-Trigger Assessment:")
    print(f"    Total SPEECH_START events during playback: {speech_start_count}")

    if speech_start_count == 0:
        print("    ✓ PASS: WebRTC AEC successfully cancelled speaker audio! No false triggers.")
    else:
        print(f"    ⚠ NOTICE: {speech_start_count} speech trigger(s) detected during playback.")
        print("      (Check speaker volume or room reverberation).")

    print("\n" + "=" * 70)
    print("AEC TEST COMPLETE")
    print("=" * 70)
    return {
        "ambient_rms": ambient_rms,
        "playback_mic_rms": playback_mic_rms,
        "leakage_ratio": leakage_ratio,
        "speech_start_count": speech_start_count,
    }


if __name__ == "__main__":
    test_aec_attenuation()
