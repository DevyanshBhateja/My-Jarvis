---
id: PRB-007
title: Non-Daemon Thread Deadlock on SIGINT (Ctrl+C Shutdown Freeze)
research_question: "[[Research_Questions|RQ1]]"
status: Solved
tags: [problem, failed-attempt, solution, rq1, threading, linux, signal, shutdown]
related: ["[[00_Map_of_Content]]", "[[PRB-004_PipeWire_Native_Player_Selection]]"]
---

# ⚠️ PRB-007: Non-Daemon Thread Deadlock on SIGINT (Ctrl+C Shutdown Freeze)

## 1. Problem Description & Symptoms
When running `python main.py` in the terminal, pressing `Ctrl+C` repeatedly failed to terminate the assistant:
- Symptoms: `^C^C^C^C^C` printed across the terminal, but the process remained stuck running in the background.
- Stack trace inspection revealed Python's runtime `threading._shutdown()` was blocked acquiring thread join locks:
  ```text
  Exception ignored in: <module 'threading' from '/usr/lib64/python3.11/threading.py'>
  Traceback (most recent call last):
    File "/usr/lib64/python3.11/threading.py", line 1581, in _shutdown
      lock.acquire()
  KeyboardInterrupt
  ```
- The user had to kill the terminal emulator window to close the application.

---

## 2. Failed Attempts & Negative Results (Thesis Discussion)

### Failed Attempt 1: Blocking `Event.wait()` in Main Thread
- **What was tried**: Kept main thread suspended using `self.stop_event.wait()` with a `try...except KeyboardInterrupt` block.
- **Negative Result**: In Python on Linux, when background C extensions (e.g., PyTorch, SoundDevice, WebRTC) hold the GIL or handle signals, `Event.wait()` without a timeout translates to a low-level `pthread_cond_wait()`. Signals like `SIGINT` are queued by the OS but delayed from propagating Python's `KeyboardInterrupt` until the condition variable unblocks.

### Failed Attempt 2: Non-Daemon Worker Threads (`daemon=False`)
- **What was tried**: Created worker threads (`Listen`, `Converse`, `Speak`, `Action`) as non-daemon threads (`daemon=False`) to ensure graceful cleanup.
- **Negative Result**: If even a single thread is waiting on an external I/O queue (`utterance_queue.get()`) or a streaming HTTP socket from Ollama, Python's runtime teardown hook `threading._shutdown()` calls `join()` with **no timeout** on all non-daemon threads. This creates an unrecoverable process freeze.

---

## 3. Working Solution & Root Cause Analysis

### The Fix
1. **Daemonized Worker Threads (`interaction_orchestrator.py`)**:
   - Explicitly configured all orchestrator loops as daemon threads:
     ```python
     thread = threading.Thread(target=target, daemon=True, name=f"Orch{name.capitalize()}")
     ```
   - Daemon threads are forcibly terminated by the OS when the main thread exits, preventing `threading._shutdown()` from locking up.
2. **Periodic Signal Slicing Loop (`interaction_orchestrator.py`)**:
   - Replaced infinite `self.stop_event.wait()` with a periodic polling loop (`time.sleep(0.2)`):
     ```python
     while not self.stop_event.is_set():
         time.sleep(0.2)
     ```
   - This ensures the Python interpreter checks pending OS signal flags at 5 Hz, guaranteeing sub-200ms `KeyboardInterrupt` delivery.
3. **Dedicated OS Signal Handlers (`main.py`)**:
   - Registered POSIX signal handlers for both `SIGINT` and `SIGTERM`:
     ```python
     def _sig_handler(signum, frame) -> None:
         print("\n[MAIN] Caught interrupt signal, shutting down Jarvis cleanly...")
         try:
             controller.shutdown()
         except Exception:
             pass
         sys.exit(0)

     signal.signal(signal.SIGINT, _sig_handler)
     signal.signal(signal.SIGTERM, _sig_handler)
     ```
4. **Hands-Free Voice Exit Command (`interaction_orchestrator.py`)**:
   - Added natural speech exit trigger in `_handle_user_utterance`:
     If the user says *"exit"*, *"quit"*, *"shutdown"*, or *"goodbye"*, the assistant immediately flags `self.stop_event.set()` for hands-free termination.

---

## 4. Academic Thesis Contribution
- **Concurrency Lifecycle Management**: In high-throughput, multi-threaded edge conversational systems combining neural models and hardware audio streams, process termination cannot rely on standard Python runtime shutdown. 
- Explicit daemonization combined with POSIX signal interceptors and polling sleep slices are essential to prevent deadlock between Python's GIL, sound subsystem threads, and neural inference workers.
- **Thesis Reference**: Chapter 3 (System Architecture & Concurrency Model), Section 3.4 (Thread Lifecycle and Fault Recovery).
