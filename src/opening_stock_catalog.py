
"""Génération du stock initial par produit et par magasin."""

import csv
import random
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import pyarrow.parquet as pq

from src.store_config import STORES


PRODUCTS_FILE = Path("data/generated/product_versions.parquet")
OUTPUT_FILE = Path("data/generated/opening_stock.csv")

OPENING_DATE = "2024-08-31"

FAMILY_STOCK_RANGES = {
    "F01": (5, 25),
    "F02": (5, 20),
    "F03": (10, 40),
    "F04": (3, 15),
    "F05": (5, 30),
    "F06": (5, 25),
}


def generate_opening_stock(seed=42):
    """Génère une quantité initiale pour chaque produit et magasin."""

    rng = random.Random(seed)

    table = pq.read_table(
        PRODUCTS_FILE,
        columns=["product_id", "family_id"]
    )
    products = table.to_pylist()

    rows = []

    for store in STORES:
        store_id = store["store_id"]
        timezone = ZoneInfo(store["timezone"])

        opening_ts = datetime(
            2024, 8, 31, 23, 59, 59,
            tzinfo=timezone
        ).isoformat()

        for product in products:
            product_id = product["product_id"]
            family_id = product["family_id"]

            min_qty, max_qty = FAMILY_STOCK_RANGES[family_id]
            opening_qty = rng.randint(min_qty, max_qty)

            rows.append({
                "product_id": product_id,
                "store_id": store_id,
                "opening_qty": opening_qty,
                "opening_ts": opening_ts,
            })

    return rows


def save_opening_stock(rows):
    """Enregistre le stock initial au format CSV."""

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

    fieldnames = [
        "product_id",
        "store_id",
        "opening_qty",
        "opening_ts",
    ]

    with OUTPUT_FILE.open(
        "w",
        newline="",
        encoding="utf-8-sig"
    ) as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"Stocks initiaux générés : {len(rows)}")
    print(f"Fichier créé : {OUTPUT_FILE}")


if __name__ == "__main__":
    opening_stock_rows = generate_opening_stock(seed=42)
    save_opening_stock(opening_stock_rows)
