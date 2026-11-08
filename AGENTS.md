# AGENTS.md — Steering Rules & Research Logging Protocol

This repository is the empirical foundation for a Bachelor's Thesis:
**"Real-Time Full-Duplex Conversational AI and Desktop Automation on Memory-Constrained Edge Workstations"**
Author: Devyansh Bhateja | Target Hardware: NVIDIA RTX 3050 (4GB VRAM) | OS: Fedora Linux.

---

## 1. Golden Rules for Antigravity (Every Turn)

1. **Thesis Scope Enforcement**:
   - Never introduce unbounded features, random tools, or arbitrary desktop commands.
   - Restrict all desktop testing strictly to the **10 Frozen Fedora Commands** defined in `[[Frozen_Fedora_Commands]]`.
   - Never deviate from the pinned model versions defined in `[[Pinned_Models_and_Licenses]]` without an Architectural Decision Record (`ADR`).

2. **Memory Constraint First (4GB VRAM Budget)**:
   - Always ensure combined VRAM footprint of STT (Whisper) + SLM (Ollama) + TTS (Coqui) does not exceed 3.5 GB (leaving ~500MB for display server / desktop).
   - If a model or approach risks OOM, document it immediately as a tested failure and formulate an alternative.

3. **Continuous Obsidian Research Logging**:
   - Whenever a problem occurs, a change is made, or an experiment is run, you **MUST** update or create corresponding notes in `thesis_vault/`:
     - **Problem encountered?** → Create/update `thesis_vault/03_Problem_Log/PRB-XXX.md`. Record:
       - What happened (error / unexpected behavior)
       - What was attempted
       - **What failed** (and why it failed technically)
       - **What worked** (root cause resolution)
       - Academic takeaway for Thesis Chapter 4/5
     - **Architectural change?** → Create/update `thesis_vault/02_Architecture_Decisions/ADR-XXX.md`.
     - **Benchmark run?** → Record raw measurements in `thesis_vault/05_Benchmarks/`.
   - Always use Obsidian wikilinks (`[[Note_Title]]`) and tags (`#problem`, `#solution`, `#failed-attempt`, `#rq1`, `#rq2`, `#rq3`, `#benchmark`) so the knowledge graph interconnects properly.

---

## 2. Directory Structure of the Knowledge Vault

All research records live in `thesis_vault/`:
- `00_Map_of_Content.md` — Central dashboard & index (MOC)
- `01_Specification/` — Supervisor guidelines, pinned models, frozen commands, abbreviations
- `02_Architecture_Decisions/` — Architectural Decision Records (ADRs) with rationale & trade-offs
- `03_Problem_Log/` — The living log of bugs, failed attempts, and working solutions
- `04_Experiments/` — Empirical test runs (hypotheses, setups, logs)
- `05_Benchmarks/` — Latency (TTFT, TTFA), accuracy, and resource profiles
- `06_Thesis_Drafts/` — Pre-written thesis sections derived from project evidence

---

## 3. Standard Problem Log Format (`PRB-XXX`)

Every problem log file MUST follow this schema:

```markdown
---
id: PRB-XXX
title: Short Description of Issue
research_question: [[RQ1_Concurrency_Pipelining]] | [[RQ2_Acoustic_Echo_BargeIn]] | [[RQ3_Edge_Cloud_Viability]]
status: Solved | In-Progress | Abandoned
tags: [problem, failed-attempt, solution, rqX]
---

# PRB-XXX: Problem Title

## 1. Problem Description & Symptoms
- Context: ...
- Observed behavior: ...

## 2. Failed Attempts & Negative Results (Crucial for Thesis Discussion)
- **Attempt 1**: What was tried?
  - *Result*: Why did it fail? What was the error/side effect?
- **Attempt 2**: ...

## 3. Working Solution & Root Cause Analysis
- *The Fix*: Exact code or configuration change.
- *Why it works*: Theoretical / algorithmic rationale.

## 4. Academic Thesis Contribution
- What does this teach us about edge AI / full-duplex systems?
- Reference in Thesis: Chapter X, Section Y.
```
