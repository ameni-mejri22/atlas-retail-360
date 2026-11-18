
import json
import unittest
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path


FIXTURE_PATH = Path(__file__).parent / "fixtures" / "t04_case.json"
CENT = Decimal("0.01")


def money(value):
    return Decimal(value).quantize(CENT, rounding=ROUND_HALF_UP)


class TestT04(unittest.TestCase):

    def test_chf_to_eur_conversion(self):
        with FIXTURE_PATH.open("r", encoding="utf-8") as file:
            case = json.load(file)

        inputs = case["input"]
        expected = case["expected"]

        rate = Decimal(inputs["fx_rate_eur_chf"])
        sales_eur = money(Decimal(inputs["sales_ht"]) * rate)
        cost_eur = money(Decimal(inputs["cost"]) * rate)
        margin_eur = money(sales_eur - cost_eur)

        self.assertEqual(sales_eur, Decimal(expected["sales_eur"]))
        self.assertEqual(cost_eur, Decimal(expected["cost_eur"]))
        self.assertEqual(
            margin_eur,
            Decimal(expected["gross_margin_eur"]),
        )


if __name__ == "__main__":
    unittest.main()
