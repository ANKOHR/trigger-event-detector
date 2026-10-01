"""Synthetic fixtures with independently specified planted expectations. No randomness."""
import json
from pathlib import Path

AS_OF = "2026-09-30"

def fixture_data():
    records = []
    for i in range(200):
        kind = ("funding", "hiring", "launch", "partnership")[i % 4]
        record = {"id": f"event-{i:03}", "company": f"Synthetic Company {i:03}", "kind": kind, "date": "2026-09-20" if i < 100 else "2026-07-01", "verified": i < 50 or i >= 100, "source": f"synthetic://evidence/{i}", "synthetic": True}
        if kind == "funding":
            record.update(amount="1000.25", currency="GBP")
        if kind == "hiring":
            record["roles"] = 3
        records.append(record)
    return {"_comment": "SYNTHETIC fixture, not real outreach evidence", "synthetic": True, "as_of": AS_OF, "records": records}

def expectations():
    # IDs 0..49 qualify; 50..99 are unverified; 100..199 are stale.
    # 13 funding and 13 hiring records, 12 launches and 12 partnerships.
    # 13 * 1000.25 = 13003.25 GBP; 13 * 3 = 39 roles.
    return {"_comment": "SYNTHETIC hand-computed expectations", "synthetic": True, "input_count": 200, "event_count": 50, "by_kind": {"funding": 13, "hiring": 13, "launch": 12, "partnership": 12}, "funding_totals": {"GBP": "13003.25"}, "reported_roles": 39, "event_ids": [f"event-{i:03}" for i in range(50)]}

def generate(out):
    out = Path(out)
    out.mkdir(parents=True, exist_ok=True)
    for name, value in (("events.json", fixture_data()), ("expectations.json", expectations())):
        (out / name).write_text(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
