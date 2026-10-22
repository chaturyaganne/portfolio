# LeaseFlow - rental data quality and analytics

A self-directed data engineering project by Chaturya Ganne, built around the ingestion, data quality, warehouse modeling, lightweight apps, and analytics needs in the supplied TheGuarantors Data Engineer description. It is not affiliated with TheGuarantors and uses no company or renter data.

Demo: https://chaturyaganne.github.io/portfolio/leaseflow/
Source: https://github.com/chaturyaganne/portfolio/tree/main/leaseflow

## What works

- Three CSV source contracts: properties, leases, and payment events.
- Content-addressed, insert-only raw records with source/run lineage.
- Validation of required fields, identifiers, UTC-aware update timestamps, integer-cent amounts, date order, and foreign keys.
- Quarantine with structured reasons, raw values, source, entity ID and first/last-seen run IDs.
- Version-aware incremental upserts. Unchanged rows make no curated writes; older updates are skipped; equal-version conflicts are quarantined.
- Late-arriving payment events accepted by record-update time instead of being lost through an event-date cutoff.
- SQL property and property/day marts with pre-aggregation to avoid join fanout.
- Transactional curated/bronze/quality writes. A failed run rolls back those writes and retains a failed run record.
- A lightweight local HTTP data app with overview endpoints and create/read/update/delete for issue-review notes.
- A public read-only dashboard generated from actual fixture runs.
- Fourteen passing Python regression tests and separate DOM checks for the dashboard.

## Reproduce

Python 3.11+; no third-party runtime packages.

```bash
python -m unittest tests -v
python pipeline.py --input fixtures --db var/warehouse.db --export snapshot.json
python pipeline.py --input fixtures --db var/warehouse.db --export snapshot.json
python app.py --db var/warehouse.db
```

Open http://127.0.0.1:4180. Local mode queries SQLite and enables issue-note CRUD. The public GitHub Pages dashboard reads `snapshot.json` and has no database or write endpoint.

To regenerate the public demonstration independently of your local warehouse:

```bash
python build_demo.py
```

This uses an isolated temporary database, runs the same fixture twice, and exports the observed results. Data app input stays local; do not deploy the loopback server as a multi-user production service without authentication, authorization, appropriate hosting, and operational hardening.

## Observed fixture results

The checked-in fixture intentionally contains bad records and one duplicate.

| Observation | Initial run | Repeat run |
| --- | ---: | ---: |
| Source rows read | 21 | 21 |
| Curated inserts | 13 | 0 |
| Curated updates | 0 | 0 |
| Unchanged curated rows | 0 | 13 |
| Quarantined input rows | 7 | 7 |
| Duplicate input rows skipped | 1 | 1 |

Curated tables contain 3 properties, 4 leases, and 6 payment events. Bronze contains 20 unique raw records. Eight active quality issues include seven invalid rows and a duplicate warning. One row can have multiple validation issues; issue counts are not generally interchangeable with quarantined-row counts. Timings in the dashboard are observations on this tiny fixture, not throughput claims.

The marts reconcile to 4 leases, $10,400 in summed monthly lease amounts, and $11,400 in recorded payment events. These are synthetic dataset totals, not business impact or a claim about delinquency, occupancy, tenant risk, or revenue recognition.

## Data model

```text
CSV contracts
  -> bronze_records (source + content hash, immutable payload)
  -> properties -> leases -> payments (curated keys and relationships)
       -> mart_property_summary
       -> mart_property_day
  -> issues + row_outcomes + runs (quality and lineage)
       -> notes (local review workflow)
```

- `properties`: one current version per property ID.
- `leases`: one current version per lease ID, related to a curated property.
- `payments`: one current version per payment event ID, related to a curated lease.
- `mart_property_summary`: separately aggregates leases and payments before joining to properties. Monthly rent is the sum of loaded lease amounts; it is not an occupancy or accounting measure.
- `mart_property_day`: payment count, distinct leases and payment amount per property and event date. Suitable for exploratory analysis and downstream data preparation, not a point-in-time feature store.

Currency uses integer cents throughout. Source update timestamps are normalized to UTC with microsecond precision. Payment event dates remain separate, allowing old activity dates with newer record versions.

## Incremental behavior and orchestration

The CLI executes ordered stages: validate all file schemas, load properties, load leases, load payments, and commit the run. The input remains a **full file scan**; incremental behavior refers to version-aware curated writes, not incremental extraction or CDC. `watermarks` records the maximum accepted update timestamp for inspection; it is not used as an extraction cutoff, so older unseen business keys are not discarded.

Reprocessing is deliberate: invalid records can be reevaluated and foreign-key dependencies can resolve in a later batch. Active issues reflect the latest successful complete supplied batch. Historical issue entries and row outcomes remain available. This prototype does not implement source deletions, cross-file streaming, slowly changing dimensions, a hosted scheduler, or distributed execution. SQL views expose committed curated data without an additional materialization job.

## Local API

| Method | Route | Behavior |
| --- | --- | --- |
| GET | `/api/overview` | Current table counts, quality, marts and recent run metadata |
| GET | `/api/notes` | Read local review notes |
| POST | `/api/notes` | Create note with `issue_id` and `text` |
| PATCH | `/api/notes/{id}` | Update note text |
| DELETE | `/api/notes/{id}` | Delete a note |

Bodies are bounded, note text is validated, and SQL values are parameterized. Mutations with a non-loopback browser origin are rejected. The app binds only to loopback by default. There is no authentication or multi-tenant authorization; all records are fictional. Adding a review note does not repair a source record or change ingestion outcomes.

## Tests and engineering evidence

Fourteen Python checks cover input accounting, idempotence, foreign keys, late arrivals, newer/stale/conflicting versions, schema drift, failure rollback, aggregate reconciliation, integer/date validation, timezone precision, parameterized values, and API note CRUD/error cases. The dashboard has DOM checks for observed metrics, issue filtering, and escaped source inspection. Real browser visual/accessibility verification remains separate.

The test-driven work exposed an SQLite connection-lifecycle issue on Windows; connections are now explicitly closed through a scoped session helper. Rollback tests deliberately inject a stage failure and verify that previously committed data stays intact.

## Tool and evidence boundaries

This project implements a **local SQLite warehouse**. It does not claim deployment to Snowflake, BigQuery, Redshift, or a cloud account. It uses Python CSV ingestion rather than claiming experience with Airbyte, Fivetran, Stitch, or Talend. No Airflow/Dagster deployment is included. Those are reasonable next integration steps, not completed work.

AI-assisted development supported implementation and tests. All reported fixture results come from executing the code. No customer deployment, measured business savings, production-scale benchmark, predictive underwriting model, or real renter data is claimed.
