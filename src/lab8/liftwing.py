"""Подбор заголовка через открытую языковую модель Wikimedia."""

import logging

import httpx

MODEL = "llm-qwen3-14b"
ENDPOINT = (
    f"https://api.wikimedia.org/service/lw/inference/v1/models/{MODEL}"
    "/openai/v1/chat/completions"
)
USER_AGENT = "MtpLab8/1.0 (https://github.com/EnroXD1/mtp-lab8-variant5)"
MAX_TOPIC_LENGTH = 300
TIMEOUT_SECONDS = 15.0
SYSTEM_PROMPT = (
    "Предложи один короткий нейтральный заголовок черновика статьи "
    "для Википедии на языке темы. Выведи только заголовок, без пояснений."
)
logger = logging.getLogger(__name__)


class LiftWingError(Exception):
    """Не удалось получить заголовок от Lift Wing."""


def suggest_title(topic: str, client: httpx.Client) -> str:
    """Отправить тему модели и вернуть заголовок из ответа."""
    topic = topic.strip()
    if not 1 <= len(topic) <= MAX_TOPIC_LENGTH:
        raise ValueError(f"Длина темы должна быть от 1 до {MAX_TOPIC_LENGTH}.")

    logger.info("Запрос к Wikimedia Lift Wing, модель %s", MODEL)
    try:
        response = client.post(
            ENDPOINT,
            headers={"User-Agent": USER_AGENT, "Api-User-Agent": USER_AGENT},
            json={
                "model": MODEL,
                "messages": [
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": topic},
                ],
                "max_tokens": 96,
                "temperature": 0.2,
            },
            timeout=TIMEOUT_SECONDS,
        )
        response.raise_for_status()
    except httpx.TimeoutException:
        raise LiftWingError("Lift Wing не ответил вовремя.") from None
    except httpx.RequestError:
        raise LiftWingError("Не удалось подключиться к Lift Wing.") from None
    except httpx.HTTPStatusError as error:
        status = error.response.status_code
        if status == 429:
            raise LiftWingError(
                "Lift Wing ограничил частоту запросов. Повтори позже."
            ) from None
        raise LiftWingError(f"Lift Wing вернул HTTP {status}.") from None

    try:
        title = response.json()["choices"][0]["message"]["content"]
    except (ValueError, TypeError, KeyError, IndexError):
        raise LiftWingError("Не удалось прочитать ответ Lift Wing.") from None
    if not isinstance(title, str) or not title.strip():
        raise LiftWingError("Lift Wing вернул пустой или нетекстовый ответ.")

    logger.info("Получен ответ Lift Wing (HTTP %d)", response.status_code)
    return title.strip()
