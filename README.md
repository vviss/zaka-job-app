# Document Research Assistant

An internal assistant that answers natural-language questions over a team's document set. Several teams share one deployment. A user submits a question along with their team id, the system retrieves from that team's documents, and returns a written answer with citations.

The pipeline uses three agents run in sequence (planner, researcher, writer). Document access goes through a filesystem MCP server. Questions that reach outside the document set can use a web search tool.

## Status

This code runs, but it contains mistakes and is not optimized. It was put together quickly and has not been hardened.

Your job:

- Make it return good results.
- Optimize its performance where you can.
- Find any security risks.

When you are done, include a short markdown file describing the mistakes you found and the changes you made to improve it, each with a quick explanation.

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# put your API keys in .env
```

## Run

```bash
python main.py --team acme --question "Summarize the Q3 planning document."
```

## Layout

```
main.py                     CLI entrypoint
config.py                   configuration
assistant/
  orchestrator.py           runs planner -> researcher -> writer
  agents/                    the three agents
  tools.py                   tool dispatch
  mcp_client.py              filesystem MCP client
  ingestion.py               document ingestion and chunking
  retrieval.py               chunk retrieval
  cache.py                   answer cache
  access.py                  document access control
  llm.py                     model client
  logging_util.py            logging helper
mcp_servers/
  filesystem_server.py       filesystem MCP server
  config.json                MCP server configuration
data/                        per-team documents
```

## Submitting

To submit your assignment, clone this repository and complete the tasks above (include a clear markdown file describing your changes and the reasoning behind them). Push your work to your own private repository, with your name visible, and add sary-mallak1 as a collaborator so it can be reviewed. Then send a short video (max 5 minutes) explaining the changes you made to recruitment@zaka.ai.
