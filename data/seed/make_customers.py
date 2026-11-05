"""Generate synthetic customer identity pools for the Owl Park order generator.

Writes two CSVs next to this file:
  real_customers.csv  - legitimate guests the generator draws normal orders from
  false_customers.csv - fraudster identities, tagged with the fraud pattern they belong to

Everything here is fake: names are random combinations, emails use reserved example domains,
phone numbers use the 555-01xx fictional range, IPs come from documentation ranges, and only
card BIN + last four are stored (never a full card number), matching raw_transactions.

Run: python data/seed/make_customers.py
"""
import csv
import random
import uuid
from datetime import datetime, timedelta
from pathlib import Path

SEED = 20261011
N_REAL = 250
OUT = Path(__file__).parent
TODAY = datetime(2026, 10, 1)

rng = random.Random(SEED)

FIRST = ["Jordan", "Sam", "Riley", "Avery", "Morgan", "Taylor", "Casey", "Jamie", "Alex", "Quinn", "Priya", "Arjun",
         "Mei", "Wei", "Hiro", "Yuki", "Sofia", "Mateo", "Lucia", "Diego", "Amara", "Kwame", "Zara", "Omar", "Fatima",
         "Noah", "Emma", "Liam", "Olivia", "Ethan", "Ava", "Mason", "Isabella", "Lucas", "Mia", "Elijah", "Harper",
         "Grace", "Henry", "Chloe", "Leo", "Nora", "Ivan", "Elena", "Tomas", "Ana", "Kai", "Leilani", "Rohan", "Aisha"]
LAST = ["Lee", "Patel", "Nguyen", "Garcia", "Smith", "Johnson", "Brown", "Martinez", "Kim", "Chen", "Okafor", "Mensah",
        "Rossi", "Muller", "Silva", "Santos", "Cohen", "Novak", "Ali", "Khan", "Walker", "Young", "Hall", "Allen",
        "Wright", "Lopez", "Hill", "Scott", "Green", "Adams", "Baker", "Nelson", "Carter", "Mitchell", "Perez", "Roberts",
        "Turner", "Phillips", "Campbell", "Parker", "Evans", "Edwards", "Collins", "Stewart", "Morris", "Murphy",
        "Cook", "Rogers", "Reed", "Bailey"]
STREETS = ["Maple", "Oak", "Cedar", "Pine", "Elm", "Willow", "Birch", "Lakeview", "Hillcrest", "Sunset", "River",
           "Park", "Meadow", "Spring", "Highland", "Forest", "Ridge", "Harbor", "Orchard", "Valley"]
SUFFIX = ["St", "Ave", "Rd", "Ln", "Dr", "Ct", "Way", "Blvd"]
# (city, state, postal) - plausible combinations; addresses are invented
US_CITIES = [("Frederick", "MD", "21701"), ("Baltimore", "MD", "21201"), ("Arlington", "VA", "22201"),
             ("Richmond", "VA", "23219"), ("Philadelphia", "PA", "19103"), ("Pittsburgh", "PA", "15222"),
             ("Columbus", "OH", "43215"), ("Charlotte", "NC", "28202"), ("Raleigh", "NC", "27601"),
             ("Atlanta", "GA", "30303"), ("Orlando", "FL", "32801"), ("Tampa", "FL", "33602"), ("Nashville", "TN", "37203"),
             ("Chicago", "IL", "60601"), ("Detroit", "MI", "48226"), ("Minneapolis", "MN", "55401"),
             ("Dallas", "TX", "75201"), ("Austin", "TX", "78701"), ("Houston", "TX", "77002"), ("Denver", "CO", "80202"),
             ("Phoenix", "AZ", "85004"), ("Seattle", "WA", "98101"), ("Portland", "OR", "97204"),
             ("San Diego", "CA", "92101"), ("Sacramento", "CA", "95814"), ("Boston", "MA", "02108"),
             ("Newark", "NJ", "07102"), ("Brooklyn", "NY", "11201"), ("Albany", "NY", "12207"), ("Hartford", "CT", "06103")]
