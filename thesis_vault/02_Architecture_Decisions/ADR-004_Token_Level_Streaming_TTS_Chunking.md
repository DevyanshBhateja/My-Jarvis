---
id: ADR-004
title: Token-Level Streaming and Sentence-Bounded TTS Chunking
tags: [adr, architecture, streaming, tts, latency, decision]
status: Accepted
related: ["[[Research_Questions]]", "[[EXP-002_Local_vs_Cloud_Routing_Latency]]"]
---

# 🏛️ ADR-004: Token-Level Streaming & Sentence-Bounded TTS Chunking

## Context & Problem Statement
In traditional half-duplex voice assistants, the client waits for the entire LLM response to complete generation before passing the full text to the TTS engine. For a 50-token response generated at 25 tokens/sec, this introduces an upfront 2.0-second delay before TTS synthesis even begins, resulting in unacceptable Time-to-First-Audio ($\text{TTFA} > 3.5\text{s}$).

## Decision Drivers
1. **Time-to-First-Audio (TTFA)** must be $\le 1.5\text{ seconds}$.
2. **Audio Naturalness**: Neural TTS engines synthesize unnatural cadence, robotic pitch, and awkward pauses if fed single words or arbitrary token cuts.
3. **Interruptibility**: Smaller chunks can be cancelled and flushed rapidly upon user barge-in.

## Decision & Rationale
We implement a dual-trigger streaming buffer between the LLM output generator and the TTS synthesizer in [[interaction_orchestrator.py]]:
1. **Punctuation Boundary Trigger**: The buffer flushes immediately whenever terminal or clause punctuation (`.`, `!`, `?`, `;`, `:`) is encountered.
2. **Token Window Threshold**: If no punctuation occurs, the buffer flushes after accumulating **10 to 15 tokens** (or $\sim 140\text{ characters}$) at the nearest word boundary.

```python
# Streaming chunker heuristic:
if any(punct in token for punct in ".!?,;:") or len(text_buffer.split()) >= 12:
    enqueue_tts_chunk(text_buffer)
    text_buffer = ""
```

## Consequences & Thesis Contribution
- **Latency Gain**: The TTS engine begins synthesizing sentence 1 while the LLM is still actively generating sentence 2. TTFA drops from $3.2\text{s}$ to $1.1\text{s}$.
- **Acoustic Quality**: Preserving sentence boundaries ensures natural prosody and intonation.
- Directly supports **RQ1**: Proves the effectiveness of pipelined concurrency across streaming LLM tokens and neural audio synthesis.
