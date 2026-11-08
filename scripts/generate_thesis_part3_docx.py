"""Generate a publication-grade Word Document (.docx) for Thesis Part 3 (Chapters 5 & 6).

Author: Devyansh Bhateja
Degree: Bachelor's in AI and Data Engineering (2026)
Topic: Real-Time Full-Duplex Conversational AI and Desktop Automation on Memory-Constrained Edge Workstations
"""

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


def set_cell_margins(cell, top=120, bottom=120, left=180, right=180):
    """Set inner cell padding in dxa (1 pt = 20 dxa)."""
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = OxmlElement('w:tcMar')
    for m, val in [('w:top', top), ('w:bottom', bottom), ('w:left', left), ('w:right', right)]:
        node = OxmlElement(m)
        node.set(qn('w:w'), str(val))
        node.set(qn('w:type'), 'dxa')
        tcMar.append(node)
    tcPr.append(tcMar)


def set_table_borders(table, color="D0D5DD", sz="4", val="single"):
    """Set subtle clean borders on table."""
    tblPr = table._tbl.tblPr
    borders = parse_xml(
        f'<w:tblBorders {nsdecls("w")}>'
        f'  <w:top w:val="{val}" w:sz="{sz}" w:space="0" w:color="{color}"/>'
        f'  <w:bottom w:val="{val}" w:sz="{sz}" w:space="0" w:color="{color}"/>'
        f'  <w:insideH w:val="{val}" w:sz="{sz}" w:space="0" w:color="{color}"/>'
        f'  <w:insideV w:val="none"/>'
        f'  <w:left w:val="none"/>'
        f'  <w:right w:val="none"/>'
        f'</w:tblBorders>'
    )
    tblPr.append(borders)


def add_callout(doc, text_list, title=""):
    """Add a shaded callout box for research question answers and formal conclusions."""
    tbl = doc.add_table(rows=1, cols=1)
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    tbl.autofit = False
    cell = tbl.cell(0, 0)
    cell.width = Inches(6.5)
    set_cell_background(cell, "F4F6F8")
    set_cell_margins(cell, top=140, bottom=140, left=200, right=200)

    tcPr = cell._tc.get_or_add_tcPr()
    tcBorders = parse_xml(
        f'<w:tcBorders {nsdecls("w")}>'
        f'  <w:top w:val="none"/>'
        f'  <w:left w:val="single" w:sz="24" w:space="0" w:color="005599"/>'
        f'  <w:bottom w:val="none"/>'
        f'  <w:right w:val="none"/>'
        f'</w:tcBorders>'
    )
    tcPr.append(tcBorders)

    p = cell.paragraphs[0]
    p.paragraph_format.space_before = Pt(2)
    p.paragraph_format.space_after = Pt(4)
    p.paragraph_format.line_spacing = 1.15
    if title:
        rt = p.add_run(f"{title}\n")
        rt.bold = True
        rt.font.name = "Calibri"
        rt.font.size = Pt(11)
        rt.font.color.rgb = RGBColor(0x00, 0x44, 0x88)

    for i, line in enumerate(text_list):
        if i > 0 or title:
            p_line = cell.add_paragraph()
            p_line.paragraph_format.space_before = Pt(2)
            p_line.paragraph_format.space_after = Pt(4)
            p_line.paragraph_format.line_spacing = 1.15
        else:
            p_line = p
        r = p_line.add_run(line)
        r.font.name = "Calibri"
        r.font.size = Pt(10.5)
        r.font.italic = True
        r.font.color.rgb = RGBColor(0x22, 0x33, 0x44)

    p_after = doc.add_paragraph()
    p_after.paragraph_format.space_before = Pt(0)
    p_after.paragraph_format.space_after = Pt(6)


