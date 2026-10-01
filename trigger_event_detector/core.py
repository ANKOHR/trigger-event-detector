"""Pure validation and detection. No prediction or estimated benefits."""
from datetime import date
from decimal import Decimal

KINDS = ("funding", "hiring", "launch", "partnership")

class InputError(ValueError):
    """Named input failure."""

def validate_record(record, as_of):
    required = {"id", "company", "kind", "date", "verified", "source", "synthetic"}
    allowed = required | {"amount", "currency", "roles", "detail"}
    if not isinstance(record, dict):
        raise InputError("SchemaError: record must be an object")
    for field in sorted(required - record.keys()):
        raise InputError(f"SchemaError: missing field {field}")
    for field in sorted(record.keys() - allowed):
        raise InputError(f"SchemaError: unknown field {field}")
    for field in ("id", "company", "source"):
        value = record[field]
        if not isinstance(value, str) or not value.strip() or len(value) > 10000:
            raise InputError(f"SchemaError: {field} must be nonempty text of at most 10000 characters")
    if not isinstance(record["kind"], str) or record["kind"] not in KINDS:
        raise InputError("SchemaError: kind must be funding, hiring, launch or partnership")
    for field in ("synthetic", "verified"):
        if type(record[field]) is not bool:
            raise InputError(f"SchemaError: {field} must be boolean")
    try:
        event_date = date.fromisoformat(record["date"])
    except (ValueError, TypeError):
        raise InputError("SchemaError: date must be YYYY-MM-DD") from None
    if event_date > as_of:
        raise InputError("SchemaError: date is in the future relative to as_of")
    if "detail" in record and (not isinstance(record["detail"], str) or len(record["detail"]) > 10000):
        raise InputError("SchemaError: detail must be text of at most 10000 characters")
    if "amount" in record:
        value = record["amount"]
        if not isinstance(value, str):
            raise InputError("SchemaError: amount must be a decimal string")
        try:
            amount = Decimal(value)
        except Exception:
            raise InputError("SchemaError: amount must be a decimal string") from None
        if not amount.is_finite() or amount < 0 or amount > Decimal("1000000000000000") or amount.as_tuple().exponent < -2:
            raise InputError("SchemaError: amount must be finite, nonnegative, at most 10^15 with at most two decimal places")
        if record["kind"] != "funding" or not isinstance(record.get("currency"), str) or len(record["currency"]) != 3 or not record["currency"].isascii() or not record["currency"].isupper() or not record["currency"].isalpha():
            raise InputError("SchemaError: amount requires funding kind and three-letter currency")
    elif "currency" in record:
        raise InputError("SchemaError: currency requires amount")
    if "roles" in record and (record["kind"] != "hiring" or type(record["roles"]) is not int or not 0 <= record["roles"] <= 1000000):
        raise InputError("SchemaError: roles must be a hiring count from 0 to 1000000")
    return dict(record)

def detect(records, as_of, window_days=30):
    """Return verified events aged 0 through window_days inclusive."""
    if type(window_days) is not int or not 0 <= window_days <= 3650:
        raise InputError("SchemaError: window_days must be from 0 to 3650")
    checked, seen = [], set()
    for record in records:
        item = validate_record(record, as_of)
        if item["id"] in seen:
            raise InputError(f"SchemaError: duplicate id {item['id']}")
        seen.add(item["id"])
        checked.append(item)
    events = sorted((r for r in checked if r["verified"] and (as_of - date.fromisoformat(r["date"])).days <= window_days), key=lambda r: r["id"])
    amounts = {}
    for r in events:
        if "amount" in r:
            c = r["currency"]
            amounts[c] = amounts.get(c, Decimal(0)) + Decimal(r["amount"])
    return {"as_of": as_of.isoformat(), "window_days": window_days, "input_count": len(checked), "event_count": len(events), "by_kind": {k: sum(r["kind"] == k for r in events) for k in KINDS}, "funding_totals": {k: format(v, ".2f") for k, v in sorted(amounts.items())}, "reported_roles": sum(r.get("roles", 0) for r in events), "synthetic_records": sum(r["synthetic"] for r in checked), "real_records": sum(not r["synthetic"] for r in checked), "events": events, "benefits": "Time and money saved: unmeasured; no estimate reported."}
