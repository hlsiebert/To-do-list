from __future__ import annotations

import json
from urllib import error

from app.services.priority_advisor import PriorityAdvisor


class FakeHTTPResponse:
    """Minimal HTTP response stub for urlopen mocks."""

    def __init__(self, payload: dict) -> None:
        self._payload = payload

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        return None

    def read(self) -> bytes:
        return json.dumps(self._payload).encode("utf-8")


def test_should_return_highest_priority_for_urgent_keywords() -> None:
    advisor = PriorityAdvisor()

    priority = advisor.suggest_priority(
        title="Corrigir bug urgente",
        description="Issue critico bloqueando deploy",
    )

    assert priority == 5


def test_should_return_high_priority_for_today_or_asap_keywords(monkeypatch) -> None:
    advisor = PriorityAdvisor()

    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    priority = advisor.suggest_priority(
        title="Enviar relatorio hoje",
        description="Precisa ser concluido asap",
    )

    assert priority == 4


def test_should_return_low_priority_for_backlog_or_improvement_keywords() -> None:
    advisor = PriorityAdvisor()

    priority = advisor.suggest_priority(
        title="Melhoria de layout",
        description="Item de backlog para improvement futuro",
    )

    assert priority == 2


def test_should_fallback_to_heuristic_when_external_call_fails(monkeypatch) -> None:
    advisor = PriorityAdvisor()

    monkeypatch.setenv("OPENAI_API_KEY", "fake-key")

    def fail_urlopen(*args, **kwargs):
        raise error.URLError("network error")

    monkeypatch.setattr("app.services.priority_advisor.request.urlopen", fail_urlopen)

    priority = advisor.suggest_priority(
        title="Tarefa urgente",
        description="bloqueia operacao",
    )

    assert priority == 5


def test_should_fallback_to_heuristic_when_llm_times_out(monkeypatch) -> None:
    advisor = PriorityAdvisor()

    monkeypatch.setenv("OPENAI_API_KEY", "fake-key")

    def timeout_urlopen(*args, **kwargs):
        raise TimeoutError("request timeout")

    monkeypatch.setattr("app.services.priority_advisor.request.urlopen", timeout_urlopen)

    priority = advisor.suggest_priority(
        title="Entrega importante hoje",
        description="",
    )

    assert priority == 4


def test_should_fallback_to_heuristic_when_llm_response_is_unparseable(monkeypatch) -> None:
    advisor = PriorityAdvisor()

    monkeypatch.setenv("OPENAI_API_KEY", "fake-key")

    invalid_payload = {
        "output": [{"content": [{"type": "output_text", "text": "sem numero"}]}]
    }

    def unparseable_urlopen(*args, **kwargs):
        return FakeHTTPResponse(invalid_payload)

    monkeypatch.setattr("app.services.priority_advisor.request.urlopen", unparseable_urlopen)

    priority = advisor.suggest_priority(
        title="Refactor backlog",
        description="melhoria tecnica",
    )

    assert priority == 2
