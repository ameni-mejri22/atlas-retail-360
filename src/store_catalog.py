"""Génération de la source stores au format CSV."""

import csv
from pathlib import Path

from src.store_config import STORES, validate_stores


def save_stores(output_path):
    """Enregistre les 12 entités dans un fichier CSV."""

    validate_stores()

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    columns = [
        "store_id",
        "country",
        "timezone",
        "opening_date",
        "closing_date",
        "label",
    ]

    with output_path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=columns)
        writer.writeheader()

        for store in STORES:
            row = store.copy()
            row["opening_date"] = row["opening_date"].isoformat()
            row["closing_date"] = (
                row["closing_date"].isoformat()
                if row["closing_date"] else ""
            )
            writer.writerow(row)

    print("Source stores générée avec succès.")
    print(f"Nombre d'entités : {len(STORES)}")
    print(f"Fichier : {output_path}")


if __name__ == "__main__":
    save_stores("data/generated/stores.csv")