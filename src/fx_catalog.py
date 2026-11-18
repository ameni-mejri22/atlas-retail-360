"""Génération de la source fx_rates au format CSV."""

import csv
import random
from datetime import date, datetime, timedelta
from decimal import Decimal
from pathlib import Path

START_DATE = date(2024, 9, 1)
END_DATE = date(2026, 8, 31)


def generate_fx_rates(seed=42):
    """Génère des taux de change synthétiques et reproductibles."""

    rng = random.Random(seed)
    rows = []

    current_date = START_DATE

    while current_date <= END_DATE:

        # Taux synthétiques : une unité de devise convertie en EUR
        chf_rate = Decimal(
            str(round(rng.uniform(0.95, 1.10), 5))
        )
        tnd_rate = Decimal(
            str(round(rng.uniform(0.28, 0.33), 5))
        )

        for currency, rate in [
            ("CHF", chf_rate),
            ("TND", tnd_rate),
        ]:
            rows.append({
                "currency": currency,
                "rate_date": current_date.isoformat(),
                "eur_per_unit": rate,
                "updated_at": datetime.combine(
                    current_date, datetime.min.time()
                ).isoformat(),
            })

        current_date += timedelta(days=1)

    return rows


def save_fx_rates(rows, output_path):
    """Enregistre les taux de change dans un fichier CSV."""

    columns = [
        "currency",
        "rate_date",
        "eur_per_unit",
        "updated_at",
    ]

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with output_path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=columns)
        writer.writeheader()

        for row in rows:
            writer.writerow({
                **row,
                "eur_per_unit": str(row["eur_per_unit"]),
            })

    print("Source fx_rates générée avec succès.")
    print(f"Nombre de lignes : {len(rows)}")
    print(f"Fichier : {output_path}")


def main():
    rows = generate_fx_rates(seed=42)
    save_fx_rates(rows, "data/generated/fx_rates.csv")


if __name__ == "__main__":
    main()