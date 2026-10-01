"""Local-file CLI. Input and output failures are named without tracebacks."""
import argparse
from datetime import date
import json
import os
from pathlib import Path
import sys
import tempfile
from .core import InputError, detect, KINDS
from .fixtures import generate
from .report import render

DEFAULT_STATE = ".ted/results.json"

def load_input(directory, override=None):
    root = Path(directory)
    if not root.is_dir():
        raise InputError(f"MissingInput: {root}; use ted fixtures --out demo or provide an input directory")
    records, dates, files = [], set(), []
    for path in sorted(root.iterdir()):
        if not path.is_file() or path.name == "expectations.json":
            continue
        if path.suffix != ".json":
            raise InputError(f"SchemaError: {path}: line 1: unsupported input format; use JSON")
        try:
            data = json.loads(path.read_text(encoding="utf-8-sig"))
        except json.JSONDecodeError as exc:
            raise InputError(f"ParseError: {path}: line {exc.lineno}: {exc.msg}") from None
        except UnicodeError:
            raise InputError(f"ParseError: {path}: line 1: invalid UTF-8") from None
        if not isinstance(data, dict) or set(data) - {"_comment", "synthetic", "as_of", "records"} or type(data.get("synthetic")) is not bool or not isinstance(data.get("records"), list):
            raise InputError(f"SchemaError: {path}: line 1: expected synthetic, as_of and records fields")
        try:
            dates.add(date.fromisoformat(data["as_of"]))
        except (KeyError, TypeError, ValueError):
            raise InputError(f"SchemaError: {path}: line 1: as_of must be YYYY-MM-DD") from None
        for index, record in enumerate(data["records"]):
            if not isinstance(record, dict) or record.get("synthetic") is not data["synthetic"]:
                raise InputError(f"SchemaError: {path}: line 1: records[{index}].synthetic conflicts with file label")
            # Validate per file so schema failures name their originating file.
            try:
                detect([record], override or date.fromisoformat(data["as_of"]))
            except InputError as exc:
                raise InputError(f"{exc}: {path}: line 1: records[{index}]") from None
        records.extend(data["records"])
        files.append(path.as_posix())
    if override is None and len(dates) > 1:
        raise InputError("SchemaError: as_of differs between input files; specify --as-of")
    if not dates and override is None:
        override = date(2026, 9, 30)
    return records, override or next(iter(dates)), files

def atomic_write(path, text):
    path = Path(path)
    temporary = None
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", newline="\n", dir=path.parent, delete=False) as f:
            temporary = f.name
            f.write(text)
        os.replace(temporary, path)
    except OSError as exc:
        raise InputError(f"WriteError: {path}: {exc.strerror or str(exc)}") from None
    finally:
        if temporary and os.path.exists(temporary):
            os.unlink(temporary)

def parser():
    p = argparse.ArgumentParser(description="Compute verified recorded triggers from local JSON. No discovery or prediction.")
    sub = p.add_subparsers(dest="command", required=True)
    f = sub.add_parser("fixtures", help="Generate 200 labelled synthetic records", epilog="Example: ted fixtures --out demo")
    f.add_argument("--out", required=True)
    for name, help_text in (("run", "Compute and save all recorded triggers"), ("events", "Inspect recorded triggers of one kind"), ("shortlist", "Group recorded triggers by company")):
        q = sub.add_parser(name, help=help_text, description=help_text, epilog=f"Example: ted {name} --input demo")
        q.add_argument("--input", required=True)
        q.add_argument("--as-of", type=date.fromisoformat)
        q.add_argument("--window-days", type=int, default=30)
        if name == "run":
            q.add_argument("--state", default=DEFAULT_STATE)
        if name == "events":
            q.add_argument("--kind", choices=KINDS)
    r = sub.add_parser("report", help="Render saved computed results with provenance", epilog="Example: ted report --format md")
    r.add_argument("--format", choices=("md", "json"), default="md")
    r.add_argument("--state", default=DEFAULT_STATE)
    r.add_argument("--out")
    return p

def main(argv=None):
    args = parser().parse_args(argv)
    try:
        if args.command == "fixtures":
            generate(args.out)
            print("Generated 200 SYNTHETIC records and hand-computed expectations.")
            return 0
        if args.command == "report":
            path = Path(args.state)
            if not path.is_file():
                raise InputError(f"MissingInput: {path}; run ted run --input demo first")
            try:
                result = json.loads(path.read_text(encoding="utf-8"))
                output = render(result, args.format)
            except (ValueError, KeyError, TypeError) as exc:
                raise InputError(f"SchemaError: {path}: line 1: invalid saved result: {exc}") from None
            if args.out:
                atomic_write(args.out, output)
            else:
                print(output, end="")
            return 0
        records, as_of, files = load_input(args.input, args.as_of)
        result = detect(records, as_of, args.window_days)
        result["input_files"] = files
        if args.command == "run":
            atomic_write(args.state, render(result, "json"))
            print(f"Computed {result['event_count']} recorded triggers from {result['input_count']} records. Synthetic: {result['synthetic_records']}; real declared: {result['real_records']}. Benefits unmeasured.")
        elif args.command == "events":
            if args.kind:
                result["selected_events"] = [r for r in result["events"] if r["kind"] == args.kind]
            print(render(result, "json"), end="")
        else:
            result["shortlist"] = [{"company": company, "event_ids": [r["id"] for r in result["events"] if r["company"] == company]} for company in sorted({r["company"] for r in result["events"]})]
            print(render(result, "json"), end="")
        return 0
    except InputError as exc:
        print(str(exc).replace(chr(0x2014), "\\u2014"), file=sys.stderr)
        return 2
    except OSError as exc:
        print(f"FileError: {exc.filename}: {exc.strerror}", file=sys.stderr)
        return 2

if __name__ == "__main__":
    sys.exit(main())
