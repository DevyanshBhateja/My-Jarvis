"""Parse ACTION directives emitted by the LLM."""

from __future__ import annotations

from dataclasses import dataclass
import ast
from typing import Any


@dataclass(slots=True)
class ActionRequest:
    name: str
    args: list[Any]
    kwargs: dict[str, Any]
    raw: str
    utterance_id: str = ""
    done_event: Any = None


def _literal(node: ast.AST) -> Any:
    return ast.literal_eval(node)


def parse_action_from_llm(text: str) -> ActionRequest | None:
    if not text:
        return None

    for line in text.splitlines():
        stripped = line.strip()
        if not stripped.startswith("ACTION:"):
            continue
        payload = stripped[len("ACTION:"):].strip()
        if not payload:
            return None
        try:
            expr = ast.parse(payload, mode="eval")
        except SyntaxError:
            return None
        if not isinstance(expr.body, ast.Call):
            return None
        call = expr.body
        if isinstance(call.func, ast.Name):
            name = call.func.id
        else:
            return None

        try:
            args = [_literal(arg) for arg in call.args]
            kwargs = {kw.arg: _literal(kw.value) for kw in call.keywords if kw.arg}
        except Exception:
            return None

        return ActionRequest(name=name, args=args, kwargs=kwargs, raw=stripped)

    return None