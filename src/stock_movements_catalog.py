
"""Génération des mouvements de stock liés aux ventes et aux retours."""

import csv
import json
from pathlib import Path


DATA_DIR = Path("data/generated")

ORDERS_FILE = DATA_DIR / "orders.jsonl"
ORDER_LINES_FILE = DATA_DIR / "order_lines.csv"
RETURNS_FILE = DATA_DIR / "returns.jsonl"
OUTPUT_FILE = DATA_DIR / "stock_movements.csv"


def load_jsonl(path):
    """Charge un fichier JSONL."""
    with path.open("r", encoding="utf-8") as file:
        return [json.loads(line) for line in file if line.strip()]


def load_csv(path):
    """Charge un fichier CSV."""
    with path.open("r", encoding="utf-8-sig", newline="") as file:
        return list(csv.DictReader(file))


def generate_stock_movements():
    """Construit les mouvements liés aux ventes et retours."""

    orders = load_jsonl(ORDERS_FILE)
    order_lines = load_csv(ORDER_LINES_FILE)
    returns = load_jsonl(RETURNS_FILE)

    orders_by_id = {order["order_id"]: order for order in orders}

    lines_by_key = {
        (line["order_id"], line["line_id"]): line
        for line in order_lines
    }

    movements = []

    # 1. Sorties de stock liées aux ventes facturées
    for line in order_lines:
        order = orders_by_id.get(line["order_id"])

        if order is None:
            continue

        qty_invoiced = int(line["qty_invoiced"])

        if (
            order["status"] != "INVOICED"
            or line["is_cancelled"] != "False"
            or qty_invoiced <= 0
        ):
            continue

        movement_ts = line["invoice_ts"]

        movements.append({
            "movement_id": f"MOV{len(movements) + 1:08d}",
            "source_version": 1,
            "product_id": line["product_id"],
            "store_id": order["store_id"],
            "movement_ts": movement_ts,
            "movement_type": "SALE",
            "qty_signed": -qty_invoiced,
            "related_order_id": order["order_id"],
            "related_return_id": "",
            "updated_at": line["updated_at"],
        })

    # 2. Entrées de stock liées aux retours remis en stock
    for returned in returns:
        if (
            returned["status"] != "ACCEPTED"
            or returned["restocked"] is not True
        ):
            continue

        order_id = returned["order_id"]
        line_id = returned["line_id"]

        order = orders_by_id.get(order_id)
        line = lines_by_key.get((order_id, line_id))

        if order is None or line is None:
            continue

        movement_ts = returned["return_ts"]

        movements.append({
            "movement_id": f"MOV{len(movements) + 1:08d}",
            "source_version": 1,
            "product_id": line["product_id"],
            "store_id": order["store_id"],
            "movement_ts": movement_ts,
            "movement_type": "CUSTOMER_RETURN",
            "qty_signed": int(returned["qty_returned"]),
            "related_order_id": order_id,
            "related_return_id": returned["return_id"],
            "updated_at": returned["updated_at"],
        })

    # Ordre chronologique
    movements.sort(
        key=lambda movement: (
            movement["movement_ts"],
            movement["movement_id"]
        )
    )

    return movements


def save_stock_movements(movements):
    """Enregistre les mouvements dans un fichier CSV."""

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

    fieldnames = [
        "movement_id",
        "source_version",
        "product_id",
        "store_id",
        "movement_ts",
        "movement_type",
        "qty_signed",
        "related_order_id",
        "related_return_id",
        "updated_at",
    ]

    with OUTPUT_FILE.open(
        "w",
        newline="",
        encoding="utf-8-sig"
    ) as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(movements)

    print(f"Mouvements générés : {len(movements)}")
    print(f"Fichier créé : {OUTPUT_FILE}")


if __name__ == "__main__":
    generated_movements = generate_stock_movements()
    save_stock_movements(generated_movements)
