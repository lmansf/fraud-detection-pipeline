# Fraud Detection Pipeline

A pipeline for generating synthetic e-commerce order data, both legitimate and fraudulent, and using it to build and evaluate fraud detection. It runs on Supabase (Postgres): a scheduled Python generator simulates Owl Park webstore checkouts, scores each one with a placeholder rules model, and writes four raw tables to Supabase in one transaction.

> **Status:** early development. The scheduled generator and the raw table DDL are in place. Items marked `TODO` are still to be decided or built.

## Repository layout

| Path | Description |
| --- | --- |
| `generator/order_generator.py` | Scheduled job: simulates a window of orders (normal guests plus fraud episodes), scores them, and writes them to Supabase. |
| `sql/001_raw_tables.sql` | DDL for the Supabase raw tables: `raw_transactions`, `raw_fraud_decisions`, `raw_checkout_responses`, `raw_fraud_truth`. |
| `data/seed/` | Synthetic seed data (products, legitimate guests, fraudster identities) and `make_customers.py`, which regenerates the customer pools. Everything in it is fake. |
| `docs/` | Project documentation (see below). |

## Documentation

- [Architecture](docs/architecture.md): pipeline stages and how data moves between them.
- [Data generation](docs/data-generation.md): how the normal and fraud order generators work, plus the order schema.
- [Contributing](docs/contributing.md): environment setup and working conventions.

## Getting started

### Prerequisites

- Python 3 *(TODO: pin the version)*
- `psycopg2-binary`
- A Supabase project with the tables from `sql/001_raw_tables.sql`

### Running the generator

```bash
pip install psycopg2-binary
export SUPABASE_DB_PASSWORD=...   # the Supabase database password; never commit it
python generator/order_generator.py --dry-run              # generate and print a summary, write nothing
python generator/order_generator.py --window-minutes 60    # simulate an hour and write it to Supabase
```

| Environment variable | Purpose |
| --- | --- |
| `SUPABASE_DB_PASSWORD` | Password for the Supabase Postgres user the generator connects as. Required unless `--dry-run`. |

Other options: `--orders-per-hour` (default 120), `--fraud-share` (default 0.03) and `--seed` (blank gives a different run each time).

## Roadmap

- [x] Scheduled order generator writing to Supabase
- [ ] Define a shared order schema
- [ ] Combine and label the datasets
- [ ] Feature engineering
- [ ] Model training and evaluation
- [ ] Scoring and inference
