
import csv
import json
from pathlib import Path
from datetime import datetime

data_dir = Path("data/generated")

# Charger les commandes
with (data_dir / "orders.jsonl").open(encoding="utf-8") as f:
    orders = {
        order["order_id"]: order
        for line in f
        if line.strip()
        for order in [json.loads(line)]
    }

# Charger les lignes de commande
with (data_dir / "order_lines.csv").open(
    encoding="utf-8",
    newline=""
) as f:
    lines = list(csv.DictReader(f))

invalid = []
before = []
naive = []

for row in lines:
    if not row["invoice_ts"]:
        continue

    try:
        invoice = datetime.fromisoformat(row["invoice_ts"])
        order = datetime.fromisoformat(
            orders[row["order_id"]]["order_ts"]
        )

        if invoice.tzinfo is None:
            naive.append(row)
        elif order.tzinfo is None:
            naive.append(row)
        elif invoice < order:
            before.append(row)

    except ValueError:
        invalid.append(row)

print("Dates de facture invalides :", len(invalid))
print("Dates sans fuseau horaire :", len(naive))
print("Factures antérieures aux commandes :", len(before))
