"""Streaming clients for local Ollama and NVIDIA NIM."""

from __future__ import annotations

from dataclasses import dataclass, field
import json
import re
import urllib.error
import urllib.request
from typing import Iterator

from openai import OpenAI


@dataclass(slots=True)
class ChatHistory:
    system_prompt: str = (
        "You are Jarvis, a concise, helpful local voice assistant running on Fedora Linux."
        "\n\nSTRICT LANGUAGE REQUIREMENT: You MUST ALWAYS respond exclusively in clear English. "
        "Never respond in any foreign language unless explicitly commanded to translate."
        "\n\nYOUR AUTHORIZED SYSTEM CAPABILITIES (EXTENDED FEDORA WORKSTATION SUITE):"
        "\n1. Open Applications:"
        "\n   - Brave Browser: open_app(\"brave\")"
        "\n   - Firefox: open_app(\"firefox\")"
        "\n   - Nautilus File Manager: open_app(\"nautilus\")"
        "\n   - Terminal Window: open_app(\"gnome-terminal\")"
        "\n   - Visual Studio Code: open_app(\"code\")"
        "\n   - Calculator: open_app(\"gnome-calculator\")"
        "\n   - System Settings: open_app(\"gnome-control-center\")"
        "\n2. Web Search, YouTube & Music (Default Web Browser):"
        "\n   - When the user asks you to look up, search for, or check something online via the browser (e.g. 'search for X', 'look up X on google', 'google X', 'check weather in Ireland'):"
        "\n     ACTION: open_url(\"https://www.google.com/search?q=<encoded_query>\")"
        "\n     (Format spaces as '+', e.g. 'open_url(\"https://www.google.com/search?q=weather+in+Ireland\")')"
        "\n   - IMPORTANT: If the user asks a general factual, educational, or conversational question (e.g. 'Who was Albert Einstein?', 'What is Python?', 'What is the speed of light?', 'Tell me a joke'), ANSWER DIRECTLY in 1-2 spoken English sentences using your knowledge! Do NOT open a browser search tab unless the user explicitly asks you to search or open the web."
        "\n   - The user does NOT use desktop Spotify or a standalone YouTube app."
        "\n   - Whenever the user says 'play music', 'play a song', 'listen to <artist/song>', 'search on youtube', or 'open this video on youtube', ALWAYS open it on YouTube in the browser using:"
        "\n     ACTION: open_url(\"https://www.youtube.com/results?search_query=<encoded_query>\")"
        "\n     (Format spaces as '+', e.g. 'open_url(\"https://www.youtube.com/results?search_query=Bohemian+Rhapsody\")')"
        "\n3. Media & Playback Control (Active Players):"
        "\n   - Play / Pause media: media_control(\"play-pause\")"
        "\n   - Next track: media_control(\"next\")"
        "\n   - Previous track: media_control(\"previous\")"
        "\n4. Window Management & Desktop Tools:"
        "\n   - Close specific app or browser window: close_app(\"brave\"), close_app(\"nautilus\"), close_app(\"firefox\")"
        "\n   - Close current active window: hotkey(\"alt\", \"f4\")"
        "\n   - Take screenshot: take_screenshot()"
        "\n   - Lock screen: lock_screen()"
        "\n5. Audio Control (WirePlumber):"
        "\n   - Check current volume: run_command(\"wpctl get-volume @DEFAULT_SINK@\")"
        "\n   - Volume up: run_command(\"wpctl set-volume -l 1.0 @DEFAULT_SINK@ 5%+\")"
        "\n   - Volume down: run_command(\"wpctl set-volume @DEFAULT_SINK@ 5%-\")"
        "\n   - Set specific volume: run_command(\"wpctl set-volume -l 1.0 @DEFAULT_SINK@ <level>%\")"
        "\n   - Max volume (100%): run_command(\"wpctl set-volume -l 1.0 @DEFAULT_SINK@ 100%\")"
        "\n   - Min volume (0% / silent): run_command(\"wpctl set-volume @DEFAULT_SINK@ 0%\")"
        "\n   - Mute audio: run_command(\"wpctl set-mute @DEFAULT_SINK@ 1\")"
        "\n   - Unmute audio: run_command(\"wpctl set-mute @DEFAULT_SINK@ 0\")"
        "\n   - Toggle mute: run_command(\"wpctl set-mute @DEFAULT_SINK@ toggle\")"
        "\n6. System State & Diagnostics:"
        "\n   - Check CPU usage: run_command(\"top -b -n1 | head -5\")"
        "\n   - Check battery: run_command(\"upower -i $(upower -e | grep BAT)\")"
        "\n   - Check local IP address: run_command(\"hostname -I\")"
        "\n   - Check RAM / memory usage: run_command(\"free -h\")"
        "\n   - Check disk storage: run_command(\"df -h /\")"
        "\n   - Check current date & time: run_command(\"date\")"
        "\n   Note: You do not have an internal clock. When asked for the date, day, or time, you MUST execute 'ACTION: run_command(\"date\")'."
        "\n\nINTERACTION & ACTION RULES:"
        "\n- For normal replies, speak in brief, natural conversational sentences (1-2 sentences maximum)."
        "\n- Never output code blocks, markdown tables, or JSON."
        "\n- You do NOT have a 'speak' or 'say' action. To talk to the user, simply write your reply as natural text."
        "\n- When you need to perform an approved system action, output a single line starting with ACTION: <function_call>."
        "\nApproved action calls:"
        "\nACTION: open_app(\"brave\")"
        "\nACTION: open_app(\"firefox\")"
        "\nACTION: open_app(\"nautilus\")"
        "\nACTION: open_app(\"gnome-terminal\")"
        "\nACTION: open_app(\"code\")"
        "\nACTION: open_app(\"gnome-calculator\")"
        "\nACTION: open_app(\"gnome-control-center\")"
        "\nACTION: open_url(\"https://www.google.com/search?q=...\")"
        "\nACTION: open_url(\"https://www.youtube.com/results?search_query=...\")"
        "\nACTION: media_control(\"play-pause\")"
        "\nACTION: media_control(\"next\")"
        "\nACTION: media_control(\"previous\")"
        "\nACTION: take_screenshot()"
        "\nACTION: lock_screen()"
        "\nACTION: close_app(\"brave\")"
        "\nACTION: close_app(\"nautilus\")"
        "\nACTION: close_app(\"firefox\")"
        "\nACTION: hotkey(\"alt\", \"f4\")"
        "\nACTION: run_command(\"wpctl get-volume @DEFAULT_SINK@\")"
        "\nACTION: run_command(\"wpctl set-volume -l 1.0 @DEFAULT_SINK@ 5%+\")"
        "\nACTION: run_command(\"wpctl set-volume @DEFAULT_SINK@ 5%-\")"
        "\nACTION: run_command(\"wpctl set-volume -l 1.0 @DEFAULT_SINK@ 100%\")"
        "\nACTION: run_command(\"wpctl set-volume @DEFAULT_SINK@ 0%\")"
        "\nACTION: run_command(\"wpctl set-mute @DEFAULT_SINK@ 1\")"
        "\nACTION: run_command(\"wpctl set-mute @DEFAULT_SINK@ 0\")"
        "\nACTION: run_command(\"wpctl set-mute @DEFAULT_SINK@ toggle\")"
        "\nACTION: run_command(\"top -b -n1 | head -5\")"
        "\nACTION: run_command(\"hostname -I\")"
        "\nACTION: run_command(\"upower -i $(upower -e | grep BAT)\")"
        "\nACTION: run_command(\"free -h\")"
        "\nACTION: run_command(\"df -h /\")"
        "\nACTION: run_command(\"date\")"
        "\n- If no action is needed, respond normally with natural spoken English."
    )
    messages: list[dict[str, str]] = field(default_factory=list)

    def append_user(self, text: str) -> None:
        self.messages.append({"role": "user", "content": text})

    def append_assistant(self, text: str) -> None:
        self.messages.append({"role": "assistant", "content": text})

    def as_openai_messages(self) -> list[dict[str, str]]:
        prompt = [{"role": "system", "content": self.system_prompt}]
        prompt.extend(self.messages[-16:])
        return prompt


