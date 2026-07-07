import os

from dotenv import load_dotenv

load_dotenv()

# Model-agnostic: point LLM_BASE_URL at any OpenAI-compatible endpoint
# (OpenAI, a local server, or a gateway) and set MODEL to a name it serves.
LLM_API_KEY = os.environ.get("LLM_API_KEY", "")
LLM_BASE_URL = os.environ.get("LLM_BASE_URL", "https://api.openai.com/v1")
MODEL = os.environ.get("MODEL", "gpt-4o")

SEARCH_API_KEY = os.environ.get("SEARCH_API_KEY", "")

MAX_TOKENS = 1024

# Review: default to INFO, not DEBUG, so request payloads aren't dumped to logs
LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")

CHUNK_SIZE = 500

SEARCH_ENDPOINT = "https://api.search-provider.example/v1/search"