INTL = [("Toronto", "ON", "M5V 2T6", "CA"), ("Vancouver", "BC", "V6B 1A1", "CA"), ("London", "", "EC1A 1BB", "GB"),
        ("Manchester", "", "M1 1AE", "GB"), ("Mexico City", "CDMX", "06600", "MX"), ("Sao Paulo", "SP", "01310-100", "BR"),
        ("Berlin", "", "10115", "DE"), ("Madrid", "", "28013", "ES"), ("Sydney", "NSW", "2000", "AU")]
FOREIGN_IP = ["NL", "RO", "BR", "VN", "GB", "DE", "UA", "ID", "US"]
AREA = ["410", "301", "240", "443", "571", "703", "215", "412", "614", "704", "919", "404", "407", "813", "615",
        "312", "313", "612", "214", "512", "713", "303", "602", "206", "503", "619", "916", "617", "973", "718"]
USER_AGENTS = [
    "Mozilla/5.0 (iPhone; CPU iPhone OS 18_5 like Mac OS X) AppleWebKit/605.1.15 Mobile/15E148",
    "Mozilla/5.0 (Linux; Android 15; Pixel 9) AppleWebKit/537.36 Chrome/139.0 Mobile Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/139.0 Safari/537.36",
    "OwlParkApp/4.12 (iOS 18.5; iPhone15,2)",
    "OwlParkApp/4.12 (Android 15; SM-S928U)",
]
HEADLESS_UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 HeadlessChrome/139.0 Safari/537.36"
# BIN -> brand (BINs are issuer prefixes, not card numbers)
BINS = [("424242", "visa"), ("411111", "visa"), ("400551", "visa"), ("453201", "visa"), ("555555", "mastercard"),
        ("510510", "mastercard"), ("222300", "mastercard"), ("378282", "amex"), ("371449", "amex"), ("601111", "discover")]
EMAIL_DOMAINS = ["example.com", "example.net", "example.org"]
THROWAWAY_DOMAINS = ["mailbox.example", "inbox.example", "tempmail.example"]

FIELDS = ["customer_id", "first_name", "last_name", "email", "phone", "account_created_at", "is_guest_checkout",
          "billing_name", "billing_address", "billing_city", "billing_state", "billing_postal", "billing_country",
          "card_brand", "card_bin", "card_last4", "card_expiry", "payment_token",
          "device_id", "ip_address", "ip_country", "user_agent"]
FRAUD_FIELDS = FIELDS + ["fraud_pattern", "fraud_ring_id", "victim_customer_id"]


def uid():
    return str(uuid.UUID(int=rng.getrandbits(128)))


def ip():
    return f"{rng.choice(['192.0.2', '198.51.100', '203.0.113'])}.{rng.randint(1, 254)}"


def device():
    return f"dev_{rng.getrandbits(48):012x}"


def card():
    bin_, brand = rng.choice(BINS)
    exp = TODAY + timedelta(days=rng.randint(60, 1800))
    return {"card_brand": brand, "card_bin": bin_, "card_last4": f"{rng.randint(0, 9999):04d}",
            "card_expiry": exp.strftime("%m/%y"), "payment_token": f"tok_{rng.getrandbits(64):016x}"}


def address(international=False):
    num = rng.randint(10, 9899)
    street = f"{num} {rng.choice(STREETS)} {rng.choice(SUFFIX)}"
    if international:
        city, state, postal, country = rng.choice(INTL)
    else:
        (city, state, postal), country = rng.choice(US_CITIES), "US"
    return {"billing_address": street, "billing_city": city, "billing_state": state,
            "billing_postal": postal, "billing_country": country}


def phone(country="US"):
    return f"+1-{rng.choice(AREA)}-555-01{rng.randint(0, 99):02d}" if country in ("US", "CA") else ""


def iso(dt):
    return dt.strftime("%Y-%m-%dT%H:%M:%SZ") if dt else ""


