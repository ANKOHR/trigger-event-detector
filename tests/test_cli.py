import json
import time
from trigger_event_detector.cli import main
from trigger_event_detector.fixtures import generate

def test_run_completes_on_fixture(tmp_path, capsys):
    generate(tmp_path / "inputs")
    state = tmp_path / "state.json"
    start = time.perf_counter()
    assert main(["run", "--input", str(tmp_path / "inputs"), "--state", str(state)]) == 0
    assert main(["report", "--state", str(state), "--format", "md"]) == 0
    assert time.perf_counter() - start < 5
    assert "DATA PROVENANCE" in capsys.readouterr().out

def test_empty_input_renders_without_traceback(tmp_path, capsys):
    directory = tmp_path / "empty"
    directory.mkdir()
    state = tmp_path / "state.json"
    assert main(["run", "--input", str(directory), "--state", str(state)]) == 0
    assert main(["report", "--state", str(state)]) == 0
    assert json.loads(state.read_text())["event_count"] == 0


def test_malformed_input_named_error(tmp_path, capsys):
    (tmp_path / "bad.json").write_text('{\n"records": nope}')
    assert main(["run", "--input", str(tmp_path)]) == 2
    error = capsys.readouterr().err
    assert "ParseError" in error and "bad.json" in error and "line 2" in error
    assert "Traceback" not in error

def test_determinism_byte_identical(tmp_path):
    generate(tmp_path / "input")
    state = tmp_path / "result.json"
    args = ["run", "--input", str(tmp_path / "input"), "--state", str(state)]
    main(args)
    first = state.read_bytes()
    main(args)
    assert first == state.read_bytes()

def test_cli_smoke_all_subcommands(tmp_path, capsys):
    import pytest
    for command in ("fixtures", "run", "report", "events", "shortlist"):
        with pytest.raises(SystemExit) as exc:
            main([command, "--help"])
        assert exc.value.code == 0
    data = tmp_path / "input"
    assert main(["fixtures", "--out", str(data)]) == 0
    for command in ("events", "shortlist"):
        assert main([command, "--input", str(data)]) == 0
        assert "DATA PROVENANCE" in capsys.readouterr().out

def test_missing_input(tmp_path, capsys):
    assert main(["run", "--input", str(tmp_path / "missing")]) == 2
    assert "MissingInput" in capsys.readouterr().err

def test_schema_error_names_file_field(tmp_path, capsys):
    generate(tmp_path)
    p = tmp_path / "events.json"
    data = json.loads(p.read_text())
    del data["records"][0]["company"]
    p.write_text(json.dumps(data))
    assert main(["run", "--input", str(tmp_path)]) == 2
    error = capsys.readouterr().err
    assert "company" in error and "events.json" in error

def test_report_write_failure_no_partial_files(tmp_path, capsys):
    generate(tmp_path / "input")
    state = tmp_path / "state.json"
    assert main(["run", "--input", str(tmp_path / "input"), "--state", str(state)]) == 0
    blocker = tmp_path / "blocker"
    blocker.write_text("keep")
    before = set(tmp_path.iterdir())
    assert main(["report", "--state", str(state), "--out", str(blocker / "report.md")]) == 2
    assert "WriteError" in capsys.readouterr().err
    assert blocker.read_text() == "keep"
    assert set(tmp_path.iterdir()) == before

def test_tiny_handwritten_real_input(tmp_path):
    records = [dict(id=str(i), company="Henry entered company", kind="launch", date="2026-09-30", verified=i < 2, source="hand-entered note", synthetic=False) for i in range(5)]
    (tmp_path / "real.json").write_text(json.dumps(dict(synthetic=False, as_of="2026-09-30", records=records)))
    state = tmp_path / "saved" / "result.json"
    assert main(["run", "--input", str(tmp_path), "--state", str(state)]) == 0
    assert json.loads(state.read_text())["event_count"] == 2
