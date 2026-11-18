import json
import unittest
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path


FIXTURE_PATH = Path(__file__).parent / "fixtures" / "t01_case.json"
CENT = Decimal("0.01")


def money(value):
    """Arrondit un montant à deux décimales."""
    return Decimal(value).quantize(CENT, rounding=ROUND_HALF_UP)


def calculate_t01(case):
    """Recalcule les montants du scénario T01."""
    inputs = case["input"]
    lines = inputs["lines"]
    order_discount = Decimal(inputs["order_discount"])

    bases = {}
    for line in lines:
        qty = Decimal(line["qty_invoiced"])
        price = Decimal(line["unit_price_ht"])
        line_discount = Decimal(line["line_discount_ht"])

        bases[line["line_id"]] = (
            qty * price - line_discount
        )

    total_base = sum(bases.values(), Decimal("0.00"))

    # Répartition proportionnelle de la remise globale.
    allocations = {}
    for line in lines:
        line_id = line["line_id"]
        allocation = money(
            order_discount * bases[line_id] / total_base
        )
        allocations[line_id] = allocation

    # Le reliquat va à la ligne ayant la base la plus élevée.
    # En cas d'égalité, on choisit le line_id lexicographiquement
    # le plus petit, conformément à la règle du projet.
    remainder = order_discount - sum(
        allocations.values(), Decimal("0.00")
    )

    if remainder != Decimal("0.00"):
        selected_line = min(
            lines,
            key=lambda line: (
                -bases[line["line_id"]],
                line["line_id"],
            ),
        )
        allocations[selected_line["line_id"]] += remainder

    results = []

    for line in lines:
        line_id = line["line_id"]
        qty = Decimal(line["qty_invoiced"])
        unit_cost = Decimal(line["unit_cost"])

        results.append({
            "line_id": line_id,
            "base_ht": money(bases[line_id]),
            "order_discount_allocation": money(
                allocations[line_id]
            ),
            "net_sales_ht": money(
                bases[line_id] - allocations[line_id]
            ),
            "cost": money(qty * unit_cost),
        })

    total_sales = sum(
        (line["net_sales_ht"] for line in results),
        Decimal("0.00"),
    )
    total_cost = sum(
        (line["cost"] for line in results),
        Decimal("0.00"),
    )

    return {
        "lines": results,
        "total_sales_ht": money(total_sales),
        "total_cost": money(total_cost),
        "gross_margin": money(total_sales - total_cost),
    }


class TestT01(unittest.TestCase):

    def test_global_discount(self):
        with FIXTURE_PATH.open("r", encoding="utf-8") as file:
            case = json.load(file)

        actual = calculate_t01(case)
        expected = case["expected"]

        self.assertEqual(
            actual["lines"],
            [
                {
                    "line_id": line["line_id"],
                    "base_ht": Decimal(line["base_ht"]),
                    "order_discount_allocation": Decimal(
                        line["order_discount_allocation"]
                    ),
                    "net_sales_ht": Decimal(line["net_sales_ht"]),
                    "cost": Decimal(line["cost"]),
                }
                for line in expected["lines"]
            ],
        )

        self.assertEqual(
            actual["total_sales_ht"],
            Decimal(expected["total_sales_ht"]),
        )
        self.assertEqual(
            actual["total_cost"],
            Decimal(expected["total_cost"]),
        )
        self.assertEqual(
            actual["gross_margin"],
            Decimal(expected["gross_margin"]),
        )


if __name__ == "__main__":
    unittest.main()
