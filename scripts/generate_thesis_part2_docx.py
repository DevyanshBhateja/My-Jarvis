"""Generate a publication-grade Word Document (.docx) for Thesis Part 2 (Chapters 3 & 4).

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
    """Add a shaded callout box for architectural principles or formal theorems."""
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


def build_thesis_part2():
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
    r_series = p_top.add_run("BACHELOR'S THESIS — PART 2 OF 3\n")
    r_series.font.size = Pt(12)
    r_series.font.bold = True
    r_series.font.color.rgb = RGBColor(0x00, 0x55, 0x99)

    r_title = p_top.add_run("Real-Time Full-Duplex Conversational AI and Desktop Automation on Memory-Constrained Edge Workstations\n")
    r_title.font.size = Pt(18)
    r_title.font.bold = True
    r_title.font.color.rgb = RGBColor(0x11, 0x11, 0x11)

    r_subtitle = p_top.add_run("Chapters 3 & 4: System Architecture, Concurrent Pipelining Design & The 16 Engineering Challenges\n")
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

    # Executive Overview Callout
    add_callout(
        doc,
        [
            "This document constitutes Part 2 of the formal Bachelor's Dissertation, detailing the technical implementation, "
            "asynchronous concurrency architecture, and empirical engineering challenges encountered while building a real-time "
            "full-duplex conversational voice assistant within a 4GB VRAM envelope.",
            "Chapter 3 introduces the multi-threaded interaction orchestrator, the Asymmetric 'Double-AI' duplex model, "
            "the sentence-bounded streaming token chunker, PipeWire WebRTC digital signal processing, two-tier command safety containment, "
            "and deterministic process lifecycle tracking under Wayland.",
            "Chapter 4 provides a comprehensive academic analysis of the 16 real-world engineering failures and negative results "
            "discovered during development and live demonstration—ranging from speaker acoustic bleed and Whisper short-utterance hallucinations "
            "to Mutter Wayland security dialogs, host terminal suicide process teardown, and PortAudio C-thread deadlocks."
        ],
        title="Part 2 Executive Overview"
    )

    # =============================================================
    # CHAPTER 3: SYSTEM ARCHITECTURE & IMPLEMENTATION
    # =============================================================
    add_h1("Chapter 3: System Architecture & Implementation")

    add_h2("3.1 Architectural Principles: The Modular Full-Duplex Philosophy")
    add_p(
        "Building a conversational voice agent capable of executing desktop actions on memory-constrained hardware requires departing "
        "from monolithic end-to-end architectures. The primary architectural objective of MY_JARVIS is the complete decoupling of "
        "perceptual responsiveness (speech recognition, token streaming, and vocalization) from symbolic tool planning and operating system execution. "
        "The system operates according to three core design invariants:"
    )
    add_p(
        "A conversational voice agent must never enforce half-duplex turn-taking. The microphone capture pipeline must remain active, "
        "filtering audio and evaluating speech boundaries even while the assistant's speech synthesizer is actively driving physical loudspeakers.",
        bold_prefix="1. Continuous Acoustic Presence: "
    )
    add_p(
        "The user must never wait for an entire language model generation to finish before hearing audio output. Streaming tokens must be "
        "transformed into spoken acoustic units in small, natural phonological increments as early as token reception permits.",
        bold_prefix="2. Sub-Second Time-to-First-Audio (TTFA): "
    )
    add_p(
        "The combined GPU VRAM allocation of the transcription model, language model, speech synthesis model, and operating system display server "
        "must remain strictly below 3,500 MB at all times, guaranteeing at least 500 MB of VRAM headroom for host desktop multitasking.",
        bold_prefix="3. Deterministic Memory Budgeting: "
    )

    add_h2("3.2 The Four-Thread Concurrent Pipelining Model")
    add_p(
        "To achieve full-duplex responsiveness without race conditions, the runtime is organized as an asynchronous four-worker pipeline "
        "managed by a central Interaction Orchestrator (`jarvis_rt/interaction_orchestrator.py`). Each worker runs as an independent daemon thread "
        "communicating across bounded, thread-safe FIFO queues:"
    )

    # 4-Thread Pipeline Table
    table_threads = doc.add_table(rows=5, cols=4)
    table_threads.alignment = WD_TABLE_ALIGNMENT.CENTER
    table_threads.autofit = False
    set_table_borders(table_threads)

    th_headers = ["Worker Thread", "Core Functionality", "Input / Output Boundary", "Concurrency Primitives"]
    for j, h in enumerate(th_headers):
        cell = table_threads.cell(0, j)
        set_cell_background(cell, "003366")
        set_cell_margins(cell, top=80, bottom=80, left=100, right=100)
        p = cell.paragraphs[0]
        r = p.add_run(h)
        r.bold = True
        r.font.size = Pt(9)
        r.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)

    th_data = [
        ("The Listen Thread", "Captures 16 kHz 16-bit PCM frames from PortAudio; evaluates dual-gate WebRTC VAD; detects speech start and end boundaries.", "Audio Stream ⟶ VAD Queue ⟶ Transcriber Queue", "Atomic boolean `is_listening`; dynamic energy threshold."),
        ("The Converse Thread", "Consumes transcribed text from Whisper; dispatches prompt to LLM Router; streams tokens into text chunker.", "Transcriber Queue ⟶ LLM Stream ⟶ TTS Chunk Queue", "Thread-safe `ChatHistory`; non-blocking token generator."),
        ("The Speak Thread", "Consumes text chunks; executes neural TTS synthesis via Coqui VITS; spawns `pw-play` subprocess for acoustic playback.", "TTS Chunk Queue ⟶ Audio Subprocess ⟶ Loudspeakers", "Atomic `interrupt_requested` flag; `subprocess.Popen.kill()`."),
        ("The Action Thread", "Parses structured `ACTION:` blocks; evaluates security whitelist; executes POSIX primitives or launches background cloud reasoning.", "Action Directive Queue ⟶ OS Primitive / Cloud NIM", "Two-tier approval barrier; `RECENT_PROCESSES` tracking stack."),
    ]

    for i, row in enumerate(th_data):
        for j, val in enumerate(row):
            cell = table_threads.cell(i + 1, j)
            bg = "F9FAFB" if i % 2 == 0 else "FFFFFF"
            set_cell_background(cell, bg)
            set_cell_margins(cell, top=70, bottom=70, left=100, right=100)
            p = cell.paragraphs[0]
            r = p.add_run(val)
            r.font.size = Pt(8.5)
            if j == 0:
                r.bold = True

    p_sp = doc.add_paragraph()
    p_sp.paragraph_format.space_before = Pt(4)
    p_sp.paragraph_format.space_after = Pt(6)

    add_h2("3.3 Asymmetric 'Double-AI' Hybrid Duplex Architecture")
    add_p(
        "A central innovation of this thesis is the Asymmetric 'Double-AI' Duplex model (formalized in `ADR-003`). Edge workstations face a fundamental "
        "dilemma: local models small enough to fit in edge VRAM (e.g. 3B parameters) possess limited multi-step tool reasoning, while massive models "
        "(70B+ parameters) require cloud hosting and suffer from unpredictable network latency jitter."
    )
    add_p(
        "Our architecture reconciles this tension by decoupling the conversational voice loop from the reasoning planning loop:"
    )
    add_p(
        "A quantized `Qwen 2.5 3B Instruct` model running locally in GPU VRAM via Ollama. It evaluates every user utterance with a mean "
        "Time-to-First-Token under 40 milliseconds. For standard conversational queries and direct desktop commands, Tier 1 directly streams tokens "
        "to the TTS engine. For complex queries requiring deep planning, Tier 1 immediately synthesizes natural spoken backchanneling tokens "
        "('Analyzing your request now...', 'Checking system performance...'), completely masking cloud latency.",
        bold_prefix="Tier 1: The Local Edge Conversational Loop: "
    )
    add_p(
        "A high-parameter model (`meta/llama-3.3-70b-instruct` or `meta/llama-3.2-90b-vision-instruct`) hosted on NVIDIA NIM cloud developer endpoints. "
        "Tier 2 executes asynchronously in the background. It consumes complex diagnostic prompts or multi-step action scripts, returning structured "
        "actions back to the Action Worker without consuming a single megabyte of local edge VRAM.",
        bold_prefix="Tier 2: The Asynchronous Cloud Reasoning Worker: "
    )

    add_h2("3.4 Token-Level Streaming and Sentence-Bounded TTS Chunking")
    add_p(
        "To achieve sub-second Time-to-First-Audio (TTFA), the assistant implements a dual-trigger sentence-bounded text chunker (`jarvis_rt/tts_stream.py`, `ADR-004`). "
        "Rather than waiting for the entire LLM response to complete, the chunker evaluates tokens as they arrive from the generator stream:"
    )
    add_p(
        "If an incoming token contains terminating punctuation ('.', '!', '?', or '\\n'), the buffered text is immediately flushed to the TTS queue. "
        "This guarantees that the speech synthesizer receives complete semantic clauses, preserving natural prosody and intonation.",
        bold_prefix="Trigger 1: Clause Boundary Punctuation: "
    )
    add_p(
        "If a clause is unusually long, waiting for a full stop would reintroduce perceptible latency. Therefore, if the token buffer reaches 12 tokens "
        "and encounters an intermediate pause (comma, semicolon, colon, or dash), it immediately dispatches the chunk. If the buffer exceeds 18 tokens "
        "without any punctuation, it forces a chunk boundary at the nearest word boundary.",
        bold_prefix="Trigger 2: Token Count Ceiling (12–18 Tokens): "
    )
    add_p(
        "This dual-trigger mechanism compresses the delay between LLM token generation and speech playback to the duration of synthesizing a single clause "
        "(~150–250 ms), enabling a total system TTFA consistently under 400 milliseconds."
    )

    add_h2("3.5 System-Level Digital Signal Processing & PipeWire WebRTC AEC Integration")
    add_p(
        "Achieving continuous listening during assistant speech output requires robust Acoustic Echo Cancellation (AEC). As established in `ADR-002`, "
        "software-level muting converts the system into a half-duplex walkie-talkie. MY_JARVIS interfaces directly with Linux PipeWire's graph-based "
        "audio processing subsystem using `libpipewire-module-echo-cancel`."
    )
    add_p(
        "The filter chain creates two virtual audio nodes in the PipeWire graph: an `echo-cancel-sink` and an `echo-cancel-source`. "
        "When the speech player outputs audio, the synthesized PCM samples are routed to the echo-cancel sink, which serves as the reference signal. "
        "The WebRTC AEC filter continuously cross-correlates the physical microphone input with the reference signal, performing frequency-domain adaptive "
        "filtering to subtract speaker acoustic bleed. Furthermore, `action_executor.py` automatically injects hardware-safe ceiling limiters "
        "(`wpctl set-volume -l 1.0 @DEFAULT_SINK@`) to guarantee that speaker audio never exceeds 100% gain, preventing digital clipping and nonlinear "
        "speaker distortions that would break AEC filter convergence."
    )

    add_h2("3.6 Two-Tier Desktop Action Containment & Safety Policy")
    add_p(
        "Autonomous operating system automation introduces severe safety hazards. If an unconstrained language model is granted raw shell execution privileges, "
        "hallucinated commands can corrupt the file system or terminate critical processes. To resolve this, MY_JARVIS implements a strict Two-Tier "
        "Command Containment Architecture (`ADR-005`):"
    )
    add_p(
        "Safe, read-only system diagnostic utilities (`top -b -n1`, `upower -i`, `hostname -I`, `free -h`) and sandboxed application launchers "
        "(`open_app('firefox')`, `open_app('nautilus')`). These commands mutate no permanent state and execute instantly with zero user confirmation overhead.",
        bold_prefix="Tier 1 (Auto-Approved Actions): "
    )
    add_p(
        "State-mutating system operations (closing active applications, adjusting system volume, or locking the workstation). "
        "Tier 2 actions require explicit confirmation. The assistant prompts the user ('Approve action: [command]?'), which can be confirmed by voice ('yes', 'proceed') "
        "or terminal input (`[y/N]`) within a 10-second timeout window.",
        bold_prefix="Tier 2 (Human-in-the-Loop Confirmation): "
    )
    add_p(
        "In addition, `action_executor.py` enforces a strict whitelist and regex-validated boundary: any command string not matching the authorized "
        "Frozen Fedora catalog is rejected with an explicit vocal telemetry message ('I cannot execute that command; it is outside my authorized capabilities.')."
    )

    add_h2("3.7 Process Lifecycle Tracking vs. Wayland Synthetic Keystrokes")
    add_p(
        "A critical systems-level contribution of this thesis is resolving the Wayland client isolation barrier (`PRB-015`). Under modern Fedora GNOME/Wayland, "
        "injecting synthetic keystrokes via X11 automation libraries (`pyautogui.hotkey('alt', 'f4')`) is intercepted by Mutter as an unauthorized remote "
        "desktop intrusion, presenting a blocking permission dialog."
    )
    add_p(
        "MY_JARVIS replaces synthetic input with a deterministic **Process Lifecycle Management Stack** (`RECENT_PROCESSES` in `system_actions.py`). "
        "Whenever the assistant launches an application (`CMD-01` to `CMD-03`), the spawned `subprocess.Popen` handle is registered into an active process stack. "
        "When the user commands 'Close this window' (`CMD-04`), the system pops the most recent process handle and issues a graceful POSIX `SIGTERM`. "
        "Furthermore, to guarantee host environment stability (`PRB-016`), critical development processes (`ptyxis`, `gnome-terminal`, `bash`, `python`, `code`) "
        "are hardcoded into an immune system list: the action executor permanently refuses to terminate any process belonging to the assistant's own process hierarchy."
    )

    add_h2("3.8 Decoupled Zero-VRAM Holographic HUD Architecture")
    add_p(
        "To provide rich visual telemetry (Arc Reactor core status, audio reactive waveforms, token-by-token streaming, and GPU VRAM monitoring) without "
        "consuming scarce edge VRAM, MY_JARVIS implements a decoupled Holographic HUD (`jarvis_ui/`, `ADR-009`). The HUD runs as a standalone lightweight "
        "browser-anchored client communicating with the backend over local inter-process WebSocket streams. Because the UI renders via hardware-accelerated "
        "browser canvas without bundling separate PyTorch dependencies, it imposes zero additional VRAM overhead on the assistant runtime."
    )

    # =============================================================
    # CHAPTER 4: PRACTICAL ENGINEERING CHALLENGES & NEGATIVE RESULTS
    # =============================================================
    doc.add_page_break()
    add_h1("Chapter 4: Practical Engineering Challenges & The 16 Empirical Failure Modes")

    add_h2("4.1 The Methodology of Negative Results in Applied Edge AI")
    add_p(
        "Academic literature in artificial intelligence frequently suffers from publication bias: papers showcase idealized benchmarks while omitting the "
        "myriad practical engineering failures that occur when deploying theoretical models onto real hardware. In edge-based full-duplex conversational "
        "systems, however, system stability is entirely determined by how gracefully the architecture handles physical audio bleed, thread deadlocks, "
        "and memory thrashing."
    )
    add_p(
        "In strict adherence to supervisor guidelines ('minimal testing: test time and accuracy, mention the problems'), this chapter documents all 16 "
        "empirical failure modes discovered, diagnosed, and resolved during the research. Each problem report tracks: (1) Symptoms, (2) Root Cause, "
        "(3) Failed Attempts, and (4) The Working Solution."
    )

    # 16 Problems Summary Table
    table_prb = doc.add_table(rows=17, cols=4)
    table_prb.alignment = WD_TABLE_ALIGNMENT.CENTER
    table_prb.autofit = False
    set_table_borders(table_prb)

    prb_headers = ["ID", "Failure Mode Category", "Observed Symptom / Negative Result", "Engineered Resolution"]
    for j, h in enumerate(prb_headers):
        cell = table_prb.cell(0, j)
        set_cell_background(cell, "003366")
        set_cell_margins(cell, top=70, bottom=70, left=90, right=90)
        p = cell.paragraphs[0]
        r = p.add_run(h)
        r.bold = True
        r.font.size = Pt(8.5)
        r.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)

    prb_data = [
        ("PRB-001", "Acoustic Feedback", "Assistant replied to its own voice in an infinite loop.", "Integrated PipeWire WebRTC AEC filter graph (`ADR-002`)."),
        ("PRB-002", "ASR Hallucination", "Whisper hallucinated YouTube tags on 'yes'/'stop'.", "Enforced 300ms pre-padding, disabled prior text condition."),
        ("PRB-003", "VRAM Contention", "Coqui XTTS v2 caused CUDA OOM when opening Firefox.", "Pinned Coqui VITS (300MB) as primary operational engine (`ADR-001`)."),
        ("PRB-004", "Audio Subprocess Hang", "Playback deadlocked with `ffplay` on PipeWire.", "Migrated to native PipeWire `pw-play` with non-blocking stream."),
        ("PRB-005", "Virtual Source Attenuation", "AEC source defaulted to 0% volume (-inf dB).", "Scripted automated WirePlumber sink/source initialization volume."),
        ("PRB-006", "VAD Noise Cascade", "Ambient room noise triggered multilingual hallucinations.", "Implemented dual-gate energy thresholding before WebRTC VAD."),
        ("PRB-007", "Thread Deadlock", "Non-daemon worker threads prevented Ctrl+C shutdown.", "Strictly daemonized all audio/LLM workers; added shutdown hooks."),
        ("PRB-008", "Command Hallucination", "SLM hallucinated 'shutdown now'; hung on stdin.", "Enforced strict whitelist barrier and non-blocking select input."),
        ("PRB-009", "Silent Action Execution", "Actions executed without user spoken feedback.", "Added spoken vocal telemetry formatting for all actions (`ADR-005`)."),
        ("PRB-010", "Audio Stream Collision", "Multiple audio playback streams overlapped simultaneously.", "Added central playback mutex and atomic process kill."),
        ("PRB-011", "Cloud Token Exhaustion", "Reasoning tokens exhausted NIM budget; split-brain.", "Pinned max_tokens=1024 and unified edge vocal synthesis (`ADR-007`)."),
        ("PRB-012", "Subprocess Terminal Leak", "GUI browser launch flooded terminal with stderr logs.", "Redirected subprocess stdout/stderr to `/dev/null`."),
        ("PRB-013", "Temporal Entity Hallucination", "SLM hallucinated day of week in weather commands.", "Injected real-time system date anchor into system prompt."),
        ("PRB-014", "PortAudio Shutdown Freeze", "C-level PortAudio stream blocked process termination.", "Added explicit `stream.abort()` and C-stream cleanup handlers."),
        ("PRB-015", "Wayland Keystroke Security", "GNOME showed 'Remote Desktop' dialog on window close.", "Replaced synthetic keys with native Process Lifecycle Stack."),
        ("PRB-016", "Terminal Process Suicide", "Browser close fallback killed parent `ptyxis` terminal.", "Immunized host terminal processes; pinned stable Cloud 90B model."),
    ]

    for i, row in enumerate(prb_data):
        for j, val in enumerate(row):
            cell = table_prb.cell(i + 1, j)
            bg = "F9FAFB" if i % 2 == 0 else "FFFFFF"
            set_cell_background(cell, bg)
            set_cell_margins(cell, top=60, bottom=60, left=90, right=90)
            p = cell.paragraphs[0]
            r = p.add_run(val)
            r.font.size = Pt(8)
            if j == 0:
                r.bold = True

    p_sp4 = doc.add_paragraph()
    p_sp4.paragraph_format.space_before = Pt(4)
    p_sp4.paragraph_format.space_after = Pt(6)

    # In-Depth Problem Sections
    add_h2("4.2 Detailed Analysis: Acoustic Feedback & The Failure of Software Mic-Muting (PRB-001)")
    add_p(
        "During initial end-to-end testing, the assistant entered a runaway feedback loop within 200 milliseconds of initiating speech. "
        "Because the physical microphone capsule remained open, the synthesized speech emitted by the laptop speakers was captured as new input. "
        "Whisper transcribed the assistant's own voice, the SLM generated a follow-up response, and the system spoke again indefinitely."
    )
    add_p(
        "Attempting to solve this by temporarily pausing microphone input (`mic.pause()`) proved to be an architectural failure: while eliminating echo, "
        "it reduced the system to a half-duplex walkie-talkie. If the assistant began speaking an inaccurate answer, the user could not interrupt mid-sentence. "
        "The working solution required integrating system-level Acoustic Echo Cancellation via PipeWire's `libpipewire-module-echo-cancel` (`ADR-002`), "
        "which continuously subtracts speaker reference audio from the microphone stream in real time, permitting continuous listening and sub-200ms barge-in."
    )

    add_h2("4.3 Detailed Analysis: Whisper Short-Utterance Hallucination (PRB-002)")
    add_p(
        "In desktop automation, voice confirmation dialogues require high precision on monosyllabic words ('yes', 'stop', 'no'). "
        "Standard Whisper models, optimized for long-form continuous speech, exhibited acute hallucinations when transcribing audio bursts under 500 ms. "
        "When a user whispered 'yes', Whisper routinely emitted phantom phrases such as 'Thank you for watching!', 'Subtitles by...', or repeated fragments "
        "from prior conversational turns."
    )
    add_p(
        "The root cause was two-fold: (1) aggressive VAD trimming clipped initial plosive consonants, leaving insufficient spectral context, and "
        "(2) enabling `condition_on_previous_text=True` biased the autoregressive decoder toward prior dialogue history. The fix required enforcing 300 ms "
        "pre-speech acoustic padding, disabling prior-text conditioning, and applying digital peak normalization prior to inference."
    )

    add_h2("4.4 Detailed Analysis: VRAM Contention on 4GB Edge Workstations (PRB-003)")
    add_p(
        "Consumer laptops featuring the NVIDIA RTX 3050 impose an unyielding 4096 MB VRAM ceiling. While modern autoregressive and diffusion-based TTS "
        "models (such as Coqui XTTS v2) offer superior voice naturalness, their ~1.6 GB footprint, combined with local SLM execution (1.9 GB) and Whisper (250 MB), "
        "leaves less than 250 MB of VRAM headroom. Under standard desktop operations—such as executing `CMD-01` to open Firefox—the Wayland display server "
        "allocated GPU memory buffers that triggered fatal CUDA Out-Of-Memory exceptions (`RuntimeError: CUDA out of memory. Tried to allocate 128.00 MiB`)."
    )
    add_p(
        "The resolution required adopting a dual-model strategy (`ADR-001`): deploying lightweight non-autoregressive models (Coqui VITS, ~300 MB) "
        "for real-time memory stability (total model footprint: 2,450 MB; 1,646 MB headroom) while preserving XTTS v2 strictly as an isolated off-line benchmark."
    )

    add_h2("4.5 Detailed Analysis: Wayland Synthetic Keystroke Rejection & Dynamic Volume Whitelist (PRB-015)")
    add_p(
        "During live demonstration, two significant edge automation barriers emerged:"
    )
    add_p(
        "When executing `CMD-04` ('Close this window'), the assistant initially called `pyautogui.hotkey('alt', 'f4')`. Under Fedora GNOME, "
        "Mutter's Wayland security portal intercepted the synthetic key event and generated a blocking security modal: 'Remote Desktop: Allow Remote Interaction'. "
        "This completely halted the pipeline until manual mouse consent was granted.",
        bold_prefix="1. Wayland Synthetic Input Rejection: "
    )
    add_p(
        "When the user asked 'Can you set the volume to 50%?', the SLM emitted `ACTION: run_command('wpctl set-volume -l 1.0 @DEFAULT_SINK@ 50%+')`. "
        "Because the safety catalog only matched rigid fixed increments (`5%+`, `5%-`), the command was rejected as an unauthorized capability.",
        bold_prefix="2. Rigid String Matching Rejection: "
    )
    add_p(
        "The fixes directly established key thesis contributions: (1) replacing synthetic keystrokes with native process lifecycle management "
        "(`proc.terminate()`), completely eliminating the Wayland modal dialog; and (2) implementing safe regex matching for arbitrary volume percentages "
        "with hardware ceiling limiters (`-l 1.0`) enforced by default."
    )

    add_h2("4.6 Detailed Analysis: Host Terminal Suicide & Cloud NIM Endpoint Pinning (PRB-016)")
    add_p(
        "In a live demonstration test, the assistant opened a browser window and the user commanded 'Close the opened brave window'. "
        "Because the browser process was launched via `xdg-open` without being registered into `RECENT_PROCESSES`, the queue was empty. "
        "The fallback loop iterated through approved process names and executed `pkill -f ptyxis`. Because the assistant, IDE server, and terminal session "
        "were all running inside Ptyxis (Fedora's default terminal emulator), the assistant terminated its own parent process, crashing the entire session."
    )
    add_p(
        "In addition, dispatching background reasoning to NVIDIA NIM failed with HTTP 404 (`Function not found for account`) because the preview endpoint "
        "had been retired on developer accounts. The resolution established two critical safeguards: (1) hardcoded terminal immunization permanently "
        "forbidding termination of `ptyxis`, `gnome-terminal`, `bash`, `python`, or `code`; and (2) pinning verified stable cloud models (`meta/llama-3.2-90b-vision-instruct`) "
        "benchmarked live across 84 available endpoints."
    )

    add_h2("4.7 Summary & Transition to Empirical Evaluation")
    add_p(
        "The 16 engineering challenges documented in this chapter illustrate the profound divergence between theoretical AI models and real-world system engineering. "
        "By identifying, root-causing, and resolving each failure mode, MY_JARVIS achieved deterministic full-duplex conversational interaction on constrained edge hardware."
    )
    add_p(
        "With the system architecture and engineering safeguards fully described, Part 3 of this thesis (Chapters 5 & 6) presents the comprehensive quantitative "
        "empirical benchmark evaluation—measuring TTFT, TTFA, intent recognition accuracy, and VRAM utilization across the 10 Frozen Fedora commands."
    )

    # -------------------------------------------------------------
    # BIBLIOGRAPHY / REFERENCES FOR PART 2
    # -------------------------------------------------------------
    add_h1("References (Chapters 3 & 4)")
    refs = [
        "Coqui Community. (2023). Coqui TTS: Fast, Multi-Speaker Neural Text-to-Speech Engine. https://github.com/coqui-ai/TTS.",
        "FreeDesktop.org. (2024). Desktop Linux Inter-Process Communication and D-Bus Specification. https://freedesktop.org.",
        "Google. (2022). WebRTC Voice Engine and Echo Cancellation 3. Google Technical Documentation.",
        "NVIDIA Corporation. (2024). NVIDIA Inference Microservices (NIM) Architecture Overview and API Reference. NVIDIA Developer Documentation.",
        "Ollama Project. (2024). Ollama: Run Large Language Models Locally. https://ollama.com.",
        "PipeWire Project. (2023). PipeWire Filter-Chain and Echo-Cancel Module Architecture. https://docs.pipewire.org.",
        "Red Hat Inc. (2024). Fedora Workstation 40 Systems Administration Guide: GNOME, Mutter, and Wayland Security Protocols."
    ]

    for i, ref in enumerate(refs):
        p_ref = doc.add_paragraph()
        p_ref.paragraph_format.left_indent = Inches(0.3)
        p_ref.paragraph_format.first_line_indent = Inches(-0.3)
        p_ref.paragraph_format.space_after = Pt(4)
        r_num = p_ref.add_run(f"[{i+1}] ")
        r_num.bold = True
        p_ref.add_run(ref)

    out_path = os.path.abspath("Thesis_Part2_Chapters_3_and_4.docx")
    doc.save(out_path)
    print(f"[SUCCESS] Generated: {out_path}")
    return out_path


if __name__ == "__main__":
    build_thesis_part2()