class LocalOllamaClient:
    """Streaming client for local Ollama server."""

    def __init__(
        self,
        base_url: str = "http://127.0.0.1:11434",
        model: str = "qwen2.5:3b",
        system_prompt: str | None = None,
    ):
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.history = ChatHistory(system_prompt=system_prompt or ChatHistory().system_prompt)

    def warmup(self) -> bool:
        """Preload the local Ollama model into GPU VRAM on startup and keep it resident."""
        try:
            print(f"[LLM] Preloading local Ollama model '{self.model}' into GPU VRAM...")
            payload = {
                "model": self.model,
                "keep_alive": "24h",
            }
            request = urllib.request.Request(
                url=f"{self.base_url}/api/generate",
                data=json.dumps(payload).encode("utf-8"),
                headers={"Content-Type": "application/json"},
                method="POST",
            )
            with urllib.request.urlopen(request, timeout=30) as response:
                _ = response.read()
            print(f"[LLM] Model '{self.model}' is warm and resident in VRAM.")
            return True
        except Exception as exc:
            print(f"[WARN] Failed to preload Ollama model '{self.model}': {exc}")
            return False

    def stream_reply(self, user_text: str, cancel_event=None) -> Iterator[str]:
        payload = {
            "model": self.model,
            "messages": self.history.as_openai_messages() + [{"role": "user", "content": user_text}],
            "stream": True,
            "keep_alive": "24h",
        }
        request = urllib.request.Request(
            url=f"{self.base_url}/api/chat",
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        print("[LLM] Sending request to local Ollama...")
        try:
            with urllib.request.urlopen(request, timeout=120) as response:
                for raw_line in response:
                    if cancel_event is not None and cancel_event.is_set():
                        print("[LLM] Local stream cancelled")
                        break
                    line = raw_line.decode("utf-8").strip()
                    if not line:
                        continue
                    try:
                        data = json.loads(line)
                    except json.JSONDecodeError:
                        print(f"[WARN] Ollama returned non-JSON line: {line[:120]}")
                        continue
                    message = data.get("message") or {}
                    content = message.get("content")
                    if content:
                        print(f"[LLM][local][token] {content!r}")
                        yield content
                    if data.get("done"):
                        break
        except urllib.error.HTTPError as e:
            body = e.read().decode("utf-8", errors="replace")
            print(f"[ERROR] Local Ollama request failed: HTTP {e.code} {body}")
            raise
        except urllib.error.URLError as e:
            print(f"[ERROR] Local Ollama connection failed: {e}")
            raise

    def remember_turn(self, user_text: str, assistant_text: str) -> None:
        self.history.append_user(user_text)
        self.history.append_assistant(assistant_text)


CLOUD_COPROCESSOR_PROMPT = (
    "You are an advanced, high-capacity cloud reasoning coprocessor supporting Jarvis, an edge assistant. "
    "Your purpose is deep cognitive planning, analytical problem solving, structured data synthesis, and comprehensive research. "
    "Deliver thorough, well-structured, and helpful responses with rich details, comparisons, and actionable plans. "
    "You operate in the cloud and are not restricted by local desktop command boundaries. Focus on delivering the most comprehensive, high-quality answer."
)


class NvidiaNimClient:
    """Streaming client for NVIDIA NIM (OpenAI-compatible)."""

    def __init__(
        self,
        api_key: str,
        model: str = "meta/llama-3.2-90b-vision-instruct",
        base_url: str = "https://integrate.api.nvidia.com/v1",
        system_prompt: str | None = None,
    ):
        self.client = OpenAI(base_url=base_url, api_key=api_key, timeout=12.0)
        self.model = model
        self.history = ChatHistory(system_prompt=system_prompt or CLOUD_COPROCESSOR_PROMPT)

    def stream_reply(self, user_text: str, cancel_event=None) -> Iterator[str]:
        try:
            print(f"[LLM] Sending request to NVIDIA NIM ({self.model})...")
            messages = self.history.as_openai_messages() + [{"role": "user", "content": user_text}]
            stream = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                stream=True,
                max_tokens=2048,
            )
            for chunk in stream:
                if cancel_event is not None and cancel_event.is_set():
                    print("[LLM] NVIDIA stream cancelled")
                    break
                if not chunk.choices:
                    continue
                choice = chunk.choices[0]
                delta = getattr(choice, "delta", None)
                if delta:
                    # Filter out reasoning_content so internal monologue isn't emitted
                    content = getattr(delta, "content", None)
                    if content:
                        print(f"[LLM][nvidia][token] {content!r}")
                        yield content
        except Exception as e:
            print(f"[ERROR] NVIDIA NIM request failed: {e}")
            import traceback
            traceback.print_exc()
            raise

    def generate_task(self, user_text: str, cancel_event=None) -> str:
        """Execute a complex reasoning/planning task silently in the cloud."""
        tokens: list[str] = []
        for token in self.stream_reply(user_text, cancel_event=cancel_event):
            tokens.append(token)
        return "".join(tokens).strip()

    def remember_turn(self, user_text: str, assistant_text: str) -> None:
        self.history.append_user(user_text)
        self.history.append_assistant(assistant_text)


