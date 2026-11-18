
import json
import unittest
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path


FIXTURE_PATH = Path(__file__).parent / "fixtures" / "t08_case.json"
CENT = Decimal("0.01")


def money(value):
    return Decimal(value).quantize(CENT, rounding=ROUND_HALF_UP)


def calculate_budget_achievement(sales, budget):
    total_sales = sum(
        (Decimal(value) for value in sales),
        Decimal("0.00"),
    )

    if budget <= 0:
        raise ValueError("Le budget doit être positif.")

    achievement = money(total_sales / budget * Decimal("100"))

    return total_sales, achievement


class TestT08(unittest.TestCase):

    def test_budget_achievement(self):
        with FIXTURE_PATH.open("r", encoding="utf-8") as file:
            case = json.load(file)

        inputs = case["input"]
        expected = case["expected"]

        total_sales, achievement = calculate_budget_achievement(
            inputs["sales"],
            Decimal(inputs["budget"]),
        )

        self.assertEqual(
            total_sales,
            Decimal(expected["total_sales_ht"]),
        )
        self.assertEqual(
            Decimal(inputs["budget"]),
            Decimal(expected["budget"]),
        )
        self.assertEqual(
            achievement,
            Decimal(expected["budget_achievement_pct"]),
        )


if __name__ == "__main__":
    unittest.main()
