import json
import re
import time

import httpx

from app.config import Config


def call_openrouter(
    prompt: str,
    config: Config,
    model: str = None,
    system_prompt: str = "",
    temperature: float = 0.7,
    max_tokens: int = 4096,
) -> str:
    model = model or config.default_model
    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": prompt})

    payload = {
        "model": model,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
    }

    for attempt in range(3):
        try:
            response = httpx.post(
                f"{config.openrouter_base_url}/chat/completions",
                headers={
                    "Authorization": f"Bearer {config.openrouter_api_key}",
                    "Content-Type": "application/json",
                    "HTTP-Referer": "https://ai-fighting-league.local",
                    "X-Title": "AI Fighting League",
                },
                json=payload,
                timeout=120.0,
            )
            response.raise_for_status()
            data = response.json()
            return data["choices"][0]["message"]["content"]
        except (httpx.HTTPError, KeyError, IndexError) as e:
            if attempt < 2:
                time.sleep(2 ** attempt)
                continue
            raise RuntimeError(f"OpenRouter call failed after 3 attempts: {e}") from e


def call_openrouter_json(
    prompt: str,
    config: Config,
    model: str = None,
    system_prompt: str = "",
    temperature: float = 0.7,
    max_tokens: int = 4096,
) -> dict:
    for attempt in range(3):
        text = call_openrouter(
            prompt, config, model=model, system_prompt=system_prompt,
            temperature=temperature, max_tokens=max_tokens,
        )
        cleaned = _strip_markdown_fences(text)
        try:
            return json.loads(cleaned)
        except json.JSONDecodeError:
            if attempt < 2:
                prompt = prompt + "\n\nIMPORTANT: Your previous response was not valid JSON. Please respond with ONLY valid JSON, no markdown fences or extra text."
                continue
            raise RuntimeError(f"Failed to parse JSON from OpenRouter after 3 attempts. Last response: {text[:500]}")


def _strip_markdown_fences(text: str) -> str:
    text = text.strip()
    pattern = r"```(?:json)?\s*\n?(.*?)```"
    match = re.search(pattern, text, re.DOTALL)
    if match:
        return match.group(1).strip()
    if text.startswith("{") or text.startswith("["):
        return text
    lines = text.split("\n")
    json_lines = []
    in_json = False
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("{") or stripped.startswith("["):
            in_json = True
        if in_json:
            json_lines.append(line)
    if json_lines:
        return "\n".join(json_lines)
    return text
