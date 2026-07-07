import asyncio

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

_params = StdioServerParameters(
    command="python",
    args=["mcp_servers/filesystem_server.py"],
)


async def _call(name, arguments):
    async with stdio_client(_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            result = await session.call_tool(name, arguments)
            parts = [block.text for block in result.content if block.type == "text"]
            return "".join(parts)


def call_tool(name, arguments):
    return asyncio.run(_call(name, arguments))
