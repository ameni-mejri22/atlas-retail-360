import json
import unittest
from decimal import Decimal
from pathlib import Path

from test_t01 import calculate_t01


FIXTURE_PATH = Path(__file__).parent / "fixtures" / "t02_case.json"


class TestT02(unittest.TestCase):

    def test_accepted_return_restocked(self):
        with FIXTURE_PATH.open("r", encoding="utf-8") as file:
            case = json.load(file)

        sales = calculate_t01(case)
        returned = case["input"]["return"]
        expected = case["expected"]

        # Coût unitaire de L1 issu du scénario de vente.
        line_l1 = next(
            line for line in case["input"]["lines"]
            if line["line_id"] == returned["line_id"]
        )
        returned_cost = (
            Decimal(returned["qty_returned"])
            * Decimal(line_l1["unit_cost"])
        )

        refund = Decimal(returned["refund_ht"])

        net_sales = sales["total_sales_ht"] - refund

        net_cost = sales["total_cost"]
        if returned["restocked"]:
            net_cost -= returned_cost

        margin = net_sales - net_cost

        self.assertEqual(
            -refund,
            Decimal(expected["return_sales_impact"]),
        )
        self.assertEqual(
            -returned_cost,
            Decimal(expected["return_cost_impact"]),
        )
        self.assertEqual(
            -refund + returned_cost,
            Decimal(expected["return_margin_impact"]),
        )
        self.assertEqual(
            net_sales,
            Decimal(expected["total_sales_ht"]),
        )
        self.assertEqual(
            net_cost,
            Decimal(expected["net_cost"]),
        )
        self.assertEqual(
            margin,
            Decimal(expected["gross_margin"]),
        )


if __name__ == "__main__":
    unittest.main()
