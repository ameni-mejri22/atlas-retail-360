"""Génération de la source orders au format JSONL."""

import json
import random
from datetime import date, datetime, time, timedelta
from decimal import Decimal
from pathlib import Path
from zoneinfo import ZoneInfo

from src.store_config import STORES
from src.order_config import (
    COUNTRY_CURRENCIES,
    STATUS_PROBABILITIES,
    validate_order_config,
)

START_DATE = date(2024, 9, 1)
END_DATE = date(2026, 8, 31)

MICRO_ORDER_COUNT = 100


def generate_orders(seed=42, count=MICRO_ORDER_COUNT):
    """Génère des commandes synthétiques et reproductibles."""

    validate_order_config()

    rng = random.Random(seed)
    rows = []

    statuses = list(STATUS_PROBABILITIES.keys())
    probabilities = list(STATUS_PROBABILITIES.values())

    total_days = (END_DATE - START_DATE).days

    for number in range(1, count + 1):

        # Choisir une entité responsable
        store = rng.choice(STORES)
        country = store["country"]

        # Déterminer la devise selon le pays
        currency = COUNTRY_CURRENCIES[country]

        # Générer une date et une heure locales
        order_date = START_DATE + timedelta(
            days=rng.randint(0, total_days)
        )

        order_time = time(
            hour=rng.randint(9, 20),
            minute=rng.choice([0, 15, 30, 45]),
        )

        timezone = ZoneInfo(store["timezone"])

        order_datetime = datetime.combine(
            order_date,
            order_time,
            tzinfo=timezone,
        )

        updated_at = order_datetime + timedelta(minutes=5)

        # Choisir le canal et le statut
        channel = rng.choice(["STORE", "WEB"])

        status = rng.choices(
            statuses,
            weights=probabilities,
            k=1,
        )[0]

        # Générer une remise globale
        discount = Decimal(
            str(rng.choice([0, 0, 0, 5, 10, 15]))
        ).quantize(Decimal("0.01"))

        row = {
            "order_id": f"ORD{number:06d}",
            "source_version": 1,
            "customer_id": f"C{rng.randint(1, 6000):06d}",
            "store_id": store["store_id"],
            "channel": channel,
            "order_ts": order_datetime.isoformat(),
            "status": status,
            "currency": currency,
            "campaign_id": None,
            "order_discount": str(discount),
            "updated_at": updated_at.isoformat(),
        }

        rows.append(row)

    return rows


def save_orders(rows, output_path):
    """Enregistre les commandes dans un fichier JSONL."""

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with output_path.open("w", encoding="utf-8") as file:
        for row in rows:
            file.write(
                json.dumps(row, ensure_ascii=False) + "\n"
            )

    print("Source orders générée avec succès.")
    print(f"Nombre de commandes : {len(rows)}")
    print(f"Fichier : {output_path}")


def main():
    rows = generate_orders(seed=42)
    save_orders(rows, "data/generated/orders.jsonl")


if __name__ == "__main__":
    main()