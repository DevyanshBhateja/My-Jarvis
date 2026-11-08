---
id: DRAFT-002
title: Thesis Chapter Draft: Practical Engineering Challenges & Negative Results
tags: [thesis-draft, failure-modes, chapter4, discussion]
related: ["[[00_Map_of_Content]]", "[[PRB-001_VAD_Self_Triggering_Acoustic_Feedback]]", "[[PRB-002_Whisper_Short_Utterance_Hallucination]]", "[[PRB-003_XTTS_VRAM_Contention_on_4GB_GPU]]"]
---

# 📝 Thesis Draft: Chapter 4/5 — Engineering Challenges, Negative Results & Failure Modes

*(Ready for inclusion into Bachelor's Thesis report)*

## 4.1 Acoustic Echo & The Limits of Software Muting
A core design requirement of full-duplex conversational systems is continuous listening during assistant speech. Initial iterations revealed severe acoustic feedback: the microphone ingested speaker playback, prompting the VAD to trigger false barge-in events within 200ms of utterance start (detailed in [[PRB-001_VAD_Self_Triggering_Acoustic_Feedback]]).

Attempting to resolve this via software microphone muting (`mic.pause()`) proved to be a false solution: while eliminating echo, it reduced the system to a half-duplex walkie-talkie and rendered mid-sentence user interruptions physically impossible. Empirical testing proved that true full-duplex communication requires system-level Acoustic Echo Cancellation (PipeWire WebRTC AEC), which continuously correlates and subtracts the reference speaker signal from the microphone input before signal digitalization reaches the application layer.

---

## 4.2 ASR Hallucinations on Edge Confirmation Tokens
In desktop automation, voice confirmation dialogues require high precision on monosyllabic words (*"yes"*, *"no"*). Standard Whisper models, optimized for long-form speech transcription, exhibited frequent hallucinations when transcribing short audio bursts under 500ms (see [[PRB-002_Whisper_Short_Utterance_Hallucination]]).

Two critical failure modes were identified:
1. **Consonant Clipping**: Overly aggressive VAD lead-in trimming removed initial plosive consonants, resulting in empty transcripts.
2. **Autoregressive Hallucination**: Enabling `condition_on_previous_text=True` caused Whisper to repeat phrases from earlier dialogue turns. Resolving this required enforcing 300ms pre-padding, disabling context conditioning, and applying digital audio peak normalization prior to model inference.

---

## 4.3 VRAM Contention on 4GB Edge Workstations
Consumer-grade laptops featuring the NVIDIA RTX 3050 impose an unyielding 4096 MB VRAM ceiling. While modern diffusion and autoregressive TTS models (such as Coqui XTTS v2) offer superior voice cloning fidelity, their ~1.6 GB memory footprint, combined with local SLM execution, leaves less than 250 MB of headroom. Under standard desktop multitasking (e.g., opening a browser window via `CMD-01`), the display server requested GPU buffer allocations that routinely triggered fatal CUDA Out-Of-Memory exceptions (see [[PRB-003_XTTS_VRAM_Contention_on_4GB_GPU]]).

The resolution required adopting a dual-model TTS strategy: deploying lightweight non-autoregressive models (Coqui VITS, ~300 MB) for real-time memory stability while preserving XTTS v2 strictly as an isolated, off-line comparison benchmark.

---

## 4.4 Desktop Automation Barriers Under Wayland Security Architecture
In modern Linux distributions (Fedora Workstation with GNOME/Mutter), legacy X11 synthetic input injection utilities (`pyautogui.hotkey('alt', 'f4')`) fail due to Wayland's strict client isolation (see [[PRB-015_Wayland_Synthetic_Input_Portal_and_Dynamic_Volume_Whitelist]]). When the assistant attempted to simulate keystrokes to close active windows, Mutter intercepted the unprivileged virtual input stream and generated a blocking security dialog: *`Remote Desktop: Allow Remote Interaction`*.

This revealed an essential theoretical takeaway: voice agents on modern display servers cannot rely on keystroke synthesis. We replaced synthetic events with deterministic process lifecycle management (`RECENT_PROCESSES` tracking stack with audited SIGTERM dispatch), achieving instant, zero-permission window closure.

---

## 4.5 Host Environment Containment & Self-Preservation Invariants
During interactive desktop automation, an autonomous voice agent with system execution capabilities risks process suicide if targeting criteria are underspecified (see [[PRB-016_Terminal_Suicide_Process_Teardown_and_Cloud_NIM_90B_Pinning]]). In an empirical test where the user asked to close a browser window, an untracked process fallback iterated through approved process names and executed `pkill -f ptyxis`, terminating the host terminal emulator running both the assistant and the IDE.

To address this, the architecture implements a strict **Process Self-Preservation Invariant**:
1. Critical development and host terminal binaries (`ptyxis`, `gnome-terminal`, `bash`, `python`, `code`) are permanently immunized against termination in `action_executor.py`.
2. Target application resolution requires explicit application tagging (e.g. `close_app("brave")`), preventing indiscriminate process sweeping.

---

## 4.6 Non-Daemon Worker Threads and PortAudio C-Stream Shutdown Deadlocks
Graceful teardown in concurrent full-duplex systems is notoriously vulnerable to thread synchronization deadlocks (see [[PRB-007_Non_Daemon_Thread_Deadlock_SIGINT]] and [[PRB-014_Stdin_Deadlock_on_Window_Close_and_PortAudio_Shutdown_Freeze]]). 

When background audio polling threads were initialized as non-daemon workers, terminating the master process via SIGINT or user speech left C-level PortAudio (`sounddevice`) input streams blocked in blocking read loops. Because native C extensions can bypass Python's signal handler loop, the process remained indefinitely suspended in memory. Resolving this required strict daemonization across all audio and inference threads, explicit PortAudio stream abortion handlers (`stream.abort()`), and non-blocking I/O checks before entering sleep intervals.
