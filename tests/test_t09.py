
import json
import unittest
from datetime import date
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path


FIXTURE_PATH = Path(__file__).parent / "fixtures" / "t09_case.json"
CENT = Decimal("0.01")


def money(value):
    return Decimal(value).quantize(CENT, rounding=ROUND_HALF_UP)


def select_cost_version(sale_date, versions):
    matches = []

    for version in versions:
        start = date.fromisoformat(version["effective_from"])
        end = (
            date.fromisoformat(version["effective_to"])
            if version["effective_to"] is not None
            else None
        )

        if start <= sale_date and (end is None or sale_date < end):
            matches.append(version)

    if len(matches) != 1:
        raise ValueError(
            f"Une seule version de coût est attendue, trouvé : {len(matches)}"
        )

    return matches[0]


class TestT09(unittest.TestCase):

    def test_cost_version_on_effective_date(self):
        with FIXTURE_PATH.open("r", encoding="utf-8") as file:
            case = json.load(file)

        inputs = case["input"]
        expected = case["expected"]

        sale_date = date.fromisoformat(inputs["sale_date"])
        quantity = Decimal(inputs["quantity"])
        unit_price = Decimal(inputs["unit_price_ht"])

        selected = select_cost_version(
            sale_date,
            inputs["cost_versions"],
        )

        unit_cost = Decimal(selected["unit_cost"])
        sales = money(quantity * unit_price)
        cost = money(quantity * unit_cost)
        margin = money(sales - cost)

        self.assertEqual(
            unit_cost,
            Decimal(expected["selected_unit_cost"]),
        )
        self.assertEqual(
            1,
            expected["matched_cost_versions"],
        )
        self.assertEqual(sales, Decimal(expected["sales_ht"]))
        self.assertEqual(cost, Decimal(expected["cost"]))
        self.assertEqual(margin, Decimal(expected["gross_margin"]))


if __name__ == "__main__":
    unittest.main()
