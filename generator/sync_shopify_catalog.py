"""Sync the Owl Park Shopify catalog into data/seed/shopify_catalog.csv.

The order generator draws every simulated cart line from that file, so generated orders carry the
same product and variant ids as real Shopify orders and can be joined to them later.

Run this whenever products or prices change in Shopify, then commit the updated CSV:

    export SHOPIFY_STORE_DOMAIN=<your-store>.myshopify.com
    export SHOPIFY_ADMIN_TOKEN=...      # Admin API token with read_products; never commit it
    python generator/sync_shopify_catalog.py

Or transform a saved Admin GraphQL `products` response (for example one pulled through a Shopify
connector) without calling the API:

    python generator/sync_shopify_catalog.py --from-json products.json

Only the standard library is used.
"""
import argparse
import csv
import json
import os
import re
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

API_VERSION = "2025-07"
OUT = Path(__file__).resolve().parent.parent / "data" / "seed" / "shopify_catalog.csv"
COLUMNS = [
    "shopify_product_id", "shopify_variant_id", "product_handle", "product_title", "variant_title",
    "sku", "shopify_product_type", "product_type", "tags", "status", "price", "compare_at_price",
    "is_gift_card", "requires_shipping", "synced_at",
]
QUERY = """
query($after: String) {
  products(first: 100, after: $after) {
    pageInfo { hasNextPage endCursor }
    nodes {
      id handle title productType status tags isGiftCard
      variants(first: 100) {
        nodes { id sku title price compareAtPrice inventoryItem { requiresShipping } }
      }
    }
  }
}
"""


def product_type(p):
    """Map a Shopify product to the generator's product_type (the category features and rules use)."""
    tags = {t.lower() for t in p.get("tags", [])}
    shop_type = (p.get("productType") or "").strip().lower()
    if p.get("isGiftCard"):
        return "gift_card"
    if "annual" in tags or "pass" in tags:
        return "annual_pass"
    if "day" in tags:
        return "day_ticket"
    if shop_type == "ticket" or "ticket" in tags:
        return "event_ticket"
    return re.sub(r"[^a-z0-9]+", "_", shop_type).strip("_") or "other"


def fetch_products(domain, token):
    nodes, after = [], None
    while True:
        req = urllib.request.Request(
            f"https://{domain}/admin/api/{API_VERSION}/graphql.json",
            data=json.dumps({"query": QUERY, "variables": {"after": after}}).encode(),
            headers={"Content-Type": "application/json", "X-Shopify-Access-Token": token},
        )
        with urllib.request.urlopen(req, timeout=30) as r:
            body = json.load(r)
        if body.get("errors"):
            raise SystemExit(f"Shopify API error: {body['errors']}")
        page = body["data"]["products"]
        nodes += page["nodes"]
        if not page["pageInfo"]["hasNextPage"]:
            return nodes
        after = page["pageInfo"]["endCursor"]


def to_rows(products, synced_at):
    rows = []
    for p in products:
        for v in p["variants"]["nodes"]:
            rows.append({
                "shopify_product_id": p["id"],
                "shopify_variant_id": v["id"],
                "product_handle": p["handle"],
                "product_title": p["title"],
                "variant_title": v.get("title") or "",
                "sku": v.get("sku") or v["id"].rsplit("/", 1)[-1],
                "shopify_product_type": p.get("productType") or "",
                "product_type": product_type(p),
                "tags": "|".join(p.get("tags", [])),
                "status": p["status"],
                "price": v["price"],
                "compare_at_price": v.get("compareAtPrice") or "",
                "is_gift_card": str(bool(p.get("isGiftCard"))).lower(),
                "requires_shipping": str(bool((v.get("inventoryItem") or {}).get("requiresShipping"))).lower(),
                "synced_at": synced_at,
            })
    return sorted(rows, key=lambda r: (r["product_handle"], r["shopify_variant_id"]))


def main():
    ap = argparse.ArgumentParser(description="Write data/seed/shopify_catalog.csv from Shopify.")
    ap.add_argument("--from-json", help="Saved Admin GraphQL products response to transform instead of calling the API")
    ap.add_argument("--out", default=str(OUT), help="Output CSV path")
    args = ap.parse_args()

    if args.from_json:
        with open(args.from_json, encoding="utf-8") as f:
            products = json.load(f)["data"]["products"]["nodes"]
    else:
        domain, token = os.environ.get("SHOPIFY_STORE_DOMAIN"), os.environ.get("SHOPIFY_ADMIN_TOKEN")
        if not domain or not token:
            raise SystemExit("Set SHOPIFY_STORE_DOMAIN and SHOPIFY_ADMIN_TOKEN (or use --from-json).")
        products = fetch_products(domain, token)

    rows = to_rows(products, datetime.now(timezone.utc).replace(microsecond=0).isoformat())
    with open(args.out, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=COLUMNS)
        w.writeheader()
        w.writerows(rows)
    active = sum(r["status"] == "ACTIVE" for r in rows)
    print(f"wrote {len(rows)} variants ({active} active) to {args.out}")
    for r in rows:
        print(f"  {r['status']:<8} {r['product_type']:<14} {r['sku']:<20} {r['price']:>8}  {r['product_title']}")


if __name__ == "__main__":
    main()
