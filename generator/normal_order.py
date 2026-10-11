"""Normal (legitimate) order generator for the Owl Park pipeline.

In a Databricks notebook:
    products, real_customers, false_customers = load_seeds(spark)
    order, truth = generate_normal_order(random.Random(42))
"""
import json, random, uuid
from datetime import datetime, timedelta, timezone
from decimal import Decimal, ROUND_HALF_UP

TAX_RATE = Decimal("0.06")
CENT = Decimal("0.01")
CHANNELS, CHANNEL_WEIGHTS = ["web", "app", "kiosk"], [55, 40, 5]


def money(x):
    return Decimal(str(x)).quantize(CENT, ROUND_HALF_UP)


def as_bool(v):
    return str(v).strip().lower() == "true"


def price_tier(d):
    """Ticket price tier for a visit date: weekends, the winter holidays and July are peak."""
    if d.weekday() >= 5 or (d.month == 12 and d.day >= 20) or (d.month == 1 and d.day <= 3) or d.month == 7:
        return "PEAK"
    return "REG" if d.weekday() == 4 else "VALUE"


def line(sku, qty, **attributes):
    p = products[sku]
    unit = money(p["unit_price"])
    return {"sku": sku, "product_name": p["product_name"], "product_type": p["product_type"],
            "qty": qty, "unit_price": float(unit), "line_discount": 0.0,
            "line_total": float(unit * qty), "attributes": attributes}


def new_id(rng):
    return str(uuid.UUID(int=rng.getrandbits(128)))


