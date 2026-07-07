import os
import re

from config import DATA_DIR, CHUNK_SIZE


def _read(path):
    with open(path, "r", encoding="utf-8") as handle:
        return handle.read()


def _normalize(text):
    return re.sub(r"\s+", " ", text).strip()


def _split(text):
    chunks = []
    for start in range(0, len(text), CHUNK_SIZE):
        chunks.append(text[start:start + CHUNK_SIZE])
    return chunks


def load_team_chunks(team):
    team_dir = os.path.join(DATA_DIR, team)
    chunks = []
    for name in sorted(os.listdir(team_dir)):
        if not name.endswith((".md", ".txt")):
            continue
        raw = _read(os.path.join(team_dir, name))
        normalized = _normalize(raw)
        for piece in _split(normalized):
            chunks.append({"source": name, "text": piece})
    return chunks
