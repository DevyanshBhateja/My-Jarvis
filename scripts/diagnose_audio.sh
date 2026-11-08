#!/bin/bash
# Audio system diagnostic script for Jarvis

echo "========================================"
echo "AUDIO SYSTEM DIAGNOSTIC"
echo "========================================"
echo ""

echo "1. PulseAudio/PipeWire Info:"
echo "-----"
pactl info | grep -E "Server Name|Default Sink|Default Source"
echo ""

echo "2. Available Sinks:"
echo "-----"
pactl list sinks short
echo ""

echo "3. Available Sources (Microphones):"
echo "-----"
pactl list sources short
echo ""

echo "4. ACTIVE PLAYBACK (sink-inputs) - should show ffplay/pw-play/paplay:"
echo "-----"
pactl list sink-inputs short
if [ $? -ne 0 ]; then
    echo "(No active sink-inputs)"
fi
echo ""

echo "5. ACTIVE RECORDING (source-outputs) - should show Coqui TTS mic:"
echo "-----"
pactl list source-outputs short
if [ $? -ne 0 ]; then
    echo "(No active source-outputs)"
fi
echo ""

echo "6. Source States (check for SUSPENDED):"
echo "-----"
pactl list sources | grep -E "Name:|State:"
echo ""

echo "7. Check if ffplay/pw-play/paplay are running:"
echo "-----"
ps aux | grep -E "ffplay|pw-play|paplay" | grep -v grep
if [ $? -ne 0 ]; then
    echo "(No audio player processes found)"
fi
echo ""

echo "8. Test manual playback with available WAV:"
echo "-----"
WAV_FILE=$(ls -t /tmp/jarvis_coqui_*.wav 2>/dev/null | head -1)
if [ -n "$WAV_FILE" ]; then
    echo "Found WAV file: $WAV_FILE"
    echo "File size: $(stat -c%s "$WAV_FILE") bytes"
    echo ""
    echo "Testing playback with pw-play:"
    timeout 3 pw-play "$WAV_FILE" 2>&1 || echo "(pw-play not available or failed)"
    echo ""
    echo "Testing playback with paplay:"
    timeout 3 paplay "$WAV_FILE" 2>&1 || echo "(paplay not available or failed)"
else
    echo "No WAV files found in /tmp/jarvis_coqui_*"
fi
echo ""

echo "========================================"
echo "END DIAGNOSTIC"
echo "========================================"
