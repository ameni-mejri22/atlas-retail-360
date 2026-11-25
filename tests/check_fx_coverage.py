
import csv
from pathlib import Path
from datetime import date, timedelta

data_dir = Path("data/generated")

with (data_dir / "fx_rates.csv").open(
    encoding="utf-8",
    newline=""
) as f:
    rows = list(csv.DictReader(f))

expected_start = date(2024, 9, 1)
expected_end = date(2026, 8, 31)

for currency in ("CHF", "TND"):
    dates = {
        date.fromisoformat(row["rate_date"])
        for row in rows
        if row["currency"] == currency
    }

    expected_dates = set()
    current = expected_start

    while current <= expected_end:
        expected_dates.add(current)
        current += timedelta(days=1)

    missing = expected_dates - dates
    unexpected = dates - expected_dates

    print(f"\nDevise : {currency}")
    print("Nombre de dates :", len(dates))
    print("Dates manquantes :", len(missing))
    print("Dates inattendues :", len(unexpected))
