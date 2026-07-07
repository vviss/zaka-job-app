import re

from assistant.ingestion import load_team_chunks

TOP_K = 4

_STOPWORDS = {
    "the", "a", "an", "is", "are", "was", "were", "be", "been", "for", "of",
    "to", "in", "on", "and", "or", "what", "how", "which", "who", "does", "do",
    "did", "this", "that", "with", "at", "by", "from", "as", "it", "its", "we",
    "our", "you", "your", "can", "should", "will", "would", "there", "here",
}


def _terms(text):
    words = re.findall(r"[a-z0-9]+", text.lower())
    return set(word for word in words if word not in _STOPWORDS)


def _score(query_terms, chunk_text):
    return len(query_terms & _terms(chunk_text))


def retrieve(team, question):
    chunks = load_team_chunks(team)
    query_terms = _terms(question)
    scored = [(chunk, _score(query_terms, chunk["text"])) for chunk in chunks]
    scored = [pair for pair in scored if pair[1] > 0]
    scored.sort(key=lambda pair: pair[1], reverse=True)
    return [chunk for chunk, _ in scored[:TOP_K]]
