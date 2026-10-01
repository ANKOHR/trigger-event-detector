"""Deterministic reports with explicit provenance and unmeasured-benefit labels."""
import json

def provenance(result):
    return (f"DATA PROVENANCE: {result['synthetic_records']} synthetic fixture records; "
            f"{result['real_records']} real records declared by the input author. "
            "Real declarations are not independently verified. Input files: " + ", ".join(result.get("input_files", [])))

def render(result, fmt="md"):
    banner = provenance(result)
    if fmt == "json":
        return (json.dumps({"provenance_banner": banner, **result}, ensure_ascii=False, sort_keys=True, indent=2) + "\n").replace(chr(0x2014), "\\u2014")
    rows = ["# Trigger Event Detector", "", banner, "", f"As of: {result['as_of']}; inclusive window: {result['window_days']} days.", f"Input records: {result['input_count']}", f"Detected events: {result['event_count']}", "", "Counts: " + ", ".join(f"{k}: {v}" for k, v in result["by_kind"].items()), "Recorded funding totals: " + (", ".join(f"{k} {v}" for k, v in result["funding_totals"].items()) or "none"), f"Recorded hiring roles: {result['reported_roles']}", "", result["benefits"], "", "## Recorded evidence", ""]
    for r in result["events"]:
        # JSON escaping keeps arbitrary text from becoming Markdown instructions.
        rows.append("- " + json.dumps(r, ensure_ascii=False, sort_keys=True))
    return ("\n".join(rows) + "\n").replace(chr(0x2014), "\\u2014")
