import json
import os

from mcp.server.fastmcp import FastMCP

HERE = os.path.dirname(os.path.abspath(__file__))

with open(os.path.join(HERE, "config.json"), "r", encoding="utf-8") as handle:
    _config = json.load(handle)

_root_setting = _config["mcpServers"]["filesystem"]["root"]
ROOT = os.path.abspath(os.path.join(HERE, _root_setting))

mcp = FastMCP("filesystem")


@mcp.tool()
def list_dir(path: str) -> list:
    """List the entries in a directory."""
    target = os.path.join(ROOT, path)
    return os.listdir(target)


@mcp.tool()
def read_file(path: str) -> str:
    """Read the contents of a file."""
    target = os.path.join(ROOT, path)
    with open(target, "r", encoding="utf-8") as handle:
        return handle.read()


if __name__ == "__main__":
    mcp.run()
