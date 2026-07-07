from assistant.llm import complete_text

_SYSTEM = (
    "You decide whether a team is allowed to open a document in a shared "
    "document system. Teams should only open documents that belong to them. "
    "Answer with a single word, either ALLOW or DENY."
)


def can_access(team, doc_path):
    prompt = "Team: %s\nDocument path: %s\nShould this team be allowed to open it?" % (
        team,
        doc_path,
    )
    verdict = complete_text(_SYSTEM, [{"role": "user", "content": prompt}])
    return "ALLOW" in verdict.upper()
