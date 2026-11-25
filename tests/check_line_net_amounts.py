
import csv
from pathlib import Path
from decimal import Decimal, InvalidOperation

DATA_FILE = Path("data/generated/order_lines.csv")


def check_line_net_amounts():
    if not DATA_FILE.exists():
        raise FileNotFoundError(f"Fichier introuvable : {DATA_FILE}")

    total = 0
    negative_net = []
    excessive_discount = []
    negative_discount = []
    invalid_values = []
    zero_quantity_nonzero_net = []

    with DATA_FILE.open(
        "r",
        encoding="utf-8-sig",
        newline=""
    ) as file:
        reader = csv.DictReader(file)

        required_columns = {
            "order_id",
            "line_id",
            "qty_invoiced",
            "unit_price_ht",
            "line_discount_ht",
        }

        missing = required_columns - set(reader.fieldnames or [])
        if missing:
            raise ValueError(f"Colonnes manquantes : {missing}")

        for row in reader:
            total += 1

            try:
                quantity = int(row["qty_invoiced"])
                unit_price = Decimal(row["unit_price_ht"])
                discount = Decimal(row["line_discount_ht"])

                gross = Decimal(quantity) * unit_price
                net = gross - discount

                if quantity < 0 or unit_price < 0:
                    invalid_values.append(row)

                if discount < 0:
                    negative_discount.append(row)

                if discount > gross:
                    excessive_discount.append(row)

                if net < 0:
                    negative_net.append(row)

                if quantity == 0 and net != 0:
                    zero_quantity_nonzero_net.append(row)

            except (ValueError, InvalidOperation):
                invalid_values.append(row)

    print("Lignes vérifiées :", total)
    print("Montants nets négatifs :", len(negative_net))
    print("Remises supérieures au montant brut :", len(excessive_discount))
    print("Remises négatives :", len(negative_discount))
    print("Lignes avec quantité nulle et montant net non nul :",
          len(zero_quantity_nonzero_net))
    print("Valeurs invalides :", len(invalid_values))

    if any([
        negative_net,
        excessive_discount,
        negative_discount,
        zero_quantity_nonzero_net,
        invalid_values,
    ]):
        raise AssertionError("Échec du contrôle des montants nets.")

    print("\nContrôle des montants nets : OK")


if __name__ == "__main__":
    check_line_net_amounts()
