from ddgs import DDGS

from assistant import mcp_client

TOOL_SCHEMA = [
    {
        "type": "function",
        "function": {
            "name": "execute",
            "description": (
                "Perform an action against the document system or the web. "
                "Set action to one of: list_dir, read_file, "
                "web_search. Pass the parameters for the action in "
                "args. For file actions args has a path field. For web_search "
                "args has a query field."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "action": {"type": "string"},
                    "args": {"type": "object"},
                },
                "required": ["action", "args"],
            },
        },
    }
]


# Review: using duckduckgo instead of a raw http call for the web search
def web_search(query):
    try:
        results = DDGS().text(query, max_results=5)
    except Exception:
        return ""
    return "\n".join(
        "- %s: %s (%s)" % (r["title"], r["body"], r["href"]) for r in results
    )


def run_tool(tool_input):
    action = tool_input.get("action")
    args = tool_input.get("args", {})

    if action == "list_dir":
        # Review: there's "list_dir" in the tools schema, not "list"
        return mcp_client.call_tool("list_dir", {"path": args.get("path", "")})
    if action == "read_file":
        return mcp_client.call_tool("read_file", {"path": args.get("path", "")})
    # Review: remove write_file and delete_file
    # They are destructive actions (security risk)
    # and anyway not useful for the purpose of this app
    if action == "web_search":
        # Review: clear message for the model when the search came back empty
        return web_search(args.get("query", "")) or "no web results found"
    return "unknown action"
