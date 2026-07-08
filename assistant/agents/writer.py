from assistant.llm import complete_text

# Review: 
# - only answer from the company data so the model doesn't make things up
# - removed citations (we have deterministic 'sources', plus the model itself won't know the sources)
# - asking directly for a markdown answer saves time and tokens instead of making a second LLM call
_ANSWER_SYSTEM = (
    "You are a writing assistant. Answer the question using only the provided "
    "context. If the context doesn't cover it, say you don't know. Write a "
    "clear, complete answer in markdown."
)


def write(question, notes, sources):
    answer_prompt = "Question: %s\n\nContext:\n%s" % (question, notes)
    answer = complete_text(_ANSWER_SYSTEM, [{"role": "user", "content": answer_prompt}])

    if sources:
        return answer + "\n\nSources: " + ", ".join(sources)
    return answer
