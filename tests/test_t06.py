
import json
import unittest
from decimal import Decimal
from pathlib import Path


FIXTURE_PATH = Path(__file__).parent / "fixtures" / "t06_case.json"


def evaluate_line(line):
    if line["is_cancelled"]:
        return {
            "sales_ht": Decimal("0.00"),
            "cost": Decimal("0.00"),
            "consistency_anomaly": (
                Decimal(line["qty_invoiced"]) > 0
            ),
        }

    quantity = Decimal(line["qty_invoiced"])

    return {
        "sales_ht": quantity * Decimal(line["unit_price_ht"]),
        "cost": quantity * Decimal(line["unit_cost"]),
        "consistency_anomaly": False,
    }


class TestT06(unittest.TestCase):

    def test_cancelled_invoiced_line_is_excluded(self):
        with FIXTURE_PATH.open("r", encoding="utf-8") as file:
            case = json.load(file)

        actual = evaluate_line(case["input"])
        expected = case["expected"]

        self.assertEqual(
            actual["sales_ht"],
            Decimal(expected["sales_ht"]),
        )
        self.assertEqual(
            actual["cost"],
            Decimal(expected["cost"]),
        )
        self.assertEqual(
            actual["consistency_anomaly"],
            expected["consistency_anomaly"],
        )


if __name__ == "__main__":
    unittest.main()
