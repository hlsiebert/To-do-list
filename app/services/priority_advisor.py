"""Priority advisor with OpenAI integration and safe local fallback."""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from typing import Any, Protocol
from urllib import error, request


class PriorityAdvisorProtocol(Protocol):
    """Contract for components that suggest task priority."""

    def suggest_priority(self, title: str, description: str | None) -> int:
        """Returns a priority suggestion between 1 and 5."""


@dataclass(slots=True)
class PriorityAdvisor:
    """Uses OpenAI when available and falls back to local heuristics."""

    model: str = "gpt-4.1-mini"
    timeout_seconds: float = 4.0

    def __post_init__(self) -> None:
        """Loads optional runtime overrides from environment variables."""
        self.model = os.getenv("OPENAI_MODEL", self.model)
        timeout_value = os.getenv("PRIORITY_ADVISOR_TIMEOUT_SECONDS")
        if timeout_value:
            try:
                self.timeout_seconds = float(timeout_value)
            except ValueError:
                pass

    def suggest_priority(self, title: str, description: str | None) -> int:
        """Returns a priority from 1 (low) to 5 (high)."""
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            return self._heuristic_priority(title=title, description=description)

        llm_priority = self._suggest_with_llm(
            api_key=api_key,
            title=title,
            description=description,
        )
        if llm_priority is None:
            return self._heuristic_priority(title=title, description=description)

        return llm_priority

    def _suggest_with_llm(
        self,
        api_key: str,
        title: str,
        description: str | None,
    ) -> int | None:
        """Calls OpenAI API and returns parsed priority, or None on failure."""
        prompt = (
            "Classifique a prioridade da tarefa de 1 a 5. "
            "Responda apenas com um numero inteiro entre 1 e 5.\n"
            f"Titulo: {title}\n"
            f"Descricao: {description or ''}"
        )

        payload = {
            "model": self.model,
            "input": [
                {
                    "role": "system",
                    "content": [
                        {
                            "type": "input_text",
                            "text": (
                                "Voce e um classificador de prioridade de tarefas internas. "
                                "Use 1 para baixa urgencia e 5 para alta urgencia."
                            ),
                        }
                    ],
                },
                {
                    "role": "user",
                    "content": [{"type": "input_text", "text": prompt}],
                },
            ],
            "max_output_tokens": 16,
        }

        req = request.Request(
            url="https://api.openai.com/v1/responses",
            data=json.dumps(payload).encode("utf-8"),
            method="POST",
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_key}",
            },
        )

        try:
            with request.urlopen(req, timeout=self.timeout_seconds) as response:
                body = response.read().decode("utf-8")
            parsed = json.loads(body)
            text = self._extract_text(parsed)
            return self._parse_priority(text)
        except (error.URLError, TimeoutError, OSError, json.JSONDecodeError, ValueError):
            return None

    def _extract_text(self, response_body: dict[str, Any]) -> str:
        """Extracts text output from a Responses API payload."""
        output_items = response_body.get("output", [])
        if not isinstance(output_items, list):
            raise ValueError("Invalid output format")

        chunks: list[str] = []
        for item in output_items:
            if not isinstance(item, dict):
                continue
            content = item.get("content", [])
            if not isinstance(content, list):
                continue
            for part in content:
                if not isinstance(part, dict):
                    continue
                if part.get("type") == "output_text":
                    text = part.get("text")
                    if isinstance(text, str):
                        chunks.append(text)

        if not chunks:
            raise ValueError("No text output from model")

        return " ".join(chunks)

    def _parse_priority(self, text: str) -> int:
        """Parses and clamps the first integer found in model output."""
        digits = "".join(char if char.isdigit() else " " for char in text).split()
        if not digits:
            raise ValueError("No numeric priority found")

        value = int(digits[0])
        return max(1, min(5, value))

    def _heuristic_priority(self, title: str, description: str | None) -> int:
        """Local fallback based on simple keywords and urgency hints."""
        text = f"{title} {description or ''}".lower()

        if any(word in text for word in ("urgent", "urgente", "critico", "critico", "blocker")):
            return 5
        if any(word in text for word in ("asap", "hoje", "today", "imediato", "importante")):
            return 4
        if any(word in text for word in ("amanha", "soon", "proxima semana")):
            return 3
        if any(word in text for word in ("melhoria", "improvement", "refactor", "backlog")):
            return 2
        return 3
