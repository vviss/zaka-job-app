import json

from openai import OpenAI, APIStatusError

from config import LLM_API_KEY, LLM_BASE_URL, MODEL, MAX_TOKENS
from assistant.logging_util import log_request, log_error

_client = OpenAI(api_key=LLM_API_KEY, base_url=LLM_BASE_URL)


def complete(system, messages, tools=None):
    full_messages = [{"role": "system", "content": system}] + messages

    # Review: don't include the API key in the payload
    # because it's a security risk to output it in the logs
    # and the chat completion API does not use it anyway (already included in the client)
    # Plus the objects 'payload' and 'kwargs' are almost duplicates

    kwargs = {
        "model": MODEL,
        "max_tokens": MAX_TOKENS,
        "messages": full_messages,
    }
    if tools:
        kwargs["tools"] = tools

    log_request("llm", kwargs)

    while True:
        try:
            return _client.chat.completions.create(**kwargs)
        except APIStatusError as exc:
            log_error("model call failed, retrying: %s" % exc)
            continue


def complete_text(system, messages):
    response = complete(system, messages)
    return response.choices[0].message.content or ""


def complete_json(system, messages):
    # The model occasionally wraps JSON in prose. This guard keeps the
    # downstream parse stable by retrying until the payload is valid.
    while True:
        text = complete_text(system, messages)
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            continue
