
import csv
from pathlib import Path
from decimal import Decimal

data_dir = Path("data/generated")

with (data_dir / "fx_rates.csv").open(
    encoding="utf-8",
    newline=""
) as f:
    rates = list(csv.DictReader(f))

invalid = [
    row for row in rates
    if Decimal(row["eur_per_unit"]) <= 0
]

duplicates = set()
seen = set()

for row in rates:
    key = (row["currency"], row["rate_date"])
    if key in seen:
        duplicates.add(key)
    seen.add(key)

print("Taux de change non positifs :", len(invalid))
print("Couples devise/date dupliqués :", len(duplicates))
print("Nombre total de taux :", len(rates))
