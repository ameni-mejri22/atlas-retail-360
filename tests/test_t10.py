
import json
import unittest
from datetime import date
from decimal import Decimal
from pathlib import Path


FIXTURE_PATH = Path(__file__).parent / "fixtures" / "t10_case.json"
MAX_FX_AGE_DAYS = 7


def value_invoice(invoice_date, currency, source_amount, rates):
    """Évalue une facture sans utiliser un taux futur ou trop ancien."""
    if currency == "EUR":
        return {
            "source_amount_preserved": Decimal(source_amount),
            "certified_sales_eur": Decimal(source_amount),
            "valuation_status": "valued",
            "reason": None,
        }

    invoice_day = date.fromisoformat(invoice_date)
    eligible_rates = []

    for rate in rates:
        rate_day = date.fromisoformat(rate["rate_date"])
        age_days = (invoice_day - rate_day).days

        if 0 <= age_days <= MAX_FX_AGE_DAYS:
            eligible_rates.append(rate)

    if not eligible_rates:
        return {
            "source_amount_preserved": Decimal(source_amount),
            "certified_sales_eur": None,
            "valuation_status": "pending",
            "reason": "no_eligible_fx_rate",
        }

    latest_rate = max(
        eligible_rates,
        key=lambda rate: rate["rate_date"],
    )

    eur_amount = (
        Decimal(source_amount) * Decimal(latest_rate["eur_chf"])
    ).quantize(Decimal("0.01"))

    return {
        "source_amount_preserved": Decimal(source_amount),
        "certified_sales_eur": eur_amount,
        "valuation_status": "valued",
        "reason": None,
    }


class TestT10(unittest.TestCase):

    def test_old_fx_rate_does_not_certify_eur_sales(self):
        with FIXTURE_PATH.open("r", encoding="utf-8") as file:
            case = json.load(file)

        inputs = case["input"]
        expected = case["expected"]

        actual = value_invoice(
            inputs["invoice_date"],
            inputs["currency"],
            inputs["source_amount"],
            inputs["available_fx_rates"],
        )

        self.assertEqual(
            actual["source_amount_preserved"],
            Decimal(expected["source_amount_preserved"]),
        )
        self.assertIsNone(expected["certified_sales_eur"])
        self.assertIsNone(actual["certified_sales_eur"])
        self.assertEqual(
            actual["valuation_status"],
            expected["valuation_status"],
        )
        self.assertEqual(actual["reason"], expected["reason"])


if __name__ == "__main__":
    unittest.main()
