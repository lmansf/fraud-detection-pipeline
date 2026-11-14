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

## Products

Every cart line comes from the real Owl Park Shopify catalog in `data/seed/shopify_catalog.csv` (refresh it with `generator/sync_shopify_catalog.py`). Only `ACTIVE` variants are sold.

- **Mapping:** the sync script gives each Shopify product a `product_type`: gift cards are `gift_card`, products tagged `annual` or `pass` are `annual_pass`, tagged `day` are `day_ticket`, other tickets are `event_ticket`, and anything else takes its Shopify product type (for example `merch`). Normal guests buy day tickets for their party, sometimes annual passes or an event night; any other type is sold as an occasional add-on, so new Shopify products show up in the data after a sync.
- **Fraud patterns follow the catalog:** card testers buy the cheapest items, resellers and fraud rings buy day tickets in bulk for peak dates, account takeovers buy the dearest annual pass or gift card. A pattern whose products the store doesn't sell is switched off for the run and named in the log; `gift_card_cashout` is off while the store has no gift card.
- **Value rules scale with price:** the `HIGH_ORDER_VALUE` and `HIGH_VALUE_GIFT_CARDS` thresholds are 11 and 3 day tickets, which matches the old $1,500 and $400 under the made-up catalog.
- **Cart line fields:** `sku`, `product_name`, `product_type`, `shopify_product_id`, `shopify_variant_id`, `product_handle`, `catalog_synced_at`, `qty`, `list_price` (Shopify compare-at price, or the price when there is none), `unit_price`, `line_discount`, `line_total`, `attributes`. The Shopify ids join generated lines to real Shopify order lines; price, list price, category and quantity per line are there for per-product models and policies later.
- **History:** rows written before this change use the old made-up SKUs (`DAY-1-PEAK-ADULT` and so on) and have no Shopify ids. Filter on `shopify_variant_id` being present to get catalog-based rows only.

## Order schema

Both generators should produce records with the same fields.

| Field | Type | Description |
| --- | --- | --- |
| TODO | | |

## Reproducibility

TODO: describe how random seeds are set so a dataset can be regenerated exactly.
