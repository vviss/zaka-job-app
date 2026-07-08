import os
import re

from config import DATA_DIR, CHUNK_SIZE


def _read(path):
    with open(path, "r", encoding="utf-8") as handle:
        return handle.read()


def _normalize(text):
    return re.sub(r"\s+", " ", text).strip()


def _split(text):
    # Review: group whole paragraphs (split on blank lines) into chunks up to
    # CHUNK_SIZE instead of slicing every 500 chars, so we don't cut mid-sentence
    chunks = []
    current = ""
    prev = ""
    for paragraph in re.split(r"\n\s*\n", text):
        paragraph = _normalize(paragraph)

        if not paragraph:
            continue
        if current and len(current) + len(paragraph) > CHUNK_SIZE:
            chunks.append(current)
            current = prev
            # Review: adding the previous paragraph as overlap to the next chunk
            # It may be overkill for the current dataset but it gave better results
        current = (current + " " + paragraph).strip()
        prev = paragraph
    if current:
        chunks.append(current)
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
        # Review: removed _normalize() from here, doing it inside _split() now
        for piece in _split(raw):
            chunks.append({"source": name, "text": piece})
    return chunks
