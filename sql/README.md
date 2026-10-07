# Software License & Subscription Management System — Database

DBMS project — Woxsen University · B.Tech CSE (AI & ML)
Jampana Naga Satya Sai Rishvarma · 25WU0102105

## Contents

| File | Purpose |
|------|---------|
| `01_schema.sql` | Complete 3NF schema — 12 tables, PK/FK constraints, CHECK rules, UNIQUE license keys, seat-limit & reclaim triggers |
| `02_seed.sql` | Representative sample data (4 vendors, 6 products, 8 users, 6 purchases, 6 licenses, 8 allocations, renewals, compliance checks) |
| `03_views_reports.sql` | 6 reporting views — utilization, department allocations, expiry monitor, compliance violations, vendor spend, upcoming renewals |
| `04_procedures.sql` | Transactional workflows — `sp_allocate_license`, `sp_reclaim_license`, `sp_renew_license`, `sp_run_compliance_check` |
| `05_demo_queries.sql` | Step-by-step prototype demonstration script (12 demos covering FR01–FR08) |
| `../app.py` | Streamlit web UI — dashboard, utilization, allocation/reclaim/renew workflows, compliance sweep, raw tables |
| `../scripts/sqlite_demo.sql` | SQLite mirror of the schema/views/triggers/seed used by the UI when MySQL is unavailable |

## Requirements

- MySQL 8.x (uses `ENUM`, `SIGNAL`, triggers, stored procedures)

## Build & Run

```bash
mysql -u root -p < 01_schema.sql
mysql -u root -p < 02_seed.sql
mysql -u root -p < 03_views_reports.sql
mysql -u root -p < 04_procedures.sql
mysql -u root -p license_mgmt < 05_demo_queries.sql
```

Or from the mysql client: `SOURCE 01_schema.sql;` etc.

## Web UI (Streamlit)

```bash
pip install -r requirements.txt
streamlit run app.py          # uses data/app.db (SQLite demo) by default
```

To point the UI at MySQL instead, set environment variables before starting:

```bash
export LM_DB_HOST=127.0.0.1 LM_DB_USER=root LM_DB_PASSWORD=secret
streamlit run app.py          # now reads/writes the license_mgmt database
```

The UI works against either engine because it uses the shared views from
`03_views_reports.sql` (present in both the MySQL schema and the SQLite
mirror) and plain SQL for workflows. Business rules still fire from the
triggers — rejected inserts are surfaced as error toasts in the browser.

## Business Rules Enforced at the Database Level

| Rule | Enforcement |
|------|-------------|
| Unique license keys | `UNIQUE (license_key)` |
| No allocation beyond purchased seats (BR-03) | `trg_alloc_before_insert` |
| No allocation past license expiry (BR-02) / inactive license (BR-01) | `trg_alloc_before_insert` |
| Valid allocation period (BR-04) | `chk_alloc_dates` + `trg_alloc_before_update` |
| Reclaim on return date | `trg_alloc_before_update` sets `RECLAIMED` |
| Renewal amounts / quantities non-negative | CHECK constraints |
| ACID allocation & renewal workflows | stored procedures with `START TRANSACTION / COMMIT` |

## Verification

The schema, seed data, all 6 views and the seat-limit trigger were executed
end-to-end and produced correct report output; an attempted over-allocation
was correctly rejected by the BR-03 trigger. (Verification harness: SQLite;
the shipped scripts are MySQL 8 dialect. Stored procedures use MySQL syntax
(`SIGNAL`, `ROW_COUNT()`) and were reviewed but require MySQL to execute.)
