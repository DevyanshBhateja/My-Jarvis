#!/usr/bin/env python
"""Lightweight syntax and logic validation without external dependencies."""

from __future__ import annotations

import ast
import sys
from pathlib import Path


def check_syntax(file_path: Path) -> bool:
    """Check if a Python file has valid syntax."""
    try:
        with open(file_path) as f:
            ast.parse(f.read())
        return True
    except SyntaxError as e:
        print(f"  ✗ Syntax error: {e}")
        return False


def check_logging(file_path: Path) -> list[str]:
    """Find print/logging statements in a file."""
    with open(file_path) as f:
        content = f.read()
    
    logs = []
    for line_no, line in enumerate(content.splitlines(), 1):
        if 'print(' in line and not line.strip().startswith('#'):
            logs.append(f"    Line {line_no}: {line.strip()}")
    return logs


def main():
    print("=" * 70)
    print("JARVIS REAL-TIME ASSISTANT - SYNTAX & LOGGING VALIDATION")
    print("=" * 70)
    
    project_root = Path("/home/dave/Documents/Projects/MY_JARVIS")
    modules = [
        "jarvis_rt/__init__.py",
        "jarvis_rt/controller.py",
        "jarvis_rt/interaction_orchestrator.py",
        "jarvis_rt/coqui_tts.py",
        "jarvis_rt/mic_stream.py",
        "jarvis_rt/vad.py",
        "jarvis_rt/tts_stream.py",
        "jarvis_rt/llm_stream.py",
        "jarvis_rt/transcription.py",
        "jarvis_rt/state.py",
        "jarvis_rt/action_protocol.py",
        "jarvis_rt/action_executor.py",
        "jarvis_rt/system_actions.py",
        "main.py",
        "legacy/listen.py",
        "legacy/speak.py",
        "legacy/jarvis_voice.py",
        "tests/test_integration.py",
    ]
    
    print("\n[1] CHECKING SYNTAX")
    print("-" * 70)
    
    syntax_ok = 0
    syntax_fail = 0
    
    for module in modules:
        file_path = project_root / module
        if file_path.exists():
            if check_syntax(file_path):
                print(f"  ✓ {module}")
                syntax_ok += 1
            else:
                print(f"  ✗ {module}")
                syntax_fail += 1
        else:
            print(f"  ? {module} (not found)")
    
    print(f"\nSyntax check: {syntax_ok} OK, {syntax_fail} FAILED")
    
    print("\n[2] CHECKING LOGGING")
    print("-" * 70)
    
    key_files = [
        ("controller.py", "jarvis_rt/controller.py"),
        ("mic_stream.py", "jarvis_rt/mic_stream.py"),
        ("vad.py", "jarvis_rt/vad.py"),
        ("tts_stream.py", "jarvis_rt/tts_stream.py"),
        ("llm_stream.py", "jarvis_rt/llm_stream.py"),
    ]
    
    total_logs = 0
    
    for name, path in key_files:
        file_path = project_root / path
        logs = check_logging(file_path)
        if logs:
            print(f"\n  {name} ({len(logs)} log points):")
            for log in logs[:5]:  # Show first 5
                print(log)
            if len(logs) > 5:
                print(f"    ... and {len(logs) - 5} more")
            total_logs += len(logs)
    
    print(f"\nTotal logging points found: {total_logs}")
    
    print("\n[3] ARCHITECTURE CHECK")
    print("-" * 70)
    
    # Check that key methods exist in controller and orchestrator
    controller_file = project_root / "jarvis_rt/controller.py"
    orchestrator_file = project_root / "jarvis_rt/interaction_orchestrator.py"
    
    with open(controller_file) as f:
        controller_content = f.read()
    with open(orchestrator_file) as f:
        orchestrator_content = f.read()
    
    combined_content = controller_content + "\n" + orchestrator_content
    
    required_methods = [
        "def run(",
        "def listen_once(",
        "def _listen_loop(",
        "def _converse_loop(",
        "def _speak_loop(",
        "def _action_loop(",
        "def shutdown(",
        "request_interrupt",
    ]
    
    methods_found = 0
    for method in required_methods:
        if method in combined_content:
            print(f"  ✓ {method}")
            methods_found += 1
        else:
            print(f"  ✗ {method}")
    
    print(f"\nMethods found: {methods_found}/{len(required_methods)}")
    
    print("\n[4] COMPONENT CHECK")
    print("-" * 70)
    
    components = {
        "AssistantState (state management)": "jarvis_rt/state.py",
        "VoiceActivityCollector (VAD)": "jarvis_rt/vad.py",
        "MicrophoneStream (audio capture)": "jarvis_rt/mic_stream.py",
        "WhisperTranscriber (transcription)": "jarvis_rt/transcription.py",
        "LocalOllamaClient (LLM streaming)": "jarvis_rt/llm_stream.py",
        "NvidiaNimClient (LLM streaming)": "jarvis_rt/llm_stream.py",
        "ChunkedEdgeTTSPlayer (TTS)": "jarvis_rt/tts_stream.py",
        "AssistantController (orchestration)": "jarvis_rt/controller.py",
    }
    
    components_ok = 0
    for comp_name, comp_file in components.items():
        file_path = project_root / comp_file
        with open(file_path) as f:
            content = f.read()
        
        class_name = comp_name.split(" ")[0]
        if f"class {class_name}" in content:
            print(f"  ✓ {comp_name}")
            components_ok += 1
        else:
            print(f"  ✗ {comp_name}")
    
    print(f"\nComponents: {components_ok}/{len(components)} defined")
    
    print("\n" + "=" * 70)
    print("VALIDATION SUMMARY")
    print("=" * 70)
    
    if syntax_ok == len(modules) and components_ok == len(components) and methods_found == len(required_methods) and total_logs > 0:
        print("\n✓ All checks passed!")
        print("\nThe real-time assistant is ready to run. Next steps:\n")
        print("1. Ensure the local Ollama server is reachable:")
        print("   http://127.0.0.1:11434\n")
        print("   (or set JARVIS_OLLAMA_URL to a different Ollama endpoint)\n")
        print("2. In another terminal, run the voice assistant:")
        print("   cd /home/dave/Documents/Projects/MY_JARVIS")
        print("   source oj-env/bin/activate")
        print("   python main.py\n")
        print("3. You should see output like:")
        print("   [JARVIS] Starting real-time assistant...")
        print("   [MIC] Starting stream: sr=16000Hz...")
        print("   [VAD] Using WebRTC VAD (or energy-based VAD)")
        print("   [JARVIS] Listening for speech...\n")
        print("4. Speak naturally. You should see:")
        print("   [VAD] Speech detected (start)")
        print("   [ASR] Transcribing...")
        print("   [USER] <your transcribed speech>")
        print("   [LLM] Starting stream...")
        print("   [ASSISTANT] <response from Jarvis>\n")
        return 0
    else:
        print(f"\n✗ Some checks failed")
        print(f"  Syntax: {syntax_ok}/{len(modules)-1} OK")
        print(f"  Components: {components_ok}/{len(components)} found")
        print(f"  Logging: {total_logs} points found")
        return 1


if __name__ == "__main__":
    sys.exit(main())
