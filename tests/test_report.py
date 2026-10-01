from datetime import date
import json
from trigger_event_detector.core import detect
from trigger_event_detector.fixtures import fixture_data, expectations
from trigger_event_detector.report import render

def result():
    return detect(fixture_data()["records"], date(2026,9,30))

def test_report_matches_ground_truth_exact():
    report = json.loads(render(result(), "json"))
    for key in ("input_count", "event_count", "by_kind", "funding_totals", "reported_roles"):
        assert report[key] == expectations()[key]

def test_report_zero_false_positives():
    report = json.loads(render(result(), "json"))
    assert [r["id"] for r in report["events"]] == expectations()["event_ids"]

def test_report_carries_provenance_banner():
    for fmt in ("md", "json"):
        output = render(result(), fmt)
        assert "DATA PROVENANCE" in output
        assert "200 synthetic" in output
        assert "0 real records" in output

def test_hypothetical_figures_labelled():
    for fmt in ("md", "json"):
        assert "Time and money saved: unmeasured; no estimate reported." in render(result(), fmt)

def test_no_em_dashes_in_outputs():
    for fmt in ("md", "json"):
        assert chr(0x2014) not in render(result(), fmt)

def test_corrupted_ground_truth_changes_computation():
    data = fixture_data()
    data["records"][0]["verified"] = False
    report = detect(data["records"], date(2026,9,30))
    assert report["event_count"] == 49
    assert report["funding_totals"] == {"GBP": "12003.00"}
    # Changing the expectations file cannot change results: core only sees records.
    assert report["event_count"] != expectations()["event_count"]

def test_real_provenance():
    r = fixture_data()["records"][0]
    r["synthetic"] = False
    assert "1 real records declared" in render(detect([r], date(2026,9,30)))

def test_input_em_dash_escaped_in_reports():
    r = fixture_data()["records"][0]
    r["company"] = "Example" + chr(0x2014) + "company"
    value = detect([r], date(2026, 9, 30))
    for fmt in ("md", "json"):
        assert chr(0x2014) not in render(value, fmt)
    assert json.loads(render(value, "json"))["events"][0]["company"] == r["company"]
