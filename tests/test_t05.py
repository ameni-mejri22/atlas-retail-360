
import json
import unittest
from pathlib import Path


FIXTURE_PATH = Path(__file__).parent / "fixtures" / "t05_case.json"


def apply_movements(stock, movements, applied_ids):
    """Applique chaque mouvement de test une seule fois."""
    for movement in movements:
        movement_id = movement["movement_id"]

        if movement_id in applied_ids:
            continue

        stock += movement["quantity"]
        applied_ids.add(movement_id)

    return stock


class TestT05(unittest.TestCase):

    def test_stock_and_idempotent_replay(self):
        with FIXTURE_PATH.open("r", encoding="utf-8") as file:
            case = json.load(file)

        inputs = case["input"]
        expected = case["expected"]

        stock = inputs["opening_stock"]
        applied_ids = set()
        movements = inputs["movements"]

        # Première application des mouvements.
        stock = apply_movements(stock, movements, applied_ids)

        self.assertEqual(
            stock,
            expected["stock_after_first_application"],
        )

        # Rejeu des mêmes mouvements : aucun effet supplémentaire.
        stock = apply_movements(stock, movements, applied_ids)

        self.assertEqual(
            stock,
            expected["stock_after_replay"],
        )


if __name__ == "__main__":
    unittest.main()
