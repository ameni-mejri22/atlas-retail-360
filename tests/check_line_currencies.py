
import csv
import json
from pathlib import Path

data_dir = Path("data/generated")

# Charger les commandes
with (data_dir / "orders.jsonl").open(encoding="utf-8") as f:
    orders = {
        order["order_id"]: order
        for line in f
        if line.strip()
        for order in [json.loads(line)]
    }

# Charger les magasins
with (data_dir / "stores.csv").open(
    encoding="utf-8",
    newline=""
) as f:
    stores = {
        row["store_id"]: row
        for row in csv.DictReader(f)
    }

expected_currency = {
    "FR": "EUR",
    "TN": "TND",
    "CH": "CHF",
}

invalid = []

for order in orders.values():
    store = stores[order["store_id"]]
    expected = expected_currency[store["country"]]

    if order["currency"] != expected:
        invalid.append(order)

print("Commandes avec devise incohérente :", len(invalid))
