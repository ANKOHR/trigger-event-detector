# Trigger Event Detector

`ted` identifies recorded funding, hiring, launch and partnership events that give an outreach operator a reason to review a contact now. Python 3.10+, CPU only, standard library runtime, no network calls, no models, no database.

Hypothesis: deterministic qualification against explicit evidence gives Henry a trustworthy targeting tool. The build validates mechanical accuracy against synthetic planted truth. It does not establish commercial demand or accuracy of real source claims.

## Quickstart

Install locally with an existing setuptools installation:

```powershell
python -m pip install --no-index --no-deps --no-build-isolation -e .
ted fixtures --out demo
ted run --input demo
ted report --format md
python -m pytest -q
```

If the Python Scripts directory is not on PATH, replace `ted` with `python -m trigger_event_detector.cli`. Run commands from the same working directory, or pass `--state` explicitly. The state defaults to `.ted/results.json`. Reports do not recompute state; rerun after changing inputs.

The 200-record fixture yields exactly 50 events: funding 13, hiring 13, launch 12, partnership 12. Recorded GBP funding is 13003.25 and recorded hiring roles total 39. These are synthetic amounts and counts, not real campaign results. The hand-computed expectations file is never read by detection.

A small handwritten five-record synthetic example lives in `examples/tiny/events.json`. Run `ted run --input examples/tiny` to exercise the smallest workflow.

## Input reference

An input directory holds UTF-8 JSON files. Each file is an object with `synthetic` (boolean), `as_of` (YYYY-MM-DD), `records` (array), and optional `_comment`. Unsupported formats fail with a named schema error; convert CSV or YAML to JSON first. `expectations.json` is reserved fixture metadata and ignored. Subdirectories are ignored. Keep reports and state outside input directories.

Every record requires:

| Field | Rule |
| --- | --- |
| id | Unique across the entire run, nonempty text |
| company | Nonempty text; grouping is exact and case sensitive |
| kind | funding, hiring, launch, partnership |
| date | ISO date no later than the run's as_of |
| verified | Boolean claim made by the input author |
| source | Nonempty evidence citation, URL, local Windows path or note; never fetched |
| synthetic | Boolean matching the file label |

Optional `detail` is text. Each text field is capped at 10000 characters. `amount` is a nonnegative finite decimal string up to 10^15 with at most two decimal places, for funding only. It requires an uppercase three-letter ASCII `currency`. Currency is a label, not a validated exchange rate; totals remain separate per currency. Optional `roles` is an integer from 0 to 1000000 for hiring only. Missing amounts and role counts contribute nothing; totals cover only recorded values, not complete company finances or headcount. Unknown fields, duplicate IDs, invalid types and future dates fail the whole run. Records are never silently dropped due to invalid data.

Detection includes verified records aged 0 through `--window-days` inclusive (default 30, range 0 to 3650). Old and unverified records remain in input counts but are not triggers. Each event is counted once; repeated evidence with different IDs is not deduplicated. Company aliases are not inferred. No ranking or contact suitability is claimed.

Use `synthetic: false` only for Henry's own real data entered by him, with his chosen source and verification claim. Reports call this real data declared by the input author; the software cannot prove who entered it or independently verify it. Real trial data and results should stay local and uncommitted. Mixed real and synthetic files are counted separately. Without an override, all files must agree on `as_of`. Empty directories produce zeros using a documented fixed as_of of 2026-09-30; `--as-of` overrides it. No clock-dependent behavior or random seed is used.

## Commands

```powershell
ted fixtures --out demo
ted run --input demo --as-of 2026-09-30 --window-days 30 --state .ted/results.json
ted report --format json --out .ted/report.json
ted events --input demo --kind funding
ted shortlist --input demo
```

`fixtures` writes explicitly labelled synthetic events and independent expectations. `run` validates, computes and atomically saves results. `report` renders Markdown or JSON with provenance and optionally atomically writes a file. `events` inspects events, adding `selected_events` when `--kind` is specified while retaining whole-run totals. `shortlist` groups detected event IDs by exact company name; it makes no claim that a person is suitable to contact. All commands provide `--help` and examples.

## Architecture

```text
local JSON -> CLI parser and validation -> pure core detection
synthetic generator -> labelled events + independent expectations
core result -> atomic state file -> report renderer -> Markdown / JSON
core result -> events inspection / company shortlist
```

## Honesty boundary

All figures are computed from explicit inputs. There is no discovery, prediction, inferred hiring intent, estimated likelihood, invented source, or estimated benefit. Time and money saved are unmeasured and no estimate is reported. Funding amounts are recorded input values, not money saved. Runtime measured by the acceptance demo is performance evidence only. Synthetic demonstrations do not measure real-world targeting accuracy.

Every fixture JSON has a leading `_comment` identifying it as SYNTHETIC plus `synthetic: true`; each event also carries the field. JSON has no comment syntax, so `_comment` is the header comment representation. Every report and domain inspection carries a provenance banner, input file paths, real and synthetic counts. JSON output retains Unicode. Input em dash characters are escaped as a Unicode escape in reports to keep output free of literal em dashes.

## Failures and limits

Malformed JSON names the file and actual parse line. Schema errors name the file, field and record index; their line 1 refers to the document root, not a claimed precise field location. Missing directories and saved state produce `MissingInput` with a usage hint. Unsupported input shapes produce `SchemaError`. Report writes use a temporary file and atomic replacement, clean up on failure, and produce `WriteError`. Errors exit 2 without a traceback. Existing fixture files are overwritten on generation. No transaction across multiple fixture files is promised.

Sources, verified flags, dates and IDs are author claims. Stale dates, fabricated verification, duplicate real events with different IDs, company aliases and incomplete records can lower real usefulness despite perfectly correct computation. Saved results are local trusted artifacts, not a tamper-proof ledger.

## Evidence-based improvement and verdict

After two weeks of real use, hand-check every reported and non-reported event in a sample of at least 50 real records. Measure error rate as (false positives + false negatives) / sampled records, using this documented window and rule as the reference. Record sample size, errors, daily use and the top cause locally using `TRIAL-TEMPLATE.md`. Do not ship private trial results. If error rate exceeds 10 percent, fix the largest cause and repeat the sample or kill the project. If unused, record the reason and kill it.

Current status: acceptance build complete; two-week real evidence window has not occurred. No demand, daily use, savings or buyer willingness has been measured. A final expand / integrate / commercialise / maintain / kill verdict is pending that evidence, not invented now. Choose expand for daily use or revenue, integrate for substantial sibling overlap, commercialise for demonstrated willingness to pay, maintain for portfolio evidence otherwise, or kill if unused or unable to meet acceptance criteria. Record the reason and evidence with the verdict.
