
import csv
import json
from pathlib import Path
from decimal import Decimal, InvalidOperation

ORDERS_FILE = Path("data/generated/orders.jsonl")
LINES_FILE = Path("data/generated/order_lines.csv")


def check_order_discount_allocation():
    if not ORDERS_FILE.exists() or not LINES_FILE.exists():
        raise FileNotFoundError("Fichier orders ou order_lines introuvable.")

    with ORDERS_FILE.open("r", encoding="utf-8") as file:
        orders = {
            order["order_id"]: order
            for order in map(json.loads, file)
        }

    with LINES_FILE.open(
        "r", encoding="utf-8-sig", newline=""
    ) as file:
        lines = list(csv.DictReader(file))

    lines_by_order = {}
    for line in lines:
        lines_by_order.setdefault(line["order_id"], []).append(line)

    checked_orders = 0
    discount_mismatches = []
    unbilled_with_discount = []
    excessive_discounts = []
    invalid_values = []

    for order_id, order in orders.items():
        if order["status"] != "INVOICED":
            continue

        checked_orders += 1
        order_lines = lines_by_order.get(order_id, [])

        try:
            order_discount = Decimal(order["order_discount"])

            line_discount_total = Decimal("0.00")
            gross_total = Decimal("0.00")

            for line in order_lines:
                quantity = int(line["qty_invoiced"])
                price = Decimal(line["unit_price_ht"])
                discount = Decimal(line["line_discount_ht"])

                if quantity < 0 or price < 0 or discount < 0:
                    raise ValueError("Valeur négative")

                if quantity == 0 and discount != 0:
                    unbilled_with_discount.append(
                        (order_id, line["line_id"])
                    )

                if quantity > 0:
                    gross_total += Decimal(quantity) * price

                line_discount_total += discount

            if line_discount_total != order_discount:
                discount_mismatches.append(
                    (order_id, str(order_discount),
                     str(line_discount_total))
                )

            if order_discount > gross_total:
                excessive_discounts.append(
                    (order_id, str(order_discount), str(gross_total))
                )

        except (ValueError, InvalidOperation, KeyError) as error:
            invalid_values.append((order_id, str(error)))

    print("Commandes facturées vérifiées :", checked_orders)
    print("Écarts de répartition :", len(discount_mismatches))
    print("Lignes non facturées avec remise :", len(unbilled_with_discount))
    print("Remises supérieures au montant brut :", len(excessive_discounts))
    print("Valeurs invalides :", len(invalid_values))

    if any([
        discount_mismatches,
        unbilled_with_discount,
        excessive_discounts,
        invalid_values,
    ]):
        raise AssertionError(
            "Échec du contrôle de l'allocation des remises."
        )

    print("\nContrôle de l'allocation des remises : OK")


if __name__ == "__main__":
    check_order_discount_allocation()
