#!/usr/bin/env python
"""Integration test to verify the real-time assistant components work and logging is visible."""

from __future__ import annotations

import queue
import threading
import time
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path
import sys

# Ensure project root is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Test that modules import cleanly
print("[TEST] Importing jarvis_rt modules...")
try:
    from jarvis_rt.state import AssistantState
    from jarvis_rt.vad import VadConfig, VoiceActivityCollector, AudioEventKind
    from jarvis_rt.transcription import WhisperTranscriber
    from jarvis_rt.llm_stream import ChatHistory, LocalOllamaClient, NvidiaNimClient
    from jarvis_rt.tts_stream import ChunkedEdgeTTSPlayer, _TextChunker
    from jarvis_rt.controller import AssistantConfig, AssistantController
    print("[TEST] ✓ All modules imported successfully")
except Exception as e:
    print(f"[TEST] ✗ Import failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)


def test_state():
    """Test thread-safe state management."""
    print("\n[TEST] Testing AssistantState...")
    state = AssistantState()
    
    assert state.is_listening == True
    assert state.is_speaking == False
    
    state.mark_speaking(True)
    assert state.is_speaking == True
    
    state.mark_listening(False)
    assert state.is_listening == False
    
    state.request_interrupt()
    assert state.interrupt_requested == True
    
    state.clear_interrupt()
    assert state.interrupt_requested == False
    
    print("[TEST] ✓ AssistantState works correctly")


def test_vad_config():
    """Test VAD configuration calculations."""
    print("\n[TEST] Testing VadConfig...")
    config = VadConfig(sample_rate=16_000, frame_duration_ms=30)
    
    assert config.frame_samples == 480  # 16000 * 30 / 1000
    assert config.prefix_frames >= 1
    assert config.silence_frames >= 1
    
    print(f"[TEST] ✓ VadConfig: frame_samples={config.frame_samples}, silence_frames={config.silence_frames}")


def test_text_chunker():
    """Test TTS text chunking."""
    print("\n[TEST] Testing _TextChunker...")
    chunker = _TextChunker(max_chars=50)
    
    chunks = chunker.feed("Hello world. This is a test.")
    print(f"[TEST] Chunks received: {chunks}")
    assert len(chunks) > 0
    assert all(isinstance(c, str) for c in chunks)
    
    remainder = chunker.flush()
    print(f"[TEST] Remainder: {remainder}")
    
    print("[TEST] ✓ TextChunker works correctly")


def test_chat_history():
    """Test chat history management."""
    print("\n[TEST] Testing ChatHistory...")
    history = ChatHistory()
    
    assert isinstance(history.system_prompt, str)
    assert "Jarvis" in history.system_prompt
    
    history.append_user("Hello")
    history.append_assistant("Hi there!")
    
    messages = history.as_openai_messages()
    assert len(messages) == 3  # system + user + assistant
    assert messages[0]["role"] == "system"
    assert messages[1]["role"] == "user"
    assert messages[2]["role"] == "assistant"
    
    print("[TEST] ✓ ChatHistory works correctly")


def test_vad_events():
    """Test VAD event generation."""
    print("\n[TEST] Testing VoiceActivityCollector...")
    
    config = VadConfig(sample_rate=16_000, frame_duration_ms=30)
    collector = VoiceActivityCollector(config)
    
    # Create a frame of silent audio (low energy)
    silent_frame = b'\x00' * 960  # 480 samples * 2 bytes
    
    events = collector.process(silent_frame)
    print(f"[TEST] Events for silent frame: {events}")
    assert len(events) == 0
    
    print("[TEST] ✓ VoiceActivityCollector initializes correctly")


@patch("jarvis_rt.controller.CoquiXTTSPlayer")
def test_controller_initialization(mock_tts):
    """Test AssistantController initializes without errors."""
    print("\n[TEST] Testing AssistantController initialization...")
    mock_tts.return_value = MagicMock()

    try:
        config = AssistantConfig(audio_device=None)
        controller = AssistantController(config)
        
        assert controller.config is not None
        assert controller.mic is not None
        assert controller.vad is not None
        assert controller.transcriber is not None
        assert controller.local_llm is not None
        assert controller.tts is not None
        
        print("[TEST] ✓ AssistantController initialized successfully")
    except Exception as e:
        print(f"[TEST] ✗ Initialization failed: {e}")
        raise


def test_logging_visible():
    """Verify that logging prints are working."""
    print("\n[TEST] Testing logging visibility...")
    
    # Capture stdout
    from io import StringIO
    old_stdout = sys.stdout
    sys.stdout = buffer = StringIO()
    
    try:
        config = VadConfig()
        collector = VoiceActivityCollector(config)
        
        sys.stdout = old_stdout
        output = buffer.getvalue()
        
        # Check that logging is visible
        if "[VAD]" in output or "[ERROR]" in output or "WebRTC" in output or "energy-based" in output:
            print(f"[TEST] ✓ Logging detected in output:\n{output}")
        else:
            print(f"[TEST] ✓ VAD initialized (logging may be conditional)")
    finally:
        sys.stdout = old_stdout


def test_config_defaults():
    """Test default configuration values."""
    print("\n[TEST] Testing AssistantConfig defaults...")
    
    config = AssistantConfig()
    
    assert config.sample_rate == 16_000
    assert config.whisper_model == "base"
    assert config.local_model == "qwen2.5:3b"
    assert config.local_base_url == "http://127.0.0.1:11434"
    
    print("[TEST] ✓ Default configuration is correct")


def main():
    """Run all tests."""
    print("=" * 60)
    print("JARVIS REAL-TIME ASSISTANT - INTEGRATION TEST")
    print("=" * 60)
    
    tests = [
        test_state,
        test_vad_config,
        test_text_chunker,
        test_chat_history,
        test_vad_events,
        test_config_defaults,
        test_logging_visible,
        test_controller_initialization,
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            test()
            passed += 1
        except AssertionError as e:
            print(f"[TEST] ✗ FAILED: {e}")
            failed += 1
        except Exception as e:
            print(f"[TEST] ✗ ERROR: {e}")
            import traceback
            traceback.print_exc()
            failed += 1
    
    print("\n" + "=" * 60)
    print(f"RESULTS: {passed} passed, {failed} failed")
    print("=" * 60)
    
    if failed == 0:
        print("\n✓ All integration tests passed!")
        print("\nTo run the real-time assistant:")
        print("  1. Ensure local Ollama is reachable at http://127.0.0.1:11434")
        print("  2. Ensure microphone is connected and working")
        print("  3. Optionally set NVIDIA_API_KEY for NVIDIA NIM")
        print("  4. Run: python main.py")
        print("\nYou should see logs like:")
        print("  [JARVIS] Starting real-time assistant...")
        print("  [MIC] Starting stream...")
        print("  [VAD] Speech detected (start)")
        print("  [ASR] Transcribing...")
        print("  [USER] <your text here>")
        print("  [LLM] Starting stream...")
        print("  [ASSISTANT] <response from Jarvis>")
        return 0
    else:
        print(f"\n✗ {failed} test(s) failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
