import json
from trigger_event_detector.fixtures import generate, expectations

def test_fixtures_labelled_synthetic(tmp_path):
    generate(tmp_path)
    for path in tmp_path.iterdir():
        data = json.loads(path.read_text(encoding="utf-8"))
        assert data["synthetic"] is True
        assert "SYNTHETIC" in data["_comment"]
        assert all(r["synthetic"] for r in data.get("records", []))
    assert len(json.loads((tmp_path / "events.json").read_text())["records"]) == 200

def test_fixture_generation_byte_identical(tmp_path):
    generate(tmp_path)
    before = {p.name: p.read_bytes() for p in tmp_path.iterdir()}
    generate(tmp_path)
    assert before == {p.name: p.read_bytes() for p in tmp_path.iterdir()}
    assert expectations()["event_ids"] == [f"event-{i:03}" for i in range(50)]