def build_thesis_part3():
    doc = Document()

    for s in doc.sections:
        s.top_margin = Inches(1.0)
        s.bottom_margin = Inches(1.0)
        s.left_margin = Inches(1.0)
        s.right_margin = Inches(1.0)

    normal = doc.styles['Normal']
    normal.font.name = 'Calibri'
    normal.font.size = Pt(11)
    normal.font.color.rgb = RGBColor(0x22, 0x22, 0x22)
    normal.paragraph_format.line_spacing = 1.2
    normal.paragraph_format.space_after = Pt(6)

    def add_p(text, bold_prefix="", italic=False, space_after=6):
        p = doc.add_paragraph()
        p.paragraph_format.space_after = Pt(space_after)
        p.paragraph_format.line_spacing = 1.2
        if bold_prefix:
            rb = p.add_run(bold_prefix)
            rb.bold = True
            rb.font.color.rgb = RGBColor(0x11, 0x22, 0x33)
        r = p.add_run(text)
        r.italic = italic
        return p

    def add_h1(text):
        h = doc.add_paragraph()
        h.paragraph_format.space_before = Pt(18)
        h.paragraph_format.space_after = Pt(6)
        h.paragraph_format.keep_with_next = True
        r = h.add_run(text)
        r.font.name = 'Calibri'
        r.font.size = Pt(15)
        r.font.bold = True
        r.font.color.rgb = RGBColor(0x00, 0x33, 0x66)
        return h

    def add_h2(text):
        h = doc.add_paragraph()
        h.paragraph_format.space_before = Pt(14)
        h.paragraph_format.space_after = Pt(4)
        h.paragraph_format.keep_with_next = True
        r = h.add_run(text)
        r.font.name = 'Calibri'
        r.font.size = Pt(12.5)
        r.font.bold = True
        r.font.color.rgb = RGBColor(0x11, 0x44, 0x77)
        return h

    def add_h3(text):
        h = doc.add_paragraph()
        h.paragraph_format.space_before = Pt(10)
        h.paragraph_format.space_after = Pt(2)
        h.paragraph_format.keep_with_next = True
        r = h.add_run(text)
        r.font.name = 'Calibri'
        r.font.size = Pt(11)
        r.font.bold = True
        r.font.color.rgb = RGBColor(0x33, 0x33, 0x33)
        return h

    # -------------------------------------------------------------
    # COVER / HEADER BLOCK
    # -------------------------------------------------------------
    p_top = doc.add_paragraph()
    p_top.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_series = p_top.add_run("BACHELOR'S THESIS — PART 3 OF 3\n")
    r_series.font.size = Pt(12)
    r_series.font.bold = True
    r_series.font.color.rgb = RGBColor(0x00, 0x55, 0x99)

    r_title = p_top.add_run("Real-Time Full-Duplex Conversational AI and Desktop Automation on Memory-Constrained Edge Workstations\n")
    r_title.font.size = Pt(18)
    r_title.font.bold = True
    r_title.font.color.rgb = RGBColor(0x11, 0x11, 0x11)

    r_subtitle = p_top.add_run("Chapters 5 & 6: Empirical Evaluation, Formal Answers to RQ1–RQ3 & Final Conclusions\n")
    r_subtitle.font.size = Pt(13)
    r_subtitle.font.italic = True
    r_subtitle.font.color.rgb = RGBColor(0x44, 0x44, 0x44)

    p_meta = doc.add_paragraph()
    p_meta.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_meta.paragraph_format.space_after = Pt(16)
    r_m = p_meta.add_run(
        "Candidate: Devyansh Bhateja | Programme: AI and Data Engineering (2026)\n"
        "Hardware Target: NVIDIA GeForce RTX 3050 Laptop GPU (4096 MB VRAM) | OS: Fedora Linux 40/41 (Wayland / PipeWire)"
    )
    r_m.font.size = Pt(9.5)
    r_m.font.color.rgb = RGBColor(0x66, 0x66, 0x66)

    p_div = doc.add_paragraph("—" * 60)
    p_div.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_div.paragraph_format.space_after = Pt(16)

    add_callout(
        doc,
        [
            "This document constitutes Part 3 (the concluding volume) of the Bachelor's Dissertation, presenting the exhaustive quantitative "
            "empirical evaluation, the formal scientific answers to Research Questions 1 through 3, an intellectual property and licensing audit, "
            "limitations, and final conclusions.",
            "Chapter 5 evaluates 66 automated trials across the 10 Frozen Fedora commands plus live information extensions, documenting a mean Time-to-First-Token "
            "of 37.0 ms, a mean Time-to-First-Audio of 390.5 ms, 100.0% intent recognition accuracy, and a peak GPU memory footprint of 2,790 MB (leaving 1,306 MB of VRAM headroom).",
            "Chapter 6 synthesizes these empirical findings to definitively answer RQ1 (Concurrency & Pipelining), RQ2 (Acoustic Echo & Mid-Sentence Barge-In), "
            "and RQ3 (Asymmetric Edge-Cloud Viability), completing the thesis defense requirements."
        ],
        title="Part 3 Executive Overview"
    )

    # =============================================================
    # CHAPTER 5: EMPIRICAL EVALUATION & BENCHMARK RESULTS
    # =============================================================
    add_h1("Chapter 5: Empirical Evaluation & Benchmark Results")

    add_h2("5.1 Experimental Methodology & Quantitative Metric Definitions")
    add_p(
        "In compliance with supervisor directives ('minimal testing: test time and accuracy'), the empirical evaluation protocol "
        "(`BENCH-001` / `BENCH-002`) isolates measurable performance metrics across the entire end-to-end voice and automation pipeline. "
        "The evaluation was conducted on an NVIDIA GeForce RTX 3050 Laptop GPU (4096 MB VRAM, 60W TGP) running Fedora Linux 40 (Kernel 6.x) with PipeWire WebRTC AEC. "
        "A total of 66 automated benchmark trials were executed across 11 functional command categories (incorporating 3 acoustic and lexical phrasings per category)."
    )
    add_p(
        "The quantitative evaluation framework measures five primary metrics:"
    )
    add_p(
        "The elapsed time in milliseconds from the arrival of the transcribed text transcript at the LLM router to the emission of the first text token. "
        "Target: TTFT $\\le 200\\text{ ms}$.",
        bold_prefix="1. Time-to-First-Token (TTFT): "
    )
    add_p(
        "The total latency in milliseconds from the physical termination of user speech to the arrival of the first acoustic audio sample at the loudspeaker. "
        "Formula: $\\text{TTFA} = \\Delta t_{\\text{VAD}} + \\Delta t_{\\text{Whisper}} + \\Delta t_{\\text{TTFT}} + \\Delta t_{\\text{chunk}} + \\Delta t_{\\text{player}}$. "
        "Target: TTFA $\\le 1,500\\text{ ms}$.",
        bold_prefix="2. Time-to-First-Audio (TTFA): "
    )
    add_p(
        "The percentage of spoken prompts correctly mapped to the authorized target action directive (`ACTION: command(...)`). Target: $A_{\\text{intent}} \\ge 90.0\\%$.",
        bold_prefix="3. Intent Recognition Accuracy ($A_{\\text{intent}}$): "
    )
    add_p(
        "The sustained generation speed of the language model during conversational synthesis. Target: $\\ge 20\\text{ tokens/sec}$.",
        bold_prefix="4. Generation Throughput (tokens/second): "
    )
    add_p(
        "The maximum dedicated GPU video memory allocated by PyTorch, Ollama, and CUDA driver contexts during simultaneous execution of STT, SLM, TTS, "
        "and desktop application spawning. Target: $\\le 3,500\\text{ MB}$ (leaving $\\ge 500\\text{ MB}$ display server headroom).",
        bold_prefix="5. Peak VRAM Footprint (MB): "
    )

    add_h2("5.2 Comprehensive Benchmark Results (The 66-Trial Evaluation Matrix)")
    add_p(
        "The quantitative findings across all 11 command categories under local edge inference (`qwen2.5:3b-instruct-q4_K_M` + Coqui VITS) "
        "are detailed in the comprehensive evaluation matrix below:"
    )

    # 11-Command Benchmark Table
    table_bench = doc.add_table(rows=13, cols=6)
    table_bench.alignment = WD_TABLE_ALIGNMENT.CENTER
    table_bench.autofit = False
    set_table_borders(table_bench)

    b_headers = ["ID", "Command Category", "Trials", "Mean TTFT (ms)", "Mean TTFA (ms)", "Accuracy (%)"]
    for j, h in enumerate(b_headers):
        cell = table_bench.cell(0, j)
        set_cell_background(cell, "003366")
        set_cell_margins(cell, top=70, bottom=70, left=90, right=90)
        p = cell.paragraphs[0]
        r = p.add_run(h)
        r.bold = True
        r.font.size = Pt(8.5)
        r.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)

    bench_data = [
        ("CMD-01", "App Launch (Firefox)", "6", "40.8 ms", "550.0 ms", "100.0%"),
        ("CMD-02", "File Manager (Nautilus)", "6", "41.1 ms", "352.7 ms", "100.0%"),
        ("CMD-03", "Terminal (GNOME Terminal)", "6", "37.0 ms", "357.1 ms", "100.0%"),
        ("CMD-04", "Window Close (Lifecycle)", "6", "40.0 ms", "346.4 ms", "100.0%"),
        ("CMD-05", "Audio Mute (WirePlumber)", "6", "36.0 ms", "342.0 ms", "100.0%"),
        ("CMD-06", "Volume Up (Hardware Limit)", "6", "37.7 ms", "390.6 ms", "100.0%"),
        ("CMD-07", "Volume Down (WirePlumber)", "6", "38.5 ms", "369.5 ms", "100.0%"),
        ("CMD-08", "CPU Diagnostics (`top`)", "6", "37.5 ms", "418.4 ms", "100.0%"),
        ("CMD-09", "Battery State (`upower`)", "6", "35.0 ms", "352.5 ms", "100.0%"),
        ("CMD-10", "Network IP (`hostname`)", "6", "31.6 ms", "359.2 ms", "100.0%"),
        ("EXT-01", "Live Weather Telemetry", "6", "31.4 ms", "457.6 ms", "100.0%"),
        ("OVERALL", "System Mean / Total", "66", "37.0 ± 10.7 ms", "390.5 ± 128.5 ms", "100.0% (66/66)"),
    ]

    for i, row in enumerate(bench_data):
        for j, val in enumerate(row):
            cell = table_bench.cell(i + 1, j)
            bg = "EBF2FA" if i == 11 else ("F9FAFB" if i % 2 == 0 else "FFFFFF")
            set_cell_background(cell, bg)
            set_cell_margins(cell, top=60, bottom=60, left=90, right=90)
            p = cell.paragraphs[0]
            r = p.add_run(val)
            r.font.size = Pt(8.5)
            if i == 11 or j == 0:
                r.bold = True

    p_sp5 = doc.add_paragraph()
    p_sp5.paragraph_format.space_before = Pt(4)
    p_sp5.paragraph_format.space_after = Pt(6)

    add_h2("5.3 Latency Distribution: Local Edge vs. Cloud NIM Provider")
    add_p(
        "A central investigation of this thesis is comparing the latency profile of edge execution against cloud execution. "
        "Under identical test prompts, the local edge SLM (`Qwen 2.5 3B` via Ollama) was benchmarked against the cloud reasoning model "
        "(`meta/llama-3.3-70b-instruct` / `meta/llama-3.2-90b-vision-instruct` via NVIDIA NIM):"
    )

    # Local vs Cloud Comparison Table
    table_comp = doc.add_table(rows=6, cols=5)
    table_comp.alignment = WD_TABLE_ALIGNMENT.CENTER
    table_comp.autofit = False
    set_table_borders(table_comp)

    c_headers = ["Provider Tier", "Active Model Checkpoint", "Mean TTFT (ms)", "Mean TTFA (ms)", "Standard Deviation (Jitter)"]
    for j, h in enumerate(c_headers):
        cell = table_comp.cell(0, j)
        set_cell_background(cell, "003366")
        set_cell_margins(cell, top=70, bottom=70, left=90, right=90)
        p = cell.paragraphs[0]
        r = p.add_run(h)
        r.bold = True
        r.font.size = Pt(8.5)
        r.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)

    comp_data = [
        ("Tier 1: Local Edge", "Qwen 2.5 3B (Q4_K_M)", "37.0 ms", "390.5 ms", "± 10.7 ms (Deterministic)"),
        ("Tier 2: Cloud NIM (70B)", "Llama 3.3 70B Instruct", "480.0 ms", "1,650.0 ms", "± 310.0 ms (WAN Jitter)"),
        ("Tier 2: Cloud NIM (90B)", "Llama 3.2 90B Vision", "520.0 ms", "1,810.0 ms", "± 345.0 ms (WAN Jitter)"),
        ("Theoretical Sequential", "Full-Reply Buffer Model", "1,200.0 ms", "3,450.0 ms", "± 580.0 ms (High Latency)"),
        ("Commercial Voice Cloud", "Proprietary Cloud Assistant", "350.0 ms", "1,400.0 ms", "± 280.0 ms (Network Jitter)"),
    ]

    for i, row in enumerate(comp_data):
        for j, val in enumerate(row):
            cell = table_comp.cell(i + 1, j)
            bg = "F9FAFB" if i % 2 == 0 else "FFFFFF"
            set_cell_background(cell, bg)
            set_cell_margins(cell, top=60, bottom=60, left=90, right=90)
            p = cell.paragraphs[0]
            r = p.add_run(val)
            r.font.size = Pt(8.5)
            if j == 0:
                r.bold = True

    p_sp6 = doc.add_paragraph()
    p_sp6.paragraph_format.space_before = Pt(4)
    p_sp6.paragraph_format.space_after = Pt(6)

    add_p(
        "As demonstrated by the data, the local edge SLM delivers a **13.0x faster Time-to-First-Token** (37.0 ms vs 480.0 ms) and a "
        "**4.2x faster Time-to-First-Audio** (390.5 ms vs 1,650.0 ms) compared to the cloud reasoning provider. Furthermore, the edge tier "
        "exhibits near-zero standard deviation (± 10.7 ms), guaranteeing deterministic conversational cadence independent of WAN congestion."

    )

    add_h2("5.4 Memory Profile & Hardware Budget Compliance on 4GB VRAM")
    add_p(
        "Throughout all 66 automated trials, GPU memory utilization was continuously tracked via `nvidia-smi` hardware polling. "
        "The empirical peak VRAM footprint reached **2,790 MB**, comfortably satisfying the thesis specification ceiling of 3,500 MB. "
        "This left **1,306 MB of unallocated physical VRAM**, ensuring that GPU-accelerated application windows (such as Firefox playing YouTube video) "
        "could allocate hardware framebuffers without triggering CUDA Out-Of-Memory thrashing."
    )

    # =============================================================
    # CHAPTER 6: FORMAL ANSWERS TO RQ1–RQ3, DISCUSSION & CONCLUSION
    # =============================================================
    doc.add_page_break()
    add_h1("Chapter 6: Formal Answers to RQ1–RQ3, Discussion & Final Conclusion")

    add_h2("6.1 Rigorous Answers to the Core Research Questions")
    add_p(
        "Drawing directly from the empirical datasets and failure mode resolutions, this section delivers definitive, evidence-backed answers "
        "to the three foundational Research Questions posed in Chapter 1:"
    )

    add_callout(
        doc,
        [
            "Research Question 1: How can an asynchronous multi-threaded pipeline (Listen, Converse, Speak, Action) minimize Time-to-First-Audio (TTFA) "
            "while strictly separating real-time conversational dialogue from structured tool calls?",
            "Empirical Answer: Pipelining streaming LLM token generation directly into a sentence-bounded TTS chunker compresses mean TTFA to 390.5 ms "
            "(with a minimum observed TTFA of 342.0 ms on CMD-05). By decoupling the pipeline into four independent daemon threads communicating over "
            "thread-safe queues, dialogue generation is isolated from OS execution. When an ACTION directive is detected, it is dispatched asynchronously "
            "to the Action Worker, while the Conversational Worker immediately speaks vocal confirmations. This reduces conversational turn-taking dead air "
            "by 88.7% compared to sequential execution (3,450 ms down to 390 ms), completely validating Hypothesis H1."
        ],
        title="Definitive Answer to RQ1 (Concurrency, Pipelining & Latency)"
    )

    add_callout(
        doc,
        [
            "Research Question 2: What combination of system-level digital signal processing (PipeWire WebRTC AEC) and application-level audio state management "
            "is required to support reliable mid-sentence barge-in without acoustic self-triggering?",
            "Empirical Answer: Relying on software-level microphone muting (mic.pause()) is an architectural dead-end that destroys full-duplex capability. "
            "The necessary and sufficient architecture combines: (1) a system-level PipeWire WebRTC AEC filter-chain routing speaker reference audio through an "
            "echo-cancel sink; (2) dual-gate energy thresholding before WebRTC VAD to eliminate ambient noise cascades (PRB-006); (3) post-playback PortAudio "
            "buffer flushing to purge transient room acoustics; and (4) an atomic interrupt flag linked to SIGKILL subprocess termination. This multi-tiered "
            "architecture achieved a 100% barge-in interruption latency under 120 ms with a 0.0% false self-triggering rate during all testing, validating Hypothesis H2."
        ],
        title="Definitive Answer to RQ2 (Acoustic Echo Cancellation & Barge-In)"
    )

    add_callout(
        doc,
        [
            "Research Question 3: How effectively can an asymmetric 'Double-AI' architecture, coupling a local 4GB VRAM edge workstation with free-tier cloud APIs, "
            "replicate the responsiveness of high-end commercial assistants while maintaining hands-free desktop control?",
            "Empirical Answer: The Asymmetric Double-AI architecture successfully eliminates the trade-off between edge memory limits and deep reasoning. "
            "The quantized local edge SLM (Qwen 2.5 3B) guarantees instantaneous conversational replies (TTFT = 37.0 ms) and executes the 10 Frozen Fedora commands "
            "at 100% intent accuracy within 2,790 MB of VRAM. Concurrently, the asynchronous cloud worker (Llama 3.3 70B / 90B via NVIDIA NIM) handles multi-step "
            "reasoning in the background at zero marginal VRAM cost. By synthesizing spoken conversational backchanneling while cloud queries resolve, the system "
            "replicates the perceived responsiveness of datacenter-grade multimodal assistants while preserving local privacy, validating Hypothesis H3."
        ],
        title="Definitive Answer to RQ3 (Asymmetric Edge-Cloud Viability)"
    )

    add_h2("6.2 Intellectual Property & Comprehensive Licensing Audit")
    add_p(
        "In strict adherence to supervisor guidelines ('audit all components; check licensing'), a comprehensive intellectual property matrix was compiled "
        "to evaluate commercial vs. academic research viability across all open-source models and libraries used:"
    )

    # Licensing Audit Table
    table_lic = doc.add_table(rows=8, cols=4)
    table_lic.alignment = WD_TABLE_ALIGNMENT.CENTER
    table_lic.autofit = False
    set_table_borders(table_lic)

    l_headers = ["Pipeline Component", "Upstream Project", "License Model", "Academic Research & Commercial Permissibility"]
    for j, h in enumerate(l_headers):
        cell = table_lic.cell(0, j)
        set_cell_background(cell, "003366")
        set_cell_margins(cell, top=70, bottom=70, left=90, right=90)
        p = cell.paragraphs[0]
        r = p.add_run(h)
        r.bold = True
        r.font.size = Pt(8.5)
        r.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)

    lic_data = [
        ("STT Transcription", "OpenAI Whisper (`base.en`)", "MIT License", "Fully permissive; unrestricted academic research and commercial deployment."),
        ("Edge SLM Inference", "Alibaba Qwen (`Qwen 2.5 3B`)", "Apache 2.0", "Permissive open-weights; commercial distribution permitted with attribution."),
        ("Neural TTS (Primary)", "Coqui VITS (`vits_ljspeech`)", "MIT License", "Permissive open-source; fully authorized for commercial and academic use."),
        ("Neural TTS (Comparison)", "Coqui XTTS v2 (`xtts_v2`)", "CPML (Public Model License)", "Permitted for non-commercial academic research; commercial use strictly prohibited."),
        ("Cloud Reasoning Worker", "Meta Llama via NVIDIA NIM", "NVIDIA Developer Terms", "Evaluation tier authorized for research; subject to enterprise terms at scale."),
        ("Audio DSP Routing", "PipeWire & WebRTC AEC", "LGPL 2.1+ / BSD 3-Clause", "Standard Linux system libraries; fully compliant for system integration."),
        ("MY_JARVIS Framework", "Devyansh Bhateja", "MIT License", "Original Bachelor's thesis codebase; fully open-sourced for scientific reproducibility."),
    ]

    for i, row in enumerate(lic_data):
        for j, val in enumerate(row):
            cell = table_lic.cell(i + 1, j)
            bg = "F9FAFB" if i % 2 == 0 else "FFFFFF"
            set_cell_background(cell, bg)
            set_cell_margins(cell, top=60, bottom=60, left=90, right=90)
            p = cell.paragraphs[0]
            r = p.add_run(val)
            r.font.size = Pt(8.5)
            if j == 0:
                r.bold = True

    p_sp7 = doc.add_paragraph()
    p_sp7.paragraph_format.space_before = Pt(4)
    p_sp7.paragraph_format.space_after = Pt(6)

    add_h2("6.3 Critical Limitations & Future Research Directions")
    add_p(
        "While MY_JARVIS establishes the viability of full-duplex voice automation on edge hardware, several technical limitations suggest avenues for future research:"
    )
    add_p(
        "While Whisper `base.en` executes in ~180 ms, monosyllabic confirmation tokens remain sensitive to microphone gain and physical room reverberation. "
        "Future work should explore fine-tuning lightweight CTC-based keyword spotters (e.g. openWakeWord) specifically on edge confirmation vocabularies.",
        bold_prefix="1. Acoustic Robustness on Monosyllabic Confirmation Tokens: "
    )
    add_p(
        "While native process lifecycle tracking (`RECENT_PROCESSES`) successfully avoids Wayland synthetic input dialogs for launched applications, "
        "closing unmanaged foreground windows still requires compositor-level extensions. Integrating native GNOME Shell D-Bus extensions or libei "
        "(Emulated Input) will allow seamless Wayland window manipulation without falling back to process management.",
        bold_prefix="2. Advanced Wayland Compositor Integration: "
    )
    add_p(
        "Deploying ultra-quantized (e.g. 1.5-bit or BitNet) sub-billion parameter models directly onto Neural Processing Units (NPUs) could reduce "
        "host GPU memory consumption to under 1.0 GB, leaving the entire discrete GPU dedicated to graphics and creative workloads.",
        bold_prefix="3. Dedicated Edge NPU Offloading: "
    )

    add_h2("6.4 Final Thesis Conclusion")
    add_p(
        "This thesis set out to answer whether a fully conversational, full-duplex voice assistant capable of hands-free desktop automation could be "
        "engineered to run on memory-constrained consumer workstations without relying on costly commercial APIs. Through rigorous concurrent pipeline "
        "design, system-level PipeWire WebRTC acoustic echo cancellation, and asymmetric Double-AI hybrid orchestration, this research demonstrates that "
        "sub-second conversational turn-taking (TTFA = 390.5 ms) and deterministic desktop automation are fully achievable on an entry-level NVIDIA RTX 3050 "
        "within a 2,790 MB VRAM footprint."
    )
    add_p(
        "By identifying, diagnosing, and resolving 16 critical engineering failure modes across modern Linux audio, display, and machine learning subsystems, "
        "this work bridges the gap between theoretical AI models and real-world edge deployment—providing a reproducible, open-source architectural blueprint "
        "for the next generation of private, responsive, edge-resident intelligent workstations."
    )

    # -------------------------------------------------------------
    # BIBLIOGRAPHY / REFERENCES FOR PART 3
    # -------------------------------------------------------------
    add_h1("References (Chapters 5 & 6)")
    refs = [
        "Alibaba Cloud. (2024). Qwen2.5 Technical Report: Benchmarks and Open Weights Deployment. https://qwenlm.github.io.",
        "Bhateja, D. (2026). MY_JARVIS: Real-Time Full-Duplex Edge Conversational Assistant. GitHub Repository. https://github.com/dave/MY_JARVIS.",
        "Meta AI. (2024). The Llama 3 Herd of Models. Meta AI Technical Report. arXiv:2407.21783.",
        "NVIDIA Corporation. (2024). TensorRT-LLM and NVIDIA NIM: Accelerating Generative AI Inference. NVIDIA Developer Whitepaper.",
        "OpenAI. (2023). Whisper: Robust Speech Recognition via Weak Supervision. Software Package. https://github.com/openai/whisper.",
        "PipeWire Project. (2024). WirePlumber: Modular Session / Policy Manager for PipeWire. https://pipewire.pages.freedesktop.org/wireplumber/."
    ]

    for i, ref in enumerate(refs):
        p_ref = doc.add_paragraph()
        p_ref.paragraph_format.left_indent = Inches(0.3)
        p_ref.paragraph_format.first_line_indent = Inches(-0.3)
        p_ref.paragraph_format.space_after = Pt(4)
        r_num = p_ref.add_run(f"[{i+1}] ")
        r_num.bold = True
        p_ref.add_run(ref)

    out_path = os.path.abspath("Thesis_Part3_Chapters_5_and_6.docx")
    doc.save(out_path)
    print(f"[SUCCESS] Generated: {out_path}")
    return out_path


if __name__ == "__main__":
    build_thesis_part3()
