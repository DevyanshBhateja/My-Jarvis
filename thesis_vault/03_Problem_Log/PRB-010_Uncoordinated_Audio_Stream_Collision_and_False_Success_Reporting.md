---
id: PRB-010
title: Uncoordinated Audio Stream Collision and False-Success Telemetry Reporting
research_question: "[[RQ1_Concurrency_Pipelining]]"
status: Solved
tags: [problem, failed-attempt, solution, rq1, rq2]
related: ["[[ADR-004_Token_Level_Streaming_TTS_Chunking]]", "[[ADR-005_Two_Tier_Action_Containment_and_Vocal_Telemetry]]", "[[Frozen_Fedora_Commands]]"]
---

# PRB-010: Uncoordinated Audio Stream Collision and False-Success Telemetry Reporting

## 1. Problem Description & Symptoms
During live full-duplex voice testing of system diagnostics and desktop actions on Fedora Linux, two compounding failure modes were identified:

1. **Dual Audio Stream Collision (Overlapping Speech)**:
   - When the user requested memory diagnostics (*"Can you check the memory usage?"*), the conversational LLM streamed an initial verbal response (*"I can assist with CPU and network usage for now. For memory usage, I need to run a different command. Please wait while I check that for you."*) while emitting an action directive: `ACTION: run_command("free -m")`.
   - Instead of waiting for conversational preamble playback to complete or sequencing the response, the assistant began speaking the action result (*"Action completed successfully."*) simultaneously with the preamble.
   - The user heard two distinct synthesized voices talking over each other in an uncoordinated collision.

2. **False-Positive Action Success Reporting (Silent Safety Denials)**:
   - When the user requested maximum volume (*"Turn my volume to max"*), the LLM emitted a command outside the pinned 10 Frozen Fedora Commands (or `wpctl set-volume @DEFAULT_SINK@ 100%`).
   - The security boundary correctly intercepted and blocked the out-of-scope command (`[ACTION SAFETY DENIED] Blocked: shell command ... is outside the 10 Frozen Fedora Commands`).
   - However, the assistant vocally announced: *"Action completed successfully."* No volume adjustment actually took place, misleading the user and violating state transparency.

---

## 2. Failed Attempts & Negative Results (Crucial for Thesis Discussion)

### Attempt 1: Decentralized TTS Invocation in Worker Threads
- **Approach**: In [[ADR-005_Two_Tier_Action_Containment_and_Vocal_Telemetry]], `_action_loop` was granted direct access to `self.tts_client.start_session()` to speak command outputs immediately upon execution.
- **Why it failed technically**:
  - `StreamingCoquiTtsSession` is an autonomous consumer pipeline that spawns a dedicated worker thread and launches a native Linux audio player subprocess (`pw-play`).
  - PipeWire is an asynchronous graph audio server designed to mix concurrent streams without blocking.
  - When `_action_loop` launched a new TTS session while `_converse_loop`'s session was actively playing earlier tokens via `_speak_loop`, two concurrent `pw-play` processes were spawned simultaneously.
  - Furthermore, `_action_loop` overwrote the shared orchestrator pointer `self._current_tts_session = session`. When `_speak_loop` attempted to feed remaining tokens from the conversational queue, it referenced the terminated action session, causing sentence reordering, dropped buffers, and acoustic chaos.

### Attempt 2: Blind String Fallback in Speech Formatter
- **Approach**: `format_action_result_speech(request, raw_output)` parsed specific successful outputs (`hostname -I`, `top`, `upower`) and ended with `return "Action completed successfully."` as a catch-all.
- **Why it failed technically**:
  - `confirm_and_execute()` returns string errors upon policy denial (e.g., `"Safety policy error: Blocked: shell command 'free -m' is outside the 10 Frozen Fedora Commands."`).
  - Because string errors are truthy in Python (`bool(result) == True`), the catch-all branch treated safety rejections and permission denials as successful completions, declaring success for actions that never ran.

---

## 3. Working Solution & Root Cause Analysis

### The Fix
The resolution required a two-part architectural synchronization and error-handling contract:

1. **Centralized Speech Pipeline Serialization via `tts_chunk_queue`**:
   - Stripped all `tts_client.start_session()` logic from `_action_loop`.
   - All spoken telemetry from actions is converted into a standard `TTSChunk(text=spoken, utterance_id=action_req.utterance_id)` and pushed directly into the central, FIFO-ordered `self.tts_chunk_queue`.
   - Instrumented `ActionRequest` with a synchronization event (`done_event: Event`).
   - In `_converse_loop`, after LLM streaming concludes, the thread waits for any `pending_actions` in the utterance to set their `done_event` before posting the end-of-session marker (`None`) into `tts_chunk_queue`.
   - This guarantees that conversational preamble (Chunk 1: *"Please wait while I check that for you"*) and action telemetry (Chunk 2: *"Your local IP address is..."*) are fed strictly sequentially into a single `StreamingCoquiTtsSession`, played by a single `pw-play` subprocess.

2. **Explicit Safety Rejection & Denial Handling**:
   - Updated `format_action_result_speech` to inspect `raw_output` for security blocks, timeouts, and cancellations before formatting:
     ```python
     if "Safety policy error:" in raw_output or "Blocked:" in raw_output:
         return "I cannot execute that command; it is outside my 10 authorized capabilities."
     if "Action cancelled by user" in raw_output or "timed out" in raw_output:
         return "Action was cancelled."
     if "Unknown action:" in raw_output or "Failed to execute" in raw_output:
         return "The action failed to execute."
     ```
   - Enhanced `ChatHistory.system_prompt` to explicitly ground Ollama/Qwen on 5% incremental volume boundaries (`5%+` / `5%-`) and declare memory/disk checks as out-of-scope for the 10 Frozen Fedora Commands.

---

## 4. Academic Thesis Contribution

### Key Takeaways for Edge Workstations:
1. **Asynchronous Audio Server Traps in Multithreaded AI**:
   - Modern Linux audio servers (PipeWire/PulseAudio) provide non-blocking mixing by design. In a full-duplex edge assistant, concurrency between independent system components (LLM inference vs OS action execution) will silently mix colliding audio streams unless audio playback is strictly managed through a single serialized gateway queue.
2. **State Transparency in Autonomous Desktop Agents**:
   - Silent execution failures and false-positive verbal confirmations degrade user trust in autonomous edge assistants. Explicit safety rejection feedback (*"I cannot execute that command..."*) is essential for human-in-the-loop oversight on security-constrained workstations.

### Thesis Mapping:
- **Chapter 3: System Design & Implementation**: Section 3.4 (*Full-Duplex Thread Orchestration and Single-Gateway Audio Serialization*).
- **Chapter 4: Engineering Challenges**: Section 4.5 (*Dual-Stream Audio Collisions and Policy Rejection Feedback*).