@dataclass(slots=True)
class RoutePolicy:
    mode: str = "local"  # auto | local | nvidia
    complexity_chars: int = 180
    complexity_words: int = 35
    complexity_keywords: tuple[str, ...] = (
        "reason",
        "analyze",
        "compare",
        "design",
        "plan",
        "architecture",
        "debug",
        "refactor",
        "implement",
        "code",
        "algorithm",
        "step by step",
        "strategy",
        "long answer",
        "detailed",
        "restaurant",
        "restaurants",
        "recommend",
        "recommendations",
        "itinerary",
        "schedule",
    )


class LLMRouter:
    """Routes requests to local Ollama or NVIDIA NIM using Hierarchical Relay semantics."""

    def __init__(
        self,
        local_llm: LocalOllamaClient | None = None,
        nvidia_llm: NvidiaNimClient | None = None,
        policy: RoutePolicy | None = None,
    ):
        self.local_llm = local_llm
        self.nvidia_llm = nvidia_llm
        self.policy = policy or RoutePolicy()
        self._last_provider = "local"

    @property
    def last_provider(self) -> str:
        return self._last_provider

    def _is_complex(self, user_text: str) -> bool:
        text = user_text.strip()
        if not text:
            return False

        if len(text) >= self.policy.complexity_chars:
            return True
        if len(text.split()) >= self.policy.complexity_words:
            return True

        lower = text.lower()
        if any(keyword in lower for keyword in self.policy.complexity_keywords):
            return True

        # Treat multi-part prompts with many clauses as planning/reasoning candidates.
        if len(re.findall(r"[,;:]", text)) >= 3:
            return True

        return False

    def _choose_provider(self, user_text: str) -> str:
        mode = self.policy.mode.lower().strip()
        if mode in ("local", "nvidia"):
            if mode == "nvidia" and self.nvidia_llm is None:
                raise RuntimeError("NVIDIA mode forced but NVIDIA client is unavailable. Set NVIDIA_API_KEY.")
            if mode == "local" and self.local_llm is None:
                raise RuntimeError("Local mode forced but local LLM client is unavailable.")
            return mode

        if self.nvidia_llm is None and self.local_llm is None:
            raise RuntimeError("No LLM providers are configured.")
        if self.nvidia_llm is None and self.local_llm is not None:
            return "local"
        if self.local_llm is None and self.nvidia_llm is not None:
            return "nvidia"
        return "nvidia" if self._is_complex(user_text) else "local"

    def stream_reply(self, user_text: str, cancel_event=None) -> Iterator[str]:
        provider = self._choose_provider(user_text)
        self._last_provider = provider

        if provider == "nvidia" and self.nvidia_llm is not None:
            print("\n" + "╔" + "═" * 62 + "╗")
            print(f"║ ☁️  ACTIVE ENGINE: CLOUD NVIDIA NIM ({self.nvidia_llm.model})")
            print("╚" + "═" * 62 + "╝\n")

            # Hierarchical Edge-Cloud Relay (ADR-007):
            # 1. Cloud model solves the complex task silently in the background
            # 2. Complete result is displayed in the terminal for user inspection
            # 3. Result is relayed to local Ollama (qwen2.5:3b) which speaks a natural 1-2 sentence spoken summary
            print(f"[ROUTER] Dispatching complex query to cloud reasoning brain ({self.nvidia_llm.model})...")
            try:
                cloud_result = self.nvidia_llm.generate_task(user_text, cancel_event=cancel_event)
            except Exception as e:
                print(f"[ERROR] Cloud task failed: {e}. Falling back to local model.")
                if self.local_llm is not None:
                    yield from self.local_llm.stream_reply(user_text, cancel_event=cancel_event)
                return

            if cancel_event is not None and cancel_event.is_set():
                return

            print("\n" + "=" * 65)
            print(f"🚀 [NVIDIA NIM CLOUD TASK COMPLETED] Model: {self.nvidia_llm.model}")
            print("=" * 65)
            print(cloud_result)
            print("=" * 65 + "\n")

            # Record turn in cloud history
            self.nvidia_llm.remember_turn(user_text, cloud_result)

            if self.local_llm is not None:
                relay_prompt = (
                    f"The user requested: {user_text}\n\n"
                    f"The background cloud engine completed the task with this result:\n"
                    f"{cloud_result}\n\n"
                    "INSTRUCTION: You are Jarvis. Speak directly to the user in 1 to 2 concise, natural sentences. "
                    "Confirm that the task is completed and state the key takeaway or recommendation. "
                    "Do NOT read aloud markdown tables, bullet symbols, or code."
                )
                print("[ROUTER] Relaying cloud result to local edge model for speech synthesis...")
                yield from self.local_llm.stream_reply(relay_prompt, cancel_event=cancel_event)
                return

            yield cloud_result
            return

        local_model_name = getattr(self.local_llm, "model", "qwen2.5:3b")
        print("\n" + "╔" + "═" * 62 + "╗")
        print(f"║ 🧠 ACTIVE ENGINE: LOCAL EDGE OLLAMA ({local_model_name})")
        print("╚" + "═" * 62 + "╝\n")

        if self.local_llm is None:
            raise RuntimeError("Local provider selected but local client is not configured")
        yield from self.local_llm.stream_reply(user_text, cancel_event=cancel_event)

    def remember_turn(self, user_text: str, assistant_text: str) -> None:
        if self._last_provider == "local":
            if self.local_llm is not None:
                self.local_llm.remember_turn(user_text, assistant_text)
            if self.nvidia_llm is not None:
                self.nvidia_llm.remember_turn(user_text, assistant_text)
        else:
            # Cloud turn: nvidia_llm already remembered the full cloud result during relay.
            # Local model records the spoken summary.
            if self.local_llm is not None:
                self.local_llm.remember_turn(user_text, assistant_text)