import os

from config import BASE_DIR, DATA_DIR


# Review: definitely not relying on an LLM decision for granting access
# Instead, we check with code if the document path is within the team's directory
def can_access(team, doc_path):
    if not team or not doc_path:
        return False

    team_dir = os.path.realpath(os.path.join(DATA_DIR, team))
    if (
        os.path.dirname(team_dir) != os.path.realpath(DATA_DIR)
        or not os.path.isdir(team_dir)
    ):
        return False

    candidate = os.path.realpath(os.path.join(BASE_DIR, doc_path))
    return candidate == team_dir or candidate.startswith(team_dir + os.sep)