def generate_normal_order(rng=random, now=None):
    """One legitimate Owl Park order, shaped like a raw_transactions row, plus its ground-truth row."""
    now = now or datetime.now(timezone.utc)
    c = rng.choice(real_customers)
    guest = as_bool(c["is_guest_checkout"])

    # who is going and when
    party = rng.choices([1, 2, 3, 4, 5, 6], weights=[10, 30, 20, 25, 10, 5])[0]
    adults = max(1, round(party * rng.uniform(0.4, 1.0)))
    kids = party - adults
    names = [f'{c["first_name"]} {c["last_name"]}'] + [f'{rng.choice(FIRST_NAMES)} {c["last_name"]}' for _ in range(party - 1)]
    visit = (now + timedelta(days=int(rng.expovariate(1 / 21)) + 1)).date()   # most visits within ~3 weeks

    cart = []
    if rng.random() < 0.05:                                                     # annual pass purchase
        sku = rng.choice(["PASS-FLEDGLING", "PASS-NIGHTOWL", "PASS-SNOWY", "PASS-GREATHORN"])
        for name in names[:rng.randint(1, 2)]:
            cart.append(line(sku, 1, holder_name=name))
    else:
        days = rng.choices([1, 2, 3, 5], weights=[75, 12, 9, 4])[0]
        if days == 1:
            tier = price_tier(visit)
            cart.append(line(f"DAY-1-{tier}-ADULT", adults, visit_date=visit.isoformat(), guest_names=names[:adults]))
            if kids:
                cart.append(line(f"DAY-1-{tier}-CHILD", kids, visit_date=visit.isoformat(), guest_names=names[adults:]))
        else:
            cart.append(line(f"DAY-{days}-ADULT", adults, first_visit_date=visit.isoformat(), days=days, guest_names=names[:adults]))
            if kids:
                cart.append(line(f"DAY-{days}-CHILD", kids, first_visit_date=visit.isoformat(), days=days, guest_names=names[adults:]))
        if rng.random() < 0.30:
            cart.append(line("HOOT-PASS", party, visit_date=visit.isoformat()))
        if rng.random() < 0.50:
            cart.append(line("PARKING-DAY", days, visit_date=visit.isoformat()))
        if days > 1 and rng.random() < 0.6:
            hotel = rng.choice(["HOTEL-ROOST-STD", "HOTEL-ROOST-FAM", "HOTEL-CANOPY-STD", "HOTEL-CANOPY-STE"])
            cart.append(line(hotel, days, check_in=visit.isoformat(),
                             check_out=(visit + timedelta(days=days)).isoformat(), guest_count=party))
        if rng.random() < 0.15:
            dining = rng.choice(["DINE-HOOTENANNY", "DINE-MOONLIGHT", "DINE-PERCH"])
            cart.append(line(dining, party, reservation_ts=f"{visit.isoformat()}T{rng.choice(['08:30', '12:00', '18:30'])}:00",
                             party_size=party))
    if rng.random() < 0.25:
        for sku in rng.sample(["MERCH-PLUSH-HOOTIE", "MERCH-EARS-FEATHER", "MERCH-TEE-ADULT",
                               "MERCH-TEE-YOUTH", "MERCH-HOODIE", "MERCH-MUG"], rng.randint(1, 2)):
            cart.append(line(sku, 1, ship_or_pickup="pickup"))
    if rng.random() < 0.05:                                                     # an occasional gift for family
        name = f'{rng.choice(FIRST_NAMES)} {c["last_name"]}'
        cart.append(line(rng.choice(["GIFT-25", "GIFT-50", "GIFT-100"]), 1, delivery="email",
                         recipients=[{"name": name, "email": name.lower().replace(" ", ".") + "@example.com"}],
                         delivery_date=(now + timedelta(days=rng.randint(0, 14))).date().isoformat()))
    cart = [{"line_number": i, **l} for i, l in enumerate(cart, 1)]

    subtotal = sum(money(l["line_total"]) for l in cart)
    taxable = sum(money(l["line_total"]) for l in cart if l["product_type"] != "gift_card")   # gift cards aren't taxed
    discount = Decimal("0.00")
    tax = (taxable * TAX_RATE).quantize(CENT, ROUND_HALF_UP)

    order = {
        "transaction_id": new_id(rng),
        "request_id": new_id(rng),
        "cart_id": new_id(rng),
        "session_id": new_id(rng),
        "event_ts": now,
        "guest_id": None if guest else c["customer_id"],
        "is_guest_checkout": guest,
        "account_created_at": None if guest else c["account_created_at"],
        "email": c["email"],
        "phone": c["phone"] or None,
        "channel": rng.choices(CHANNELS, weights=CHANNEL_WEIGHTS)[0],
        "device_id": c["device_id"],
        "ip_address": c["ip_address"],
        "ip_country": c["ip_country"],
        "user_agent": c["user_agent"],
        "payment_token": c["payment_token"],
        "card_bin": c["card_bin"],
        "card_last4": str(c["card_last4"]).zfill(4),        # CSV import may have read these as numbers
        "card_expiry": c["card_expiry"],
        "billing_name": c["billing_name"],
        "billing_country": c["billing_country"],
        "billing_postal": str(c["billing_postal"]).zfill(5) if c["billing_country"] == "US" else str(c["billing_postal"]),
        "currency": "USD",
        "subtotal": subtotal,
        "discount": discount,
        "tax": tax,
        "total": subtotal - discount + tax,
        "promo_code": None,
        "cart": cart,
        "status": "pending",   # set to completed / declined once Model 1 has scored it
    }
    truth = {"transaction_id": order["transaction_id"], "is_fraud": False,
             "fraud_pattern": None, "fraud_ring_id": None, "label_available_at": None}
    return order, truth


SEEDS = "`fraud-detection-pipeline`.seeds"
products, real_customers, false_customers, FIRST_NAMES = {}, [], [], []


def load_seeds(spark, schema=SEEDS):
    """Pull the small seed tables into Python once; orders are built from these in memory."""
    global products, real_customers, false_customers, FIRST_NAMES
    products = {r["sku"]: r.asDict() for r in spark.table(f"{schema}.products").collect()}
    real_customers = [r.asDict() for r in spark.table(f"{schema}.real_customers").collect()]
    false_customers = [r.asDict() for r in spark.table(f"{schema}.false_customers").collect()]
    FIRST_NAMES = sorted({c["first_name"] for c in real_customers})
    return products, real_customers, false_customers
