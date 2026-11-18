
"""Génération de la source product_versions au format Parquet."""

import random
from datetime import date, datetime
from decimal import Decimal
from pathlib import Path

import pyarrow as pa
import pyarrow.parquet as pq

from src.catalog_config import PRODUCT_FAMILIES, validate_product_families
from src.product_catalog_data import PRODUCTS_BY_FAMILY, validate_catalog_data


START_DATE = date(2024, 9, 1)


def generate_product_versions(seed=42):
    """Génère les 1 000 versions initiales du catalogue produits."""

    validate_product_families()
    validate_catalog_data()

    rng = random.Random(seed)
    rows = []

    for family in PRODUCT_FAMILIES:
        family_id = family["family_id"]
        product_count = family["product_count"]
        product_names = PRODUCTS_BY_FAMILY[family_id]

        if len(product_names) != product_count:
            raise ValueError(
                f"{family_id} : {product_count} produits attendus, "
                f"{len(product_names)} trouvés."
            )

        for number, product_name in enumerate(product_names, start=1):
            product_id = f"{family_id}-P{number:03d}"

            # Coût synthétique initial, généré de manière reproductible.
            cost = (
                Decimal(rng.randint(50, 10000)) / Decimal("100")
            )

            rows.append({
                "product_id": product_id,
                "effective_from": START_DATE,
                "family_id": family_id,
                "label": product_name,
                "unit_cost": cost,
                "cost_currency": "EUR",
                "effective_to": None,
                "updated_at": datetime(2024, 9, 1, 0, 0, 0),
            })

    if len(rows) != 1000:
        raise ValueError(
            f"Le catalogue doit contenir 1000 produits, "
            f"{len(rows)} générés."
        )

    return rows


def save_product_versions(rows, output_path):
    """Enregistre les versions dans un fichier Parquet."""

    schema = pa.schema([
        ("product_id", pa.string()),
        ("effective_from", pa.date32()),
        ("family_id", pa.string()),
        ("label", pa.string()),
        ("unit_cost", pa.decimal128(12, 2)),
        ("cost_currency", pa.string()),
        ("effective_to", pa.date32()),
        ("updated_at", pa.timestamp("us")),
    ])

    table = pa.Table.from_pylist(rows, schema=schema)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    pq.write_table(table, output_path)

    return table


def main():
    output_path = Path("data/generated/product_versions.parquet")

    rows = generate_product_versions(seed=42)
    table = save_product_versions(rows, output_path)

    print("Source product_versions générée avec succès.")
    print(f"Nombre de lignes : {table.num_rows}")
    print(f"Nombre de produits uniques : {len(set(row['product_id'] for row in rows))}")
    print(f"Fichier : {output_path}")


if __name__ == "__main__":
    main()
