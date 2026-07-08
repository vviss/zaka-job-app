import json

from assistant.llm import complete, complete_text
from assistant.retrieval import retrieve
from assistant.access import can_access
from assistant import tools

_SYSTEM = (
    "You are a research assistant for the {team} team. Use the execute tool to "
    "open the documents you need under data/{team}/ and, when it helps, to search "
    "the web to corroborate what you find. When you search the web, include the "
    "relevant details from the documents you have read so the query is well "
    "targeted. When you have enough, write down the facts relevant to the "
    "question. Be concise."
)


def _preview(chunks):
    if not chunks:
        return "(no matching documents found)"
    # Review: drop [:120] truncation per chunck because it's giving lots of false negatives
    # (the answers are sometimes in the truncated parts)
    # Not sure of this change because it costs more LLM tokens but I see better results
    # TODO Wissam: double-check this again later
    return "\n".join("- %s: %s" % (c["source"], c["text"]) for c in chunks)


def _run_tool_call(team, tool_input, used):
    action = (tool_input or {}).get("action")
    args = (tool_input or {}).get("args", {})
    # Review: add "list_dir" to the security gating
    # because it's also a "read" of the system files
    if action in ("read_file", "list_dir"):
        path = args.get("path", "")
        if not can_access(team, path):
            return "access denied"
        if action == "read_file":
            name = path.rstrip("/").split("/")[-1]
            if name and name not in used:
                used.append(name)
    result = tools.run_tool(tool_input)
    if not isinstance(result, str):
        result = json.dumps(result, default=str)
    return result


def research(team, question, steps=None):
    chunks = retrieve(team, question)
    system = _SYSTEM.format(team=team)

    # Review: include the plan (formatted as a numbered list) in the prompt
    plan = ""
    if steps:
        plan = "Plan of action:\n" + "\n".join(
            "%d. %s" % (i + 1, step) for i, step in enumerate(steps)
        ) + "\n\n"
    prompt = (
        "Question: %s\n\n%sTop matching snippets from the %s document set:\n%s\n\n"
        "Open whichever document you need and answer."
        % (question, plan, team, _preview(chunks))
    )
    messages = [{"role": "user", "content": prompt}]
    used = []

    # Review: let the researcher take a few tool rounds 
    # (ex: read a doc, then decide to read another or answer) instead of a single round
    MAX_STEPS = 4 # to avoid an infinite loop

    for _ in range(MAX_STEPS):
        response = complete(system, messages, tools=tools.TOOL_SCHEMA)
        message = response.choices[0].message
        tool_calls = message.tool_calls or []

        if not tool_calls:
            return {"notes": message.content or "", "sources": used}

        messages.append(
            {
                "role": "assistant",
                "content": message.content,
                "tool_calls": [
                    {
                        "id": call.id,
                        "type": "function",
                        "function": {"name": call.function.name, "arguments": call.function.arguments},
                    }
                    for call in tool_calls
                ],
            }
        )
        for call in tool_calls:
            try:
                tool_input = json.loads(call.function.arguments or "{}")
            except json.JSONDecodeError:
                tool_input = {}
            output = _run_tool_call(team, tool_input, used)
            messages.append({"role": "tool", "tool_call_id": call.id, "content": output})

    notes = complete_text(system, messages)
    return {"notes": notes, "sources": used}
