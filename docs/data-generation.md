# Data Generation

> Draft. Both order types come from `generator/order_generator.py`. Fill in each section as the generator grows.

## Normal Order Generator

**Code:** `generator/order_generator.py`

Generates synthetic legitimate orders.

- **Parameters:** TODO (for example: number of orders, date range, random seed)
- **Distributions and assumptions:** TODO
- **Output:** TODO

## Fraud Order Generator

**Code:** `generator/order_generator.py`

Generates synthetic fraudulent orders.

- **Parameters:** TODO
- **Fraud patterns modeled:** TODO. Document each pattern the generator simulates, for example:

  | Pattern | Description | Signals it produces |
  | --- | --- | --- |
  | TODO | | |

- **Output:** TODO

## Order schema

Both generators should produce records with the same fields.

| Field | Type | Description |
| --- | --- | --- |
| TODO | | |

## Reproducibility

TODO: describe how random seeds are set so a dataset can be regenerated exactly.
