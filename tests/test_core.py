from datetime import date
import pytest
from trigger_event_detector.core import detect, InputError
from trigger_event_detector.fixtures import fixture_data

AS_OF = date(2026, 9, 30)

def test_fixture_ground_truth_matches_hand_computed():
    r = detect(fixture_data()["records"], AS_OF)
    assert r["event_count"] == 50
    assert r["by_kind"] == {"funding": 13, "hiring": 13, "launch": 12, "partnership": 12}
    assert r["funding_totals"] == {"GBP": "13003.25"}
    assert r["reported_roles"] == 39

@pytest.mark.parametrize("field,value", [("amount", "-1"), ("amount", "NaN"), ("amount", "1.001"), ("amount", "1e999999"), ("amount", 100), ("date", "2027-01-01"), ("company", "x" * 10001), ("verified", 1), ("kind", "rumour"), ("kind", []), ("extra", 1), ("currency", "gbp")])
def test_rejects_adversarial_values(field, value):
    r = fixture_data()["records"][0]
    r[field] = value
    with pytest.raises(InputError, match="SchemaError"):
        detect([r], AS_OF)

def test_duplicate_ids():
    r = fixture_data()["records"][0]
    with pytest.raises(InputError, match="duplicate id"):
        detect([r, r], AS_OF)

def test_handles_unicode_and_long_inputs():
    r = fixture_data()["records"][0]
    r["company"] = "東京 café " + "x" * 9000
    r["source"] = "C:\\Users\\henry\\証拠.json"
    assert detect([r], AS_OF)["events"][0] == r

def test_boundary_and_unverified():
    records = fixture_data()["records"][:3]
    records[0]["date"] = "2026-08-31"
    records[1]["date"] = "2026-08-30"
    records[2]["verified"] = False
    assert [r["id"] for r in detect(records, AS_OF)["events"]] == ["event-000"]

def test_different_currencies_never_added():
    records = [fixture_data()["records"][i] for i in (0,4)]
    records[1]["currency"] = "USD"
    assert detect(records, AS_OF)["funding_totals"] == {"GBP": "1000.25", "USD": "1000.25"}
