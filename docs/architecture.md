# Architecture

> Draft. This describes the intended shape of the pipeline and will be updated to match the code as it is written.

## Overview

```
┌──────────────────────────┐
│ Normal Order Generator   │──┐
└──────────────────────────┘  │    ┌──────────────────┐    ┌────────────────────┐    ┌──────────────────┐
                              ├──▶ │ Combine & label  │──▶ │ Feature engineering│──▶ │ Model / scoring  │
┌──────────────────────────┐  │    └──────────────────┘    └────────────────────┘    └──────────────────┘
│ Fraud Order Generator    │──┘
└──────────────────────────┘
```

## Stages

### 1. Data generation

Two generators produce synthetic orders: one for legitimate traffic and one for fraudulent traffic. Both should write orders in the same schema so the outputs can be combined. See [data-generation.md](data-generation.md).

- **Implemented in:** `generator/order_generator.py` (normal and fraud orders in one run)
- **Output:** the Supabase raw tables in `sql/001_raw_tables.sql`

### 2. Combine and label

Merges the two generated datasets into one dataset with an `is_fraud` label.

- **Status:** not yet implemented

### 3. Feature engineering

Turns raw order records into model features. Examples might include order velocity, mismatches between billing and shipping, and account age.

- **Status:** not yet implemented

### 4. Modeling and scoring

Trains and evaluates a fraud classifier, then scores new orders.

- **Status:** not yet implemented

## Open questions

- What fraud-to-normal ratio should the combined dataset use?
