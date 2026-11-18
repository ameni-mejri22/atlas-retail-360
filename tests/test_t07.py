
import json
import unittest
from decimal import Decimal
from pathlib import Path


FIXTURE_PATH = Path(__file__).parent / "fixtures" / "t07_case.json"


def resolve_current_state(events):
    """Conserve l'état correspondant à la version source la plus élevée."""
    if not events:
        return None

    return max(events, key=lambda event: event["source_version"])


class TestT07(unittest.TestCase):

    def test_late_older_cdc_event_does_not_replace_newer_version(self):
        with FIXTURE_PATH.open("r", encoding="utf-8") as file:
            case = json.load(file)

        events = case["input"]["events"]
        expected = case["expected"]

        current = resolve_current_state(events)

        self.assertIsNotNone(current)
        self.assertEqual(
            current["source_version"],
            expected["current_source_version"],
        )
        self.assertEqual(
            Decimal(current["price"]),
            Decimal(expected["current_price"]),
        )

        # Une seule entité métier est représentée par la clé K.
        business_line_count = len({case["input"]["entity_key"]})
        self.assertEqual(
            business_line_count,
            expected["business_line_count"],
        )


if __name__ == "__main__":
    unittest.main()
