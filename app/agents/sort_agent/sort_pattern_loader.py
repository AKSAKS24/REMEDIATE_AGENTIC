import json
from typing import List, Dict, Any


def load_rag_patterns(path: str) -> List[Dict[str, Any]]:    
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, list):
        raise ValueError("RAG patterns file must contain a JSON array.")
    for i, item in enumerate(data):
        if "id" not in item or "pattern" not in item:
            raise ValueError(f"RAG item at index {i} must include 'id' and 'pattern'.")
        item.setdefault("type", "regex")
        item.setdefault("description", "")
        item.setdefault("case_sensitive", False)
        item.setdefault("suggested_replacement", "")
    return data