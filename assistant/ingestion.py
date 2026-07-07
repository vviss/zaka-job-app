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


def get_available_teams():
    return sorted(
        name for name in os.listdir(DATA_DIR)
        if os.path.isdir(os.path.join(DATA_DIR, name))
    )


def _resolve_team_dir(team):
    # Review: validate the team is a valid directory
    # and filter out injections in team names (ex: acme/../../root)
    team_dir = os.path.realpath(os.path.join(DATA_DIR, team))
    if (
        os.path.dirname(team_dir) != os.path.realpath(DATA_DIR)
        or not os.path.isdir(team_dir)
    ):
        raise ValueError(
            "Unknown team %r. Available teams: %s"
            % (team, ", ".join(get_available_teams()))
        )
    return team_dir


def load_team_chunks(team):
    team_dir = _resolve_team_dir(team)
    chunks = []
    for name in sorted(os.listdir(team_dir)):
        if not name.endswith((".md", ".txt")):
            continue
        raw = _read(os.path.join(team_dir, name))
        normalized = _normalize(raw)
        for piece in _split(normalized):
            chunks.append({"source": name, "text": piece})
    return chunks
