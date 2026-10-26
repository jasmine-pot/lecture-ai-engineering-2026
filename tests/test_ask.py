from types import SimpleNamespace

from app import ask as ask_module


def test_ask_prints_token_usage_and_response_time(monkeypatch, capsys):
    response = SimpleNamespace(
        text="answer",
        usage_metadata=SimpleNamespace(
            prompt_token_count=12,
            candidates_token_count=7,
        ),
    )

    class FakeModels:
        def generate_content(self, **kwargs):
            return response

    class FakeClient:
        models = FakeModels()

    monkeypatch.setattr(ask_module.genai, "Client", lambda **kwargs: FakeClient())
    monkeypatch.setattr(ask_module, "get_api_key", lambda: "test-key")
    elapsed_values = iter((1.0, 3.5))
    monkeypatch.setattr(ask_module.time, "perf_counter", lambda: next(elapsed_values))

    assert ask_module.ask("question") == "answer"
    assert capsys.readouterr().out.splitlines() == [
        "[usage] input_tokens=12, output_tokens=7",
        "[response time] 2.50s",
    ]


def test_ask_sends_and_updates_conversation_history(monkeypatch):
    responses = iter(
        [
            SimpleNamespace(text="first answer", usage_metadata=None),
            SimpleNamespace(text="second answer", usage_metadata=None),
        ]
    )
    requests = []

    class FakeModels:
        def generate_content(self, **kwargs):
            requests.append(kwargs["contents"])
            return next(responses)

    class FakeClient:
        models = FakeModels()

    monkeypatch.setattr(ask_module.genai, "Client", lambda **kwargs: FakeClient())
    monkeypatch.setattr(ask_module, "get_api_key", lambda: "test-key")
    history = []

    assert ask_module.ask("first question", history) == "first answer"
    assert ask_module.ask("follow-up", history) == "second answer"

    assert [message.role for message in requests[1]] == ["user", "model", "user"]
    assert requests[1][-1].parts[0].text == "follow-up"
    assert [message.role for message in history] == ["user", "model", "user", "model"]