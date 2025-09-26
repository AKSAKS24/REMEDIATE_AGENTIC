import re
from typing import List, Dict, Any
from datetime import date


def compile_regex(pattern: str, case_sensitive: bool):
    flags = re.MULTILINE | re.DOTALL
    if not case_sensitive:
        flags |= re.IGNORECASE
    return re.compile(pattern, flags)


def scan_code_for_patterns(code: str, patterns: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    findings = []
    for p in patterns:
        ptype = p.get("type", "regex")
        pattern_text = p["pattern"]
        case_sensitive = p.get("case_sensitive", False)
        if ptype == "literal":
            rx = compile_regex(re.escape(pattern_text), case_sensitive)
        else:
            rx = compile_regex(pattern_text, case_sensitive)

        matches = list(rx.finditer(code or ""))
        if not matches:
            continue

        occurrences = []
        for m in matches:
            start, end = m.span()
            occurrences.append({
                "match_text": m.group(0),
                "start": start,
                "end": end,
                "line": code.count("\n", 0, start) + 1
            })

        findings.append({
            "id": p.get("id"),
            "description": p.get("description", ""),
            "pattern": pattern_text,
            "type": ptype,
            "case_sensitive": case_sensitive,
            "suggested_replacement": p.get("suggested_replacement", ""),
            "occurrences": occurrences
        })        
    return findings


def add_pwc_tag(code: str) -> str:
    tag = f"* Added By Pwc {date.today().strftime('%Y-%m-%d')}"
    if tag in code:
        return code
    if code:
        return f"{tag}\n{code}"
    return tag