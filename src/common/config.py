import os
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI
import json

load_dotenv()
ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / "data/raw"
PROCESSED = ROOT / "data/processed"
GOLD = ROOT / "data/gold"
TEMPLATES = ROOT / "templates"
EXPERIMENTS = ROOT / "experiments"

CHAT_MODEL = os.environ["AZURE_OPENAI_CHAT_DEPLOYMENT"]
EMBED_MODEL = os.environ["AZURE_OPENAI_EMBED_DEPLOYMENT"]
SEARCH_ENDPOINT = os.getenv("AZURE_SEARCH_ENDPOINT")
SEARCH_KEY = os.getenv("AZURE_SEARCH_API_KEY")
SEARCH_INDEX = os.getenv("AZURE_SEARCH_INDEX", "testplan-knowledge")


def llm():
    endpoint = os.environ["AZURE_OPENAI_ENDPOINT"].rstrip("/")
    return OpenAI(api_key=os.environ["AZURE_OPENAI_API_KEY"], base_url=f"{endpoint}/openai/v1/")


def ask(system: str, content, effort: str = "low") -> str:
    """Call gpt-5-mini. content = text, or a list of input parts (text + images)."""
    if isinstance(content, str):
        content = [{"type": "input_text", "text": content}]
    resp = llm().responses.create(
        model=CHAT_MODEL,
        instructions=system,
        input=[{"role": "user", "content": content}],
        reasoning={"effort": effort},
    )
    return resp.output_text.strip()

def ask_json(system: str, user_text: str, schema: dict, name: str, effort: str = "medium") -> dict:
    """Same as ask(), but the model MUST return JSON matching `schema` (structured outputs)."""
    resp = llm().responses.create(
        model=CHAT_MODEL, instructions=system,
        input=[{"role": "user", "content": [{"type": "input_text", "text": user_text}]}],
        reasoning={"effort": effort},
        text={"format": {"type": "json_schema", "name": name, "schema": schema, "strict": True}},
    )
    return json.loads(resp.output_text)

def embed(texts: list[str]) -> list[list[float]]:
    resp = llm().embeddings.create(model=EMBED_MODEL, input=texts)
    return [d.embedding for d in resp.data]