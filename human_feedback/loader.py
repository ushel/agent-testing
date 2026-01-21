import json
from pathlib import Path


def load_human_feedback(agent_type: str) -> dict:
    path = Path("human_feedback") / f"{agent_type}.json"
    if not path.exists():
        return {}

    with open(path) as f:
        return json.load(f)
