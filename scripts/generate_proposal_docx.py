"""Generate a professionally formatted Word Document (.docx) for the Thesis Proposal."""

import os
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn


def set_cell_background(cell, fill_hex):
    """Set background color of a table cell."""
    tcPr = cell._tc.get_or_add_tcPr()
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{fill_hex}"/>')
    tcPr.append(shd)


def set_cell_margins(cell, top=100, bottom=100, left=150, right=150):
    """Set padding for a cell."""
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = OxmlElement('w:tcMar')
    for m, val in [('w:top', top), ('w:bottom', bottom), ('w:left', left), ('w:right', right)]:
        node = OxmlElement(m)
        node.set(qn('w:w'), str(val))
        node.set(qn('w:type'), 'dxa')
        tcMar.append(node)
    tcPr.append(tcMar)


def build_document():
    doc = Document()

    # Set Margins
    for section in doc.sections:
        section.top_margin = Inches(1.0)
        section.bottom_margin = Inches(1.0)
        section.left_margin = Inches(1.0)
        section.right_margin = Inches(1.0)

    # Styles
    normal_style = doc.styles['Normal']
    normal_style.font.name = 'Calibri'
    normal_style.font.size = Pt(11)
    normal_style.font.color.rgb = RGBColor(0x22, 0x22, 0x22)
    normal_style.paragraph_format.line_spacing = 1.15
    normal_style.paragraph_format.space_after = Pt(6)

    # Title & Metadata Header
    p_title = doc.add_paragraph()
    p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_sub = p_title.add_run("BACHELOR’S THESIS PROPOSAL (REVISED)\n")
    r_sub.font.size = Pt(13)
    r_sub.font.bold = True
    r_sub.font.color.rgb = RGBColor(0x00, 0x55, 0x99)

    r_title = p_title.add_run("Real-Time Full-Duplex Conversational AI and Desktop Automation on Memory-Constrained Edge Workstations\n")
    r_title.font.size = Pt(18)
    r_title.font.bold = True
    r_title.font.color.rgb = RGBColor(0x11, 0x11, 0x11)

    p_meta = doc.add_paragraph()
    p_meta.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_meta.paragraph_format.space_after = Pt(20)
    r_meta = p_meta.add_run("Author: Devyansh Bhateja | Degree Programme: AI and Data Engineering | Academic Year: 2026\nTarget Hardware: NVIDIA GeForce RTX 3050 (4GB VRAM) | OS: Fedora Linux 40/41")
    r_meta.font.size = Pt(10)
    r_meta.font.italic = True
    r_meta.font.color.rgb = RGBColor(0x55, 0x55, 0x55)

    doc.add_paragraph("—" * 50).alignment = WD_ALIGN_PARAGRAPH.CENTER

    def add_h1(text):
        h = doc.add_paragraph()
        h.paragraph_format.space_before = Pt(16)
        h.paragraph_format.space_after = Pt(4)
        run = h.add_run(text)
        run.font.size = Pt(14)
        run.font.bold = True
        run.font.color.rgb = RGBColor(0x00, 0x44, 0x88)
        return h

    def add_h2(text):
        h = doc.add_paragraph()
        h.paragraph_format.space_before = Pt(12)
        h.paragraph_format.space_after = Pt(3)
        run = h.add_run(text)
        run.font.size = Pt(12)
        run.font.bold = True
        run.font.color.rgb = RGBColor(0x22, 0x22, 0x22)
        return h

    # Section 1
    add_h1("1. Executive Summary & Scope")
    doc.add_paragraph(
        "This thesis addresses an applied software systems and AI engineering challenge: achieving real-time, "
        "full-duplex conversational voice interaction and deterministic desktop automation on consumer-grade edge "
        "workstations with tight memory limits (NVIDIA GeForce RTX 3050 with 4GB VRAM)."
    )
    doc.add_paragraph(
        "Rather than training foundational neural network weights from scratch, the research focuses on pipeline "
        "concurrency, asynchronous edge-cloud orchestration, digital signal processing (DSP) echo cancellation, and "
        "low-latency full-duplex communication. The engineering objective is to replace rigid, half-duplex 'walkie-talkie' "
        "turn-taking with a natural, interruptible voice interface capable of hands-free operating system control on "
        "Fedora Linux at zero marginal API cost."
    )

    # Section 2
    add_h1("2. Problem Statement & Technical Motivation")
    doc.add_paragraph(
        "Current consumer voice assistants process interactions through a sequential half-duplex pipeline: "
        "Speech Ingestion → VAD → STT → LLM Generation → TTS Synthesis → Playback. "
        "On memory-constrained consumer workstations, this setup introduces three major failure points:"
    )
    p_pts = doc.add_paragraph()
    p_pts.add_run("1. Unacceptable Perceptible Latency: ").bold = True
    p_pts.add_run("End-to-end response times routinely sit between 2.5 and 5.0 seconds. Waiting for full LLM generation before beginning audio synthesis destroys natural conversational flow.\n")
    p_pts.add_run("2. Barge-In Failure & Acoustic Feedback: ").bold = True
    p_pts.add_run("When speakers are active, the microphone captures the assistant's own voice. Muting the microphone prevents user barge-in, while leaving it open creates self-triggering acoustic feedback loops.\n")
    p_pts.add_run("3. Severe Edge Memory Constraints (4GB VRAM): ").bold = True
    p_pts.add_run("Simultaneously running Whisper (STT), an autoregressive Small Language Model (SLM), and a Neural TTS engine on an NVIDIA RTX 3050 (4096 MB VRAM) routinely exhausts memory, causing CUDA Out-Of-Memory (OOM) crashes.\n")
    p_pts.add_run("4. Cloud WAN Latency Jitter: ").bold = True
    p_pts.add_run("Relying purely on cloud APIs adds network jitter (300–1200ms) and recurring per-token financial costs.")

    # Section 3
    add_h1("3. Proposed Architecture: The Asymmetric 'Double-AI' Hybrid Duplex")
    doc.add_paragraph(
        "To reconcile tight edge memory with deep reasoning capabilities, the system implements an asymmetric two-tier architecture:"
    )
    add_h2("3.1 The Local Edge Tier (Low Latency Loop)")
    doc.add_paragraph(
        "Runs locally on the RTX 3050 (4GB VRAM). Combines Whisper base.en (~250MB), an Ollama-quantized Qwen 2.5 3B SLM (~1.9GB), "
        "and Coqui VITS (~300MB), alongside PipeWire WebRTC Acoustic Echo Cancellation (AEC). "
        "Role: Delivers sub-second Time-to-First-Audio (TTFA), immediate spoken backchanneling ('Checking system stats now...'), "
        "and hardware-level barge-in cancellation under 200ms."
    )
    add_h2("3.2 The Cloud Worker Tier (Asynchronous Reasoning Loop)")
    doc.add_paragraph(
        "Interfaced via NVIDIA NIM developer endpoints (hosting Meta Llama 3.3 70B Instruct). "
        "Role: Operates asynchronously in the background on complex queries. It handles multi-step tool parameter extraction "
        "and diagnostic planning without blocking the audio output of the local conversational loop."
    )
    add_h2("3.3 The OS Automation & Execution Layer (Fedora Linux)")
    doc.add_paragraph(
        "Directly interfaces with Fedora system daemons and utilities (wpctl, upower, top, subprocess). "
        "Enforces an explicit confirmation dialogue ('Approve action?') before triggering OS mutations."
    )

    # Section 4
    add_h1("4. Research Questions & Formal Hypotheses")
    for rq, title, q, h in [
        ("RQ1", "Concurrency & Streaming Pipelining",
         "How can an asynchronous multi-threaded pipeline (Listen, Converse, Speak, Action) minimize Time-to-First-Audio (TTFA) while separating real-time dialogue from structured tool calls?",
         "By coupling streaming LLM token generation directly with sentence-bounded TTS chunking (10–15 tokens per chunk), Time-to-First-Audio can be compressed under 1.5 seconds, even on local edge GPUs."),
        ("RQ2", "Acoustic Echo & Mid-Sentence Barge-In",
         "What combination of system-level acoustic echo cancellation (PipeWire WebRTC AEC) and soft audio state management is required to support reliable mid-sentence barge-in without self-triggering?",
         "Software-only microphone muting eliminates feedback but destroys full-duplex responsiveness. A system-level PipeWire WebRTC AEC filter chain is necessary and sufficient to permit continuous listening during playback with barge-in interruption latency under 200ms."),
        ("RQ3", "Asymmetric Edge-Cloud Viability",
         "How effectively can an asymmetric architecture, coupling a local 4GB VRAM edge device with free-tier cloud APIs, replicate the responsiveness of commercial, high-end voice assistants while maintaining hands-free desktop control?",
         "An asymmetric 'Double-AI' model—where a fast local SLM (Qwen 2.5 3B) provides instant conversational backchanneling while a cloud worker (Llama 3.3 70B via NVIDIA NIM) asynchronously plans and verifies OS actions—satisfies sub-second conversational ergonomics without exceeding a 4GB VRAM ceiling.")
    ]:
        p = doc.add_paragraph()
        p.add_run(f"{rq} ({title}):\n").bold = True
        p.add_run(f"Question: ").italic = True
        p.add_run(f"{q}\n")
        p.add_run(f"Hypothesis: ").italic = True
        p.add_run(f"{h}")

    # Section 5
    add_h1("5. Strict Scope Containment: The Frozen Fedora Benchmark Suite")
    doc.add_paragraph(
        "Following supervisor feedback ('make a list what i can do, test that nothing more'), OS automation testing "
        "is strictly restricted to exactly 10 deterministic commands across 3 categories:"
    )

    table_data = [
        ("ID", "Category", "Voice Prompt Trigger", "Internal Action", "Target Utility", "Expected Result"),
        ("CMD-01", "App Launch", "Launch Firefox / Open browser", "open_app('firefox')", "subprocess.Popen", "Browser window renders"),
        ("CMD-02", "App Launch", "Open file manager", "open_app('nautilus')", "subprocess.Popen", "Nautilus explorer opens"),
        ("CMD-03", "App Launch", "Open terminal", "open_app('gnome-terminal')", "subprocess.Popen", "Terminal window launches"),
        ("CMD-04", "Window Ctrl", "Close active window", "hotkey('alt', 'f4')", "pyautogui.hotkey", "Active window terminates"),
        ("CMD-05", "Audio Ctrl", "Mute audio / Unmute sound", "run_command('wpctl set-mute...')", "wpctl (WirePlumber)", "Toggles sink audio mute"),
        ("CMD-06", "Audio Ctrl", "Turn volume up", "run_command('wpctl set-volume +5%')", "wpctl", "Increases volume by 5%"),
        ("CMD-07", "Audio Ctrl", "Turn volume down", "run_command('wpctl set-volume -5%')", "wpctl", "Decreases volume by 5%"),
        ("CMD-08", "Diagnostics", "Check CPU usage", "run_command('top -b -n1 | head -5')", "top", "Returns CPU load %"),
        ("CMD-09", "Diagnostics", "Check battery level", "run_command('upower -i ...')", "upower daemon", "Returns battery % and state"),
        ("CMD-10", "System Info", "What is my IP address?", "run_command('hostname -I')", "hostname", "Returns local IPv4 address"),
    ]

    t = doc.add_table(rows=len(table_data), cols=6)
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    for r_idx, row in enumerate(table_data):
        for c_idx, val in enumerate(row):
            cell = t.cell(r_idx, c_idx)
            cell.text = val
            p = cell.paragraphs[0]
            p.runs[0].font.size = Pt(8.5)
            set_cell_margins(cell, top=60, bottom=60, left=80, right=80)
            if r_idx == 0:
                p.runs[0].font.bold = True
                set_cell_background(cell, "004488")
                p.runs[0].font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
            elif r_idx % 2 == 1:
                set_cell_background(cell, "F2F5F8")

    # Section 6
    add_h1("6. Pinned Model Specifications & VRAM Memory Budget")
    doc.add_paragraph(
        "All model checkpoints, parameter counts, and precision formats are pinned to ensure full reproducibility:"
    )

    models_data = [
        ("Pipeline Stage", "Pinned Model", "Params", "Format / Quantization", "VRAM Footprint"),
        ("STT (Speech-to-Text)", "OpenAI Whisper base.en", "74M", "PyTorch FP32/FP16 Checkpoint", "~250 MB"),
        ("Local Edge SLM", "Qwen 2.5 3B Instruct", "3.09B", "Ollama qwen2.5:3b-instruct-q4_K_M", "~1,900 MB"),
        ("Cloud Worker LLM", "Meta Llama 3.3 70B Instruct", "70B", "NVIDIA NIM Cloud API", "0 MB (Cloud offloaded)"),
        ("Local TTS (Primary)", "Coqui VITS (vits_ljspeech)", "~30M", "PyTorch Checkpoint", "~300 MB"),
        ("Local TTS (Comparison)", "Coqui XTTS v2 (xtts_v2)", "~460M", "PyTorch Checkpoint (Diffusion/Autoreg)", "~1,600 MB"),
        ("VAD", "Google WebRTC VAD", "N/A", "C Library (webrtcvad Mode 1)", "0 MB (Host CPU)"),
        ("AEC", "PipeWire WebRTC AEC", "N/A", "PipeWire DSP Module", "0 MB (Host CPU)"),
    ]

    t2 = doc.add_table(rows=len(models_data), cols=5)
    t2.alignment = WD_TABLE_ALIGNMENT.CENTER
    for r_idx, row in enumerate(models_data):
        for c_idx, val in enumerate(row):
            cell = t2.cell(r_idx, c_idx)
            cell.text = val
            p = cell.paragraphs[0]
            p.runs[0].font.size = Pt(8.5)
            set_cell_margins(cell, top=60, bottom=60, left=80, right=80)
            if r_idx == 0:
                p.runs[0].font.bold = True
                set_cell_background(cell, "004488")
                p.runs[0].font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
            elif r_idx % 2 == 1:
                set_cell_background(cell, "F2F5F8")

    doc.add_paragraph(
        "\nMemory Budget Breakdown on 4096 MB VRAM Ceiling:\n"
        "• Primary Pipeline (Whisper + Qwen 3B + Coqui VITS): 250MB + 1900MB + 300MB = 2,450 MB. "
        "Leaves 1,646 MB headroom for OS display buffers and active application windows (e.g., Firefox). Zero OOM risk.\n"
        "• Heavy Comparison (Whisper + Qwen 3B + XTTS v2): 250MB + 1900MB + 1600MB = 3,750 MB. "
        "Leaves only 346 MB headroom. Application launches trigger fatal CUDA OOM errors (documented in thesis as an empirical boundary)."
    )

    # Section 7
    add_h1("7. Minimal Testing Protocol: Time, Accuracy & Known Failure Modes")
    doc.add_paragraph(
        "Per supervisor guidance ('minimal testing: test time and accuracy, mention the problems'), evaluation is strictly scoped to:"
    )
    p_test = doc.add_paragraph()
    p_test.add_run("1. Time & Latency Benchmarks (ms):\n").bold = True
    p_test.add_run("• Time-to-First-Token (TTFT): Elapsed ms from prompt dispatch to first token emitted.\n")
    p_test.add_run("• Time-to-First-Audio (TTFA): Total elapsed ms from user speech termination to first acoustic sample from speaker.\n")
    p_test.add_run("• Barge-In Interruption Latency: Elapsed ms from user speech onset to SIGKILL cancellation of active audio playback (Target: <= 200ms).\n\n")

    p_test.add_run("2. Accuracy & Reliability Benchmarks (%):\n").bold = True
    p_test.add_run("• Intent Classification Accuracy: % of spoken commands correctly mapped to target action across 50 trials per command (N = 500 total trials).\n")
    p_test.add_run("• Action Execution Success Rate: % of approved OS actions exiting with status code 0.\n")
    p_test.add_run("• False Barge-In Rate: Frequency of assistant self-interruptions due to acoustic bleed (Target: <= 2.0%).\n\n")

    p_test.add_run("3. Explicitly Documented Real-World Problems & Failure Modes:\n").bold = True
    p_test.add_run("• Acoustic Bleed & AEC Leakage: Physical speaker volume and room echo overwhelming the WebRTC AEC digital filter.\n")
    p_test.add_run("• Whisper Hallucination on Confirmation Tokens: Short one-word utterances ('yes', 'stop') lost or hallucinated when pre-padding is absent.\n")
    p_test.add_run("• VRAM Eviction under Desktop Load: Desktop window manager GPU allocations causing CUDA OOM when combined with heavy TTS.\n")
    p_test.add_run("• Cloud WAN Latency Jitter: Fluctuations in remote developer endpoint latency vs deterministic local inference.")

    # Section 8
    add_h1("8. Comprehensive Licensing & Intellectual Property Audit")
    lic_data = [
        ("Component", "Software / Model", "License Type", "Academic Terms", "Commercial Terms"),
        ("STT", "OpenAI Whisper", "MIT License", "Permissive open access", "Permitted"),
        ("Edge SLM", "Qwen 2.5 3B Instruct", "Apache 2.0", "Permissive open access", "Permitted"),
        ("Local TTS (Primary)", "Coqui VITS LJSpeech", "MIT License", "Permissive open access", "Permitted"),
        ("Local TTS (Comparison)", "Coqui XTTS v2", "CPML (Coqui Public Model License)", "Permitted for non-commercial research", "Prohibited without commercial license"),
        ("Cloud Worker", "NVIDIA NIM Free Tier", "NVIDIA Developer License", "Free evaluation tier for research", "Subject to enterprise license"),
        ("Audio Routing", "PipeWire & WebRTC", "LGPL 2.1+ / BSD 3-Clause", "Open-source system libraries", "Permitted"),
        ("Assistant Code", "MY_JARVIS", "MIT License", "Author's original research implementation", "Permitted"),
    ]
    t3 = doc.add_table(rows=len(lic_data), cols=5)
    t3.alignment = WD_TABLE_ALIGNMENT.CENTER
    for r_idx, row in enumerate(lic_data):
        for c_idx, val in enumerate(row):
            cell = t3.cell(r_idx, c_idx)
            cell.text = val
            p = cell.paragraphs[0]
            p.runs[0].font.size = Pt(8.5)
            set_cell_margins(cell, top=60, bottom=60, left=80, right=80)
            if r_idx == 0:
                p.runs[0].font.bold = True
                set_cell_background(cell, "004488")
                p.runs[0].font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
            elif r_idx % 2 == 1:
                set_cell_background(cell, "F2F5F8")

    # Section 9
    add_h1("9. Prerequisites for Practical Reproduction")
    doc.add_paragraph(
        "• Hardware: NVIDIA GeForce RTX 3050 (4GB VRAM), Intel Core i5/i7 (11th Gen+) or AMD Ryzen 5/7, >= 16 GB RAM, microphone + stereo speakers.\n"
        "• Operating System: Fedora Linux 40 or 41 (Workstation Edition, GNOME on Wayland/X11).\n"
        "• System Packages: pipewire-plugin-echo-cancel, pipewire-utils, alsa-utils, mpg123.\n"
        "• Local Inference: Ollama Linux daemon with qwen2.5:3b model pulled.\n"
        "• Python Virtual Environment: Python 3.11 with PyTorch (CUDA 12.1), openai-whisper, TTS, sounddevice, webrtcvad, openai, pyautogui."
    )

    # Section 10
    add_h1("10. Nomenclature & Abbreviations Glossary")
    abbr_data = [
        ("AEC", "Acoustic Echo Cancellation", "DSP algorithm removing speaker playback from microphone capture."),
        ("ASR", "Automatic Speech Recognition", "Algorithmic conversion of acoustic signals into textual transcripts."),
        ("CPML", "Coqui Public Model License", "Restrictive license permitting non-commercial research use only."),
        ("CUDA", "Compute Unified Device Architecture", "NVIDIA parallel computing platform for GPU acceleration."),
        ("D-Bus", "Desktop Bus", "Linux inter-process communication system for desktop management."),
        ("HCI", "Human-Computer Interaction", "Academic discipline studying interactive system interfaces."),
        ("LLM", "Large Language Model", "High-parameter transformer networks (>= 70B) hosted in cloud."),
        ("NIM", "NVIDIA Inference Microservice", "Containerized deployment microservice and cloud API framework."),
        ("OOM", "Out-Of-Memory", "Error condition when software exceeds physical VRAM or RAM capacity."),
        ("PCM", "Pulse-Code Modulation", "Uncompressed digital representation of sampled audio signals."),
        ("SLM", "Small Language Model", "Quantized language models (<= 3B) optimized for edge GPU execution."),
        ("STT", "Speech-to-Text", "Pipeline component transcribing voice audio into text tokens."),
        ("TTFA", "Time-to-First-Audio", "Latency from user speech end to first sound from the speaker."),
        ("TTFT", "Time-to-First-Token", "Latency from prompt dispatch to first token emitted by language model."),
        ("TTS", "Text-to-Speech", "Pipeline component synthesizing spoken waveforms from text strings."),
        ("VAD", "Voice Activity Detection", "Algorithmic classification of human speech presence in audio frames."),
        ("VITS", "Variational Inference TTS", "Lightweight, non-autoregressive neural TTS architecture (~300MB VRAM)."),
        ("VRAM", "Video Random-Access Memory", "Dedicated high-speed physical memory mounted on the GPU board."),
        ("XTTS", "Extended Text-to-Speech", "Diffusion/autoregressive neural TTS architecture (~1.6GB VRAM)."),
    ]
    t4 = doc.add_table(rows=len(abbr_data) + 1, cols=3)
    t4.alignment = WD_TABLE_ALIGNMENT.CENTER
    t4.cell(0, 0).text = "Abbreviation"
    t4.cell(0, 1).text = "Expanded Name"
    t4.cell(0, 2).text = "Definition in Context of Thesis"
    for c in range(3):
        cell = t4.cell(0, c)
        set_cell_background(cell, "004488")
        cell.paragraphs[0].runs[0].font.bold = True
        cell.paragraphs[0].runs[0].font.size = Pt(8.5)
        cell.paragraphs[0].runs[0].font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)

    for r_idx, (a, n, d) in enumerate(abbr_data, 1):
        for c_idx, val in enumerate([a, n, d]):
            cell = t4.cell(r_idx, c_idx)
            cell.text = val
            p = cell.paragraphs[0]
            p.runs[0].font.size = Pt(8.5)
            set_cell_margins(cell, top=50, bottom=50, left=70, right=70)
            if r_idx % 2 == 1:
                set_cell_background(cell, "F2F5F8")

    # Section 11
    add_h1("11. Deliverables & Milestone Timeline")
    doc.add_paragraph(
        "1. Reference Implementation: A fully functional, full-duplex conversational voice assistant running on Fedora Linux "
        "and an RTX 3050 (4GB VRAM) supporting mid-sentence barge-in and the 10 frozen desktop automation commands.\n"
        "2. Empirical Benchmarking Dataset: Documented latency measurements (TTFT, TTFA, Barge-in delay) and accuracy metrics across 500 standardized command trials.\n"
        "3. Completed Bachelor's Thesis Report: A formal academic dissertation detailing architectural trade-offs, negative results/engineering failures, and findings addressing RQ1, RQ2, and RQ3."
    )

    output_path = "/home/dave/Documents/Projects/MY_JARVIS/Thesis_Proposal_Revised.docx"
    doc.save(output_path)
    print(f"Successfully generated: {output_path}")


if __name__ == "__main__":
    build_document()
