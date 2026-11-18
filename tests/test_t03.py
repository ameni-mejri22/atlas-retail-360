
import json
import unittest
from decimal import Decimal
from pathlib import Path

from test_t01 import calculate_t01


FIXTURE_PATH = Path(__file__).parent / "fixtures" / "t03_case.json"


class TestT03(unittest.TestCase):

    def test_accepted_return_not_restocked(self):
        with FIXTURE_PATH.open("r", encoding="utf-8") as file:
            case = json.load(file)

        sales = calculate_t01(case)
        returned = case["input"]["return"]
        expected = case["expected"]

        refund = Decimal(returned["refund_ht"])

        line = next(
            item for item in case["input"]["lines"]
            if item["line_id"] == returned["line_id"]
        )

        returned_cost = (
            Decimal(returned["qty_returned"])
            * Decimal(line["unit_cost"])
        )

        net_sales = sales["total_sales_ht"] - refund

        net_cost = sales["total_cost"]
        cost_impact = Decimal("0.00")

        if returned["restocked"]:
            net_cost -= returned_cost
            cost_impact = -returned_cost

        margin = net_sales - net_cost
        margin_impact = -refund - cost_impact

        self.assertEqual(
            -refund,
            Decimal(expected["return_sales_impact"]),
        )
        self.assertEqual(
            cost_impact,
            Decimal(expected["return_cost_impact"]),
        )
        self.assertEqual(
            margin_impact,
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
