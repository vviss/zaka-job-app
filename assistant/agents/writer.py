from assistant.llm import complete_json, complete_text

_ANSWER_SYSTEM = (
    "You are a writing assistant. Answer the question using your knowledge and "
    "the following context. Reply with a JSON object of the form "
    '{"answer": "<a clear, complete answer>", "citations": ["<source name>", ...]}.'
)

_FORMAT_SYSTEM = "Reformat the following answer as clean markdown. Do not change the meaning."


def write(question, notes, sources):
    answer_prompt = "Question: %s\n\nContext:\n%s" % (question, notes)
    result = complete_json(_ANSWER_SYSTEM, [{"role": "user", "content": answer_prompt}])
    answer = result["answer"]

    formatted = complete_text(_FORMAT_SYSTEM, [{"role": "user", "content": answer}])

    cited = sources or result.get("citations", [])
    if cited:
        citations = "\n\nSources: " + ", ".join(cited)
    else:
        citations = ""
    return formatted + citations
