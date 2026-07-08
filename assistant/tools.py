import httpx

from config import SEARCH_API_KEY, SEARCH_ENDPOINT
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


# Review: simple error handling for web search failure
# so that the researcher doesn't crash the app if the search request fails
# (especially now that I haven't implemented a real search service yet)
def web_search(query):
    try:
        response = httpx.post(
            SEARCH_ENDPOINT,
            headers={"Authorization": "Bearer %s" % SEARCH_API_KEY},
            json={"q": query},
            timeout=30.0,
        )
        return response.text
    except httpx.HTTPError as exc:
        return "web search failed: %s" % exc


def run_tool(tool_input):
    action = tool_input.get("action")
    args = tool_input.get("args", {})

    if action == "list":
        return mcp_client.call_tool("list_dir", {"path": args.get("path", "")})
    if action == "read_file":
        return mcp_client.call_tool("read_file", {"path": args.get("path", "")})
    # Review: remove write_file and delete_file
    # They are destructive actions (security risk)
    # and anyway not useful for the purpose of this app
    if action == "web_search":
        return web_search(args.get("query", ""))
    return "unknown action"
