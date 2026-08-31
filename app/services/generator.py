from dataclasses import dataclass
from typing import Any

import httpx

from app.config import Settings, get_settings
from app.services.prompt_builder import BuiltPrompt

GROQ_CHAT_URL = "https://api.groq.com/openai/v1/chat/completions"
OPENAI_CHAT_URL = "https://api.openai.com/v1/chat/completions"

PLATFORM_MAX_TOKENS = {
    "linkedin": 900,
    "x": 220,
    "instagram": 700,
    "threads": 450,
}

SESSION_KEY = "generation"
SESSION_ERROR_KEY = "generation_error"


class GeneratorError(RuntimeError):
    """Raised when the LLM provider cannot return usable copy."""


@dataclass(frozen=True, slots=True)
class GenerationResult:
    content: str
    provider: str
    model: str
    platform: str
    topic: str

    def to_dict(self) -> dict[str, str]:
        return {
            "content": self.content,
            "provider": self.provider,
            "model": self.model,
            "platform": self.platform,
            "topic": self.topic,
        }


def save_generation(session: dict[str, Any], result: GenerationResult) -> None:
    session[SESSION_KEY] = result.to_dict()
    session.pop(SESSION_ERROR_KEY, None)


def get_generation(session: dict[str, Any]) -> GenerationResult | None:
    raw = session.get(SESSION_KEY)
    if not isinstance(raw, dict):
        return None
    try:
        return GenerationResult(
            content=str(raw.get("content", "")),
            provider=str(raw.get("provider", "")),
            model=str(raw.get("model", "")),
            platform=str(raw.get("platform", "")),
            topic=str(raw.get("topic", "")),
        )
    except Exception:
        return None


def set_generation_error(session: dict[str, Any], message: str) -> None:
    session[SESSION_ERROR_KEY] = message


def pop_generation_error(session: dict[str, Any]) -> str:
    message = session.pop(SESSION_ERROR_KEY, "")
    return str(message) if message else ""


def generate_post(
    prompt: BuiltPrompt,
    *,
    settings: Settings | None = None,
    client: httpx.Client | None = None,
) -> GenerationResult:
    if not prompt.ready:
        raise GeneratorError("Prompt is not ready. Capture a topic and save a brand voice first.")

    config = settings or get_settings()
    provider, api_key, model, url = _provider_config(config)
    owns_client = client is None
    http = client or httpx.Client(timeout=config.llm_timeout_seconds)
    payload = {
        "model": model,
        "messages": prompt.as_messages(),
        "temperature": config.llm_temperature,
        "max_tokens": PLATFORM_MAX_TOKENS.get(prompt.platform, 700),
    }

    try:
        response = http.post(
            url,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            json=payload,
        )
    except httpx.TimeoutException as exc:
        raise GeneratorError("The language model timed out. Try again in a moment.") from exc
    except httpx.HTTPError as exc:
        raise GeneratorError("Could not reach the language model provider.") from exc
    finally:
        if owns_client:
            http.close()

    content = _parse_completion(response)
    return GenerationResult(
        content=content,
        provider=provider,
        model=model,
        platform=prompt.platform,
        topic=prompt.topic,
    )


def _provider_config(settings: Settings) -> tuple[str, str, str, str]:
    provider = settings.active_provider
    if provider == "openai":
        if not settings.openai_configured:
            raise GeneratorError(settings.llm_setup_message)
        return provider, settings.openai_api_key.strip(), settings.openai_model, OPENAI_CHAT_URL
    if not settings.groq_configured:
        raise GeneratorError(settings.llm_setup_message)
    return provider, settings.groq_api_key.strip(), settings.groq_model, GROQ_CHAT_URL


def _parse_completion(response: httpx.Response) -> str:
    if response.status_code in {401, 403}:
        raise GeneratorError("The language model API key was rejected. Check .env and try again.")
    if response.status_code == 429:
        raise GeneratorError("The language model rate limit was reached. Wait a moment and try again.")
    if response.status_code >= 500:
        raise GeneratorError("The language model provider is unavailable. Try again shortly.")
    if response.status_code >= 400:
        raise GeneratorError("The language model could not complete this request.")

    try:
        data = response.json()
        content = data["choices"][0]["message"]["content"]
    except (ValueError, KeyError, IndexError, TypeError) as exc:
        raise GeneratorError("The language model returned an unexpected response.") from exc

    text = str(content).strip()
    if not text:
        raise GeneratorError("The language model returned empty copy.")
    return text
