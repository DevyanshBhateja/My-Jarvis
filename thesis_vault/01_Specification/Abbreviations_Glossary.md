---
id: SPEC-004
title: Nomenclature & Abbreviations Glossary
tags: [specification, abbreviations, glossary, terminology]
related: ["[[Supervisor_Guidelines]]", "[[00_Map_of_Content]]"]
---

# 📖 Nomenclature & Abbreviations Glossary

In accordance with academic standards and supervisor feedback (*"detailed names for abbreviations"*), all terms and acronyms used throughout the thesis and repository are formally defined below.

| Abbreviation | Expanded Full Name | Definition in Context of the Thesis |
| :--- | :--- | :--- |
| **AEC** | **Acoustic Echo Cancellation** | Digital signal processing technique used to remove speaker playback audio from microphone capture, preventing acoustic feedback loops. |
| **ASR** | **Automatic Speech Recognition** | Algorithmic conversion of continuous human speech signals into text strings (instantiated via OpenAI Whisper). |
| **CPML** | **Coqui Public Model License** | A restrictive license permitting non-commercial research use of model weights while prohibiting unlicensed commercial distribution. |
| **CUDA** | **Compute Unified Device Architecture** | NVIDIA's proprietary parallel computing platform and API model for GPU-accelerated computing. |
| **D-Bus** | **Desktop Bus** | An inter-process communication (IPC) system for Linux desktop environments enabling software to communicate with system daemons. |
| **FP16 / FP32** | **Floating-Point 16-bit / 32-bit** | Precision format of neural network tensor weights balancing arithmetic speed and numerical precision against VRAM consumption. |
| **HCI** | **Human-Computer Interaction** | The field of research focused on the design, implementation, and evaluation of interfaces between humans and computer systems. |
| **IPC** | **Inter-Process Communication** | Mechanisms provided by the operating system allowing separate concurrent processes to exchange data. |
| **LLM** | **Large Language Model** | High-parameter transformer neural networks ($\ge 70\text{B}$ parameters) hosted on cloud clusters for complex reasoning. |
| **NIM** | **NVIDIA Inference Microservice** | Containerized inference deployment framework and cloud API providing optimized execution for foundation models. |
| **OOM** | **Out-Of-Memory** | An error triggered when an application attempts to allocate more RAM or GPU VRAM than physically available on the hardware. |
| **PCM** | **Pulse-Code Modulation** | A raw, uncompressed digital representation of an analog audio signal sampled at fixed intervals (e.g., 16 kHz 16-bit mono). |
| **RMS** | **Root Mean Square** | Statistical measure of the magnitude of a varying audio signal, used in energy-based voice activity detection. |
| **SLM** | **Small Language Model** | Quantized language models ($\le 3\text{B}$ parameters) capable of real-time local execution on consumer edge GPUs. |
| **STT** | **Speech-to-Text** | The pipeline stage converting spoken audio waveforms into textual transcripts. |
| **TTFA** | **Time-to-First-Audio** | Latency benchmark: elapsed milliseconds between the moment user speech ends and the moment the first output audio sample reaches the speaker. |
| **TTFT** | **Time-to-First-Token** | Latency benchmark: elapsed milliseconds between prompt dispatch and the generation of the first token by the language model. |
| **TTS** | **Text-to-Speech** | The pipeline stage synthesizing natural sounding spoken audio waveforms from linguistic text inputs. |
| **VAD** | **Voice Activity Detection** | Algorithmic classification determining the presence or absence of human speech in continuous audio frames. |
| **VRAM** | **Video Random-Access Memory** | High-bandwidth dedicated physical memory mounted on the graphics processing unit (GPU). |
| **VITS** | **Variational Inference with adversarial learning for end-to-end Text-to-Speech** | A lightweight, fast, one-stage neural TTS architecture with low VRAM footprint. |
| **XTTS** | **Extended Text-to-Speech** | A multi-lingual autoregressive and diffusion-based neural TTS model supporting voice cloning, requiring significant VRAM. |
