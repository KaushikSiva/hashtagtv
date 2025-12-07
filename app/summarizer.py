\"\"\"Generate broadcast-style scripts from aggregated news items.\"\"\"
import re
from typing import List

from .config import GROK_API_KEY
from .grok_client import ask_grok


def _sanitize_item(text: str) -> str:
    text = text or \"\"
    text = re.sub(r\"(#|@)[\\w_]+\", \"\", text)
    text = re.sub(r\"https?://\\S+\", \"\", text)
    text = re.sub(r\"[^\\x00-\\x7F]+\", \"\", text)
    return \" \".join(text.split())


def _build_prompt(query: str, items: List[str]) -> str:
    cleaned = \"\\n\".join(filter(None, (_sanitize_item(item) for item in items))) or \"No updates available.\"
    return (
        \"You are a neutral broadcast news anchor delivering a 60 to 80 second script. \"
        \"Do not mention 'according to Twitter'. Present the key developments in a calm tone and finish with "
        \"'More updates as the story develops.'\\n\\n\"
        f\"Facts from recent reports about {query}:\\n\" + cleaned + \"\\n\\nScript:\"
    )


def generate_news_script_from_items(query: str, items: List[str]) -> str:
    if not GROK_API_KEY:
        return \"GROK API key not configured. Unable to generate script.\"

    prompt = _build_prompt(query, items)
    script = ask_grok(prompt)
    if not script:
        return \"Unable to generate script: GROK request failed or key missing.\"

    if not script.endswith(\"More updates as the story develops.\"):
        script = script.rstrip(\".\") + \". More updates as the story develops.\"
    return script
