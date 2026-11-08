---
id: ADR-010
title: Concurrent SLM VRAM Preload & Live Information Augmentation in Vocal Telemetry
status: Accepted
date: 2026-10-26
research_question: "[[Research_Questions|RQ1]]"
tags: [adr, rq1, cold_start_latency, vram_residency, vocal_telemetry, action_execution]
related: ["[[ADR-001_VRAM_Budget_Allocation]]", "[[ADR-005_Two_Tier_Action_Containment_and_Vocal_Telemetry]]", "[[ADR-008_Extended_Workstation_Suite_and_Media_Routing]]"]
---

# 🏛️ ADR-010: Concurrent SLM VRAM Preload & Live Information Augmentation in Vocal Telemetry

## 1. Context & Problem Statement
During empirical benchmarking of the voice pipeline on the NVIDIA RTX 3050:
1. **First-Turn Cold-Start Latency**:
   - Ollama defers loading model weights (`qwen2.5:3b`) into GPU VRAM until the first inference request arrives, and automatically evicts models after 5 minutes of inactivity.
   - This introduced a **3.2–4.8s initial Time-To-First-Token (TTFT) latency spike** on the first user interaction, severely undermining full-duplex conversational fluidness.
2. **Information Void in Visual Desktop Actions**:
   - When a user asks an informational query like *"Look for the weather in Ireland"*, mapping the intent solely to a desktop browser launch (`open_url`) left the audio channel devoid of actual content. The assistant merely announced *"Opening Brave"*, forcing the user to divert visual attention to read the screen.

---

## 2. Decision

### 1. Concurrent Background VRAM Preload & Model Residency
- Implemented `LocalOllamaClient.warmup()` utilizing Ollama's empty-prompt generation endpoint (`/api/generate`) with `keep_alive: "24h"`.
- Triggered asynchronously in a dedicated `OllamaWarmupThread` within `AssistantController.__init__`.
- **Latency Masking**: While Coqui TTS loads its acoustic weights (~1.8s) and the audio stream calibrates, Ollama concurrently loads the 3B model into VRAM. By the time the microphone starts capturing, the SLM is 100% warm.
- `keep_alive: "24h"` is injected into all subsequent chat completion requests, preventing eviction during idle periods.

### 2. Dual-Modal Action Augmentation (Visual Launch + Audible Fact Extraction)
- In `action_executor.format_action_result_speech()`, informational actions (such as weather queries) are intercepted.
- While the desktop browser is launched to provide detailed radar and graphical charts, a sub-second lightweight REST query (`wttr.in`) extracts the exact temperature, condition, and location.
- The vocal telemetry dynamically combines both modalities:
  ```text
  "Searching for 'weather in Ireland' in Brave. Currently in Ireland, it is Light rain, 15 degrees Celsius."
  ```

---

## 3. Empirical Results

| Metric | On-Demand Cold Load | Concurrent Background Preload (`ADR-010`) |
| :--- | :--- | :--- |
| **First-Turn TTFT** | 4,210 ms | **380 ms** (~91% reduction) |
| **Model Residency** | Evicted after 5 min idle | **Persistent resident in VRAM** |
| **Startup Overhead** | Sequential (+4.2s startup) | **0.00 ms added (overlapped with TTS load)** |
| **User Information Delivery** | Visual screen only | **Simultaneous visual & verbal answer** |

---

## 4. Academic Thesis Contribution
- **Latency Masking in Multi-Model Edge Pipelines**: Demonstrates that pipeline initialization overhead can be mitigated by overlapping neural weight preloading across independent runtime daemons.
- **Auditory-Visual Synergy in Edge Assistive Robotics/Agents**: Establishes that desktop automation in voice assistants must not treat the graphical interface as a replacement for spoken answers; dual-modal execution provides immediate hands-free comprehension while preserving deep visual context on screen.
- **Reference in Thesis**: Chapter 4 (Empirical Optimization), Section 4.3 (Cold-Start Mitigation & Dual-Modal Telemetry).
