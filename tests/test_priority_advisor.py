from __future__ import annotations

from urllib import error

from app.services.priority_advisor import PriorityAdvisor


def test_should_return_highest_priority_for_urgent_keywords() -> None:
    advisor = PriorityAdvisor()

    priority = advisor.suggest_priority(
        title="Corrigir bug urgente",
        description="Issue critico bloqueando deploy",
    )

    assert priority == 5


def test_should_return_high_priority_for_today_or_asap_keywords() -> None:
    advisor = PriorityAdvisor()

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

    def fail_llm_call(*args, **kwargs):
        raise error.URLError("network error")

    monkeypatch.setattr(advisor, "_suggest_with_llm", fail_llm_call)

    priority = advisor.suggest_priority(
        title="Tarefa urgente",
        description="bloqueia operacao",
    )

    assert priority == 5
