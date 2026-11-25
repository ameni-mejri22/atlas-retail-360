
"""Génération de la source des retours clients."""

import csv
import json
import random
from datetime import datetime, timedelta
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path

from src.customer_config import END_DATE



CENT = Decimal("0.01")

# Proportion de lignes éligibles qui auront un retour.
RETURN_PROBABILITY = 0.15

# Pourcentage maximal de la quantité facturée pouvant être retournée.
MAX_RETURN_RATIO = 1.0


def load_orders(orders_path):
    """Charge les commandes et les indexe par order_id."""

    orders = {}

    with open(orders_path, encoding="utf-8") as file:
        for line in file:
            order = json.loads(line)
            orders[order["order_id"]] = order

    return orders


def load_order_lines(order_lines_path):
    """Charge les lignes de commande."""

    with open(
        order_lines_path,
        encoding="utf-8-sig",
        newline="",
    ) as file:
        return list(csv.DictReader(file))


def generate_return_timestamp(invoice_ts, rng):
    """Génère une date de retour après la facturation."""

    invoice_datetime = datetime.fromisoformat(invoice_ts)

    max_return_datetime = datetime(
        END_DATE.year,
        END_DATE.month,
        END_DATE.day,
        23,
        59,
        59,
        tzinfo=invoice_datetime.tzinfo,
    )

    available_seconds = int(
        (max_return_datetime - invoice_datetime).total_seconds()
    )

    if available_seconds <= 0:
        return None

    # Retour entre 1 et 90 jours après la facturation,
    # sans dépasser la fin de la période du projet.
    max_days = min(90, available_seconds // 86400)

    if max_days < 1:
        return None

    days_after = rng.randint(1, max_days)

    return_datetime = invoice_datetime + timedelta(
        days=days_after,
        hours=rng.randint(0, 23),
        minutes=rng.randint(0, 59),
    )

    if return_datetime > max_return_datetime:
        return_datetime = max_return_datetime

    return return_datetime


def calculate_refund(line, qty_returned):
    """Calcule le remboursement proportionnel au montant net."""

    qty_invoiced = int(line["qty_invoiced"])

    unit_price = Decimal(line["unit_price_ht"])
    line_discount = Decimal(line["line_discount_ht"])

    gross_amount = unit_price * qty_invoiced
    net_amount = gross_amount - line_discount

    refund = (
        net_amount * Decimal(qty_returned) / Decimal(qty_invoiced)
    ).quantize(CENT, rounding=ROUND_HALF_UP)

    return refund


def generate_returns(
    seed=42,
    orders_path="data/generated/orders.jsonl",
    order_lines_path="data/generated/order_lines.csv",
):
    """Génère les retours à partir des commandes et des lignes."""

    rng = random.Random(seed)

    orders = load_orders(orders_path)
    order_lines = load_order_lines(order_lines_path)

    returns = []

    for line in order_lines:

        order = orders.get(line["order_id"])

        if order is None:
            continue

        # Seules les lignes facturées et non annulées sont éligibles.
        if order["status"] != "INVOICED":
            continue

        if line["is_cancelled"].lower() == "true":
            continue

        qty_invoiced = int(line["qty_invoiced"])

        if qty_invoiced <= 0:
            continue

        invoice_ts = line["invoice_ts"]

        if not invoice_ts:
            continue

        # Toutes les lignes ne donnent pas nécessairement lieu à un retour.
        if rng.random() > RETURN_PROBABILITY:
            continue

        return_datetime = generate_return_timestamp(
            invoice_ts,
            rng,
        )

        if return_datetime is None:
            continue

        qty_returned = rng.randint(1, qty_invoiced)

        refund_ht = calculate_refund(
            line,
            qty_returned,
        )

        if refund_ht <= Decimal("0.00"):
            continue

        return_number = len(returns) + 1

        updated_at = return_datetime + timedelta(
            minutes=rng.randint(1, 60)
        )

        restocked = rng.choice([True, False])

        returns.append({
            "return_id": f"RET{return_number:06d}",
            "source_version": 1,
            "order_id": line["order_id"],
            "line_id": line["line_id"],
            "return_ts": return_datetime.isoformat(),
            "qty_returned": qty_returned,
            "refund_ht": str(refund_ht),
            "restocked": restocked,
            "status": "ACCEPTED",
            "updated_at": updated_at.isoformat(),
        })

    return returns


def save_returns(
    returns,
    output_path="data/generated/returns.jsonl",
):
    """Enregistre les retours au format JSONL."""

    path = Path(output_path)
    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with open(path, "w", encoding="utf-8") as file:
        for return_record in returns:
            file.write(
                json.dumps(
                    return_record,
                    ensure_ascii=False,
                ) + "\n"
            )

    print(f"Retours générés : {len(returns)}")
    print(f"Fichier créé : {path}")


if __name__ == "__main__":
    
    generated_returns = generate_returns(seed=42)

    save_returns(generated_returns)