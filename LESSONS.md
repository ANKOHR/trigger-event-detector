# Lessons for KOML

Synthetic tests validate the assumption that explicit verification flags, event dates and exact decimal amounts can produce fully reconciling outreach signals. They do not validate whether a funding announcement creates demand for Henry's services. That assumption still requires real hand-checking and actual use.

Domain lesson: event freshness and evidence quality are separate. A recent unverified claim is not a qualifying signal under this policy. Money needs per-currency accounting, and missing role counts cannot be interpreted as complete headcount.

Operating rule: plant positive, unverified and stale examples independently, then mutate a qualifying record and require the measured report to change. Keep expectations outside the production data path. Make the as_of date explicit so tomorrow's clock cannot change yesterday's report.

Evidence-based improvement in this build: schema validation was exercised with invalid decimals, booleans masquerading as integers and oversized strings. Validation now rejects these with field-specific errors before any output is written. The mutation test demonstrates that changing a verified flag removes one event and GBP 1000.25 from the report.

Real-world accuracy, adoption, time saved and commercial demand remain unmeasured. The two-week hook and final verdict are pending real evidence.
