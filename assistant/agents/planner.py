from assistant.llm import complete_text

_SYSTEM = "You are a helpful planning assistant. Do your best to help the user."


def make_plan(question):
    prompt = (
        "A user asked the following question. Write a short numbered plan for "
        "how to answer it.\n\nQuestion: %s" % question
    )
    return complete_text(_SYSTEM, [{"role": "user", "content": prompt}])
