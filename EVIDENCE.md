# Build acceptance evidence

Measured locally on 2026-10-01 with Python 3.12.10 on Windows, CPU only.

Installed `ted` console entry point completed fixtures, run and Markdown report in 0.765 seconds total wall time, measured with perf_counter around three subprocesses. Acceptance threshold: less than 5 seconds. This is one local measurement, not a general performance guarantee.

36 pytest cases passed. Synthetic ground truth: 200 records, 50 detected events, 13 funding, 13 hiring, 12 launches, 12 partnerships, GBP 13003.25 recorded funding, 39 recorded roles. Exactly the planted IDs were reported, with zero false positives and zero false negatives on this synthetic set. These findings do not measure real-world targeting accuracy.

Mutation evidence: removing event-000 verification gives 49 events and GBP 12003.00. Expectation metadata is never loaded by detection. Repeated runs produce identical saved bytes. Empty inputs, invalid values, invalid JSON, missing inputs, Unicode and failed atomic report writes are exercised by tests.

No real trial, savings baseline, adoption or demand measurement has occurred. The final verdict remains pending the two-week real-use hook.