# ---------------------------------------------------------------- real customers
real = []
for _ in range(N_REAL):
    first, last = rng.choice(FIRST), rng.choice(LAST)
    tourist = rng.random() < 0.12                 # legitimate visitors with foreign billing
    addr = address(international=tourist)
    guest = rng.random() < 0.15
    created = None if guest else TODAY - timedelta(days=rng.randint(20, 2400), seconds=rng.randint(0, 86399))
    row = {
        "customer_id": uid(), "first_name": first, "last_name": last,
        "email": f"{first.lower()}.{last.lower()}{rng.randint(1, 999)}@{rng.choice(EMAIL_DOMAINS)}",
        "phone": phone(addr["billing_country"]), "account_created_at": iso(created), "is_guest_checkout": guest,
        # a few people pay with a partner's card, so billing name differs from the account name
        "billing_name": f"{first} {last}" if rng.random() > 0.06 else f"{rng.choice(FIRST)} {last}",
        **addr, **card(),
        "device_id": device(), "ip_address": ip(),
        # tourists browse from home; some US customers travel or use a VPN
        "ip_country": addr["billing_country"] if rng.random() > 0.05 else rng.choice(["CA", "GB", "MX"]),
        "user_agent": rng.choice(USER_AGENTS),
    }
    real.append(row)

# ---------------------------------------------------------------- fraudster identities
false = []


def fraud_row(pattern, ring=None, **overrides):
    first, last = rng.choice(FIRST), rng.choice(LAST)
    addr = address()
    row = {
        "customer_id": uid(), "first_name": first, "last_name": last,
        "email": f"{uuid.UUID(int=rng.getrandbits(128)).hex[:10]}@{rng.choice(THROWAWAY_DOMAINS)}",
        "phone": "", "account_created_at": iso(TODAY - timedelta(days=rng.randint(0, 14), seconds=rng.randint(0, 86399))),
        "is_guest_checkout": False, "billing_name": f"{rng.choice(FIRST)} {rng.choice(LAST)}",  # stolen card owner
        **addr, **card(),
        "device_id": device(), "ip_address": ip(), "ip_country": rng.choice(FOREIGN_IP),
        "user_agent": rng.choice(USER_AGENTS + [HEADLESS_UA]),
        "fraud_pattern": pattern, "fraud_ring_id": ring or "", "victim_customer_id": "",
    }
    row.update(overrides)
    return row


# card testing: one bot device cycling many stolen cards as guest checkouts
for _ in range(3):
    dev, addr_ip = device(), ip()
    for _ in range(rng.randint(5, 8)):
        false.append(fraud_row("card_testing", device_id=dev, ip_address=addr_ip, user_agent=HEADLESS_UA,
                               is_guest_checkout=True, account_created_at=""))

# stolen-card resale: brand-new accounts buying peak tickets with someone else's card
for _ in range(10):
    false.append(fraud_row("stolen_card_resale"))

# gift card cash-out: throwaway accounts, mismatched IP
for _ in range(8):
    false.append(fraud_row("gift_card_cashout", ip_country=rng.choice([c for c in FOREIGN_IP if c != "US"])))

# account takeover: a real customer's account and card, used from a new device and location
for victim in rng.sample([r for r in real if not r["is_guest_checkout"]], 8):
    false.append({**victim, "device_id": device(), "ip_address": ip(),
                  "ip_country": rng.choice([c for c in FOREIGN_IP if c != victim["billing_country"]]),
                  "user_agent": rng.choice(USER_AGENTS + [HEADLESS_UA]),
                  "fraud_pattern": "account_takeover", "fraud_ring_id": "", "victim_customer_id": victim["customer_id"]})

# fraud rings: several identities sharing devices, an IP and a drop address
for _ in range(3):
    ring, devs, ring_ip = uid(), [device(), device()], ip()
    drop = address()
    for _ in range(rng.randint(4, 6)):
        false.append(fraud_row("fraud_ring", ring=ring, device_id=rng.choice(devs), ip_address=ring_ip, **drop))

rng.shuffle(false)

for name, rows, fields in [("real_customers.csv", real, FIELDS), ("false_customers.csv", false, FRAUD_FIELDS)]:
    with open(OUT / name, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)
    print(f"wrote {name}: {len(rows)} rows")
