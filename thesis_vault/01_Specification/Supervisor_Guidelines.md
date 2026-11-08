---
id: SPEC-001
title: Supervisor Guidelines & Feedback Checklist
tags: [specification, supervisor, checklist, thesis]
related: ["[[00_Map_of_Content]]", "[[Pinned_Models_and_Licenses]]", "[[Frozen_Fedora_Commands]]"]
---

# 📋 Supervisor Guidelines & Feedback Checklist

This document tracks all direct feedback from the thesis supervisor and how each item is satisfied in the codebase and research documentation.

## Direct Feedback Items

| # | Supervisor Feedback | Status | Implementation in Repository | Relevant Vault Note |
| :- | :--- | :--- | :--- | :--- |
| **1** | **Model versions**: *"narrow all of them down, it can be anything"* | ✅ COMPLETED | Pinned Whisper `base.en`, Ollama `qwen2.5:3b-instruct-q4_K_M`, Coqui `vits_ljspeech` & `xtts_v2`, NVIDIA NIM `llama-3.3-70b-instruct`. | [[Pinned_Models_and_Licenses]] |
| **2** | **Limited commands in Fedora**: *"make a list what i can do, test that nothing more"* | ✅ COMPLETED | Created frozen 10-command benchmark catalog across 3 categories (apps, workspace/audio, system stats). | [[Frozen_Fedora_Commands]] |
| **3** | **Minimal testing**: *"test time and accuracy, mention the problems"* | ✅ COMPLETED | Defined precise TTFT, TTFA, and accuracy metrics. Created dedicated problem log recording failed attempts. | [[Benchmarking_Protocol_and_Metrics]], [[Draft_Problems_and_Failure_Modes]] |
| **4** | **Detailed names for abbreviations**: *"provide full definitions"* | ✅ COMPLETED | Complete nomenclature and abbreviations table created. | [[Abbreviations_Glossary]] |
| **5** | **Check licensing**: *"audit all components"* | ✅ COMPLETED | Licensing matrix compiled comparing MIT, Apache 2.0, CPML (Coqui XTTS v2 academic restriction), and NVIDIA Dev terms. | [[Pinned_Models_and_Licenses]] |
| **6** | **Prerequisites for following thesis in practice**: *"add exact steps"* | ✅ COMPLETED | Documented full hardware (RTX 3050 4GB), Fedora packages, PipeWire echo-cancel, and Python 3.11 reproduction guide. | [[Pinned_Models_and_Licenses]] |

---

## Thesis Invariant Rule
Any future pull requests or coding updates must strictly adhere to these 6 constraints. No new commands, models, or uninstrumented tests are permitted without logging an [[ADR-001_VRAM_Budget_Allocation|ADR]] or problem report.
