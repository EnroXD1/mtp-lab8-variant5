"""Проверки запроса и обработки ответа без внешней сети."""

import json
import logging

import httpx
import pytest

from lab8.liftwing import ENDPOINT, MODEL, LiftWingError, suggest_title


def test_request_and_successful_response(caplog):
    topic = "История солнечных часов"
    title = "Солнечные часы"

    def respond(request):
        assert request.method == "POST"
        assert str(request.url) == ENDPOINT
        body = json.loads(request.content)
        assert body["model"] == MODEL
        assert body["messages"][0]["role"] == "system"
        assert body["messages"][1] == {"role": "user", "content": topic}
        assert "MtpLab8" in request.headers["Api-User-Agent"]
        assert request.extensions["timeout"]["read"] == 15.0
        return httpx.Response(200, json={
            "choices": [{"message": {"content": f"  {title}  "}}],
        })

    with (
        caplog.at_level(logging.INFO, logger="lab8.liftwing"),
        httpx.Client(transport=httpx.MockTransport(respond)) as client,
    ):
        assert suggest_title(f" {topic} ", client) == title
    assert "HTTP 200" in caplog.text
    assert topic not in caplog.text
    assert title not in caplog.text


@pytest.mark.parametrize("topic", ["", "  ", "а" * 301])
def test_invalid_topic_is_rejected_before_request(topic):
    def unexpected_request(request):
        pytest.fail("Для некорректной темы HTTP-запрос не нужен.")

    with httpx.Client(
        transport=httpx.MockTransport(unexpected_request),
    ) as client:
        with pytest.raises(ValueError, match="Длина темы"):
            suggest_title(topic, client)


@pytest.mark.parametrize(("status", "expected"), [
    (429, "ограничил частоту"),
    (503, "HTTP 503"),
])
def test_service_error(status, expected):
    transport = httpx.MockTransport(lambda _: httpx.Response(status))
    with httpx.Client(transport=transport) as client:
        with pytest.raises(LiftWingError, match=expected):
            suggest_title("Тема", client)


@pytest.mark.parametrize(("error_type", "expected"), [
    (httpx.ReadTimeout, "не ответил вовремя"),
    (httpx.ConnectError, "Не удалось подключиться"),
])
def test_network_failure(error_type, expected):
    def fail(request):
        raise error_type("details", request=request)

    with httpx.Client(transport=httpx.MockTransport(fail)) as client:
        with pytest.raises(LiftWingError, match=expected):
            suggest_title("Тема", client)


@pytest.mark.parametrize("body", [
    b"not json",
    b'{"choices":[]}',
    b'{"choices":[{"message":{"content":" "}}]}',
    b'{"choices":[{"message":{"content":null}}]}',
])
def test_invalid_response(body):
    transport = httpx.MockTransport(
        lambda _: httpx.Response(200, content=body),
    )
    with httpx.Client(transport=transport) as client:
        with pytest.raises(LiftWingError, match="ответ"):
            suggest_title("Тема", client)
