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
                "Set action to one of: list_dir, read_file, write_file, "
                "delete_file, web_search. Pass the parameters for the action in "
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


def web_search(query):
    response = httpx.post(
        SEARCH_ENDPOINT,
        headers={"Authorization": "Bearer %s" % SEARCH_API_KEY},
        json={"q": query},
        timeout=30.0,
    )
    return response.text


def run_tool(tool_input):
    action = tool_input.get("action")
    args = tool_input.get("args", {})

    if action == "list":
        return mcp_client.call_tool("list_dir", {"path": args.get("path", "")})
    if action == "read_file":
        return mcp_client.call_tool("read_file", {"path": args.get("path", "")})
    if action == "write_file":
        return mcp_client.call_tool(
            "write_file", {"path": args.get("path", ""), "content": args.get("content", "")}
        )
    if action == "delete_file":
        return mcp_client.call_tool("delete_file", {"path": args.get("path", "")})
    if action == "web_search":
        return web_search(args.get("query", ""))
    return "unknown action"
