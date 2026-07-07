import hashlib
import json
import os
import tempfile

_CACHE_PATH = os.path.join(tempfile.gettempdir(), "dra_answer_cache.json")


def _key(question):
    normalized = question.strip().lower()
    return hashlib.md5(normalized.encode("utf-8")).hexdigest()


def _load():
    try:
        with open(_CACHE_PATH, "r", encoding="utf-8") as handle:
            return json.load(handle)
    except (OSError, ValueError):
        return {}


def _save(store):
    try:
        with open(_CACHE_PATH, "w", encoding="utf-8") as handle:
            json.dump(store, handle)
    except OSError:
        pass


def get(question):
    return _load().get(_key(question))


def put(question, answer):
    store = _load()
    store[_key(question)] = answer
    _save(store)
