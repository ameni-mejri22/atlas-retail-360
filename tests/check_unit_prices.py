
import csv
import json
from pathlib import Path
from datetime import datetime, timedelta
from decimal import Decimal, ROUND_HALF_UP
import pyarrow.parquet as pq

data_dir = Path("data/generated")
CENT = Decimal("0.01")

# Charger le catalogue produits
product_rows = pq.read_table(
    data_dir / "product_versions.parquet"
).to_pylist()

products = {
    row["product_id"]: row
    for row in product_rows
}

# Charger les commandes
with (data_dir / "orders.jsonl").open(encoding="utf-8") as f:
    orders = {
        order["order_id"]: order
        for line in f
        if line.strip()
        for order in [json.loads(line)]
    }

# Charger les taux de change
with (data_dir / "fx_rates.csv").open(
    encoding="utf-8",
    newline=""
) as f:
    rates = {
        (row["currency"], row["rate_date"]):
        Decimal(row["eur_per_unit"])
        for row in csv.DictReader(f)
    }

# Charger les lignes
with (data_dir / "order_lines.csv").open(
    encoding="utf-8",
    newline=""
) as f:
    lines = list(csv.DictReader(f))

invalid_prices = []
invalid_margins = []
invalid_fx = []

for line in lines:
    price_local = Decimal(line["unit_price_ht"])

    if price_local <= 0:
        invalid_prices.append(line)
        continue

    product = products[line["product_id"]]
    order = orders[line["order_id"]]

    # Reconstituer le prix EUR à partir du coût et de la marge
    unit_cost = Decimal(str(product["unit_cost"]))

    currency = order["currency"]

    target_timestamp = (
        line["invoice_ts"]
        if line["invoice_ts"]
        else order["order_ts"]
    )

    target_date = datetime.fromisoformat(
        target_timestamp
    ).date()

    # Retrouver le taux utilisé : date du jour ou dernier taux
    # disponible dans les 7 jours précédents.
    rate = None

    if currency == "EUR":
        rate = Decimal("1")
    else:
        for days_back in range(8):
            rate_date = (
                target_date - timedelta(days=days_back)
            ).isoformat()

            rate = rates.get((currency, rate_date))

            if rate is not None:
                break

    if rate is None or rate <= 0:
        invalid_fx.append(line)
        continue

    # Le prix EUR a été arrondi avant conversion.
    price_eur = price_local * rate
    price_eur = price_eur.quantize(
        CENT,
        rounding=ROUND_HALF_UP
    )

    # Vérifier si la marge implicite est entre 15 % et 50 %.
    margin = (price_eur / unit_cost) - Decimal("1")

    if not (Decimal("0.15") <= margin <= Decimal("0.50")):
        invalid_margins.append(line)

print("Prix non positifs :", len(invalid_prices))
print("Marges hors intervalle :", len(invalid_margins))
print("Taux de change introuvables :", len(invalid_fx))
