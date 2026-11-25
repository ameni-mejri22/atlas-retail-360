
"""Génération de la source order_lines au format CSV."""

import json
import csv
from datetime import datetime, timedelta
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path
from zoneinfo import ZoneInfo

import pyarrow.parquet as pq

from src.store_config import STORES


MICRO_LINE_MIN = 1
MICRO_LINE_MAX = 5
LINE_ID_PREFIX = "L"

MARGIN_MIN = Decimal("0.15")
MARGIN_MAX = Decimal("0.50")

CENT = Decimal("0.01")


def load_product_catalog(product_path):
    """Charge les produits, leurs identifiants et leurs coûts."""

    table = pq.read_table(
        product_path,
        columns=[
            "product_id",
            "family_id",
            "label",
            "unit_cost",
            "cost_currency",
        ],
    )

    products = table.to_pylist()

    if not products:
        raise ValueError("Le catalogue produits est vide.")

    for product in products:
        if product["unit_cost"] is None:
            raise ValueError(
                f"Coût manquant pour {product['product_id']}"
            )

    print(f"Catalogue chargé : {len(products)} produits.")

    return products


def generate_unit_price(product, rng):
    """Calcule un prix de vente HT synthétique en EUR."""

    unit_cost = Decimal(str(product["unit_cost"]))

    margin = Decimal(
        str(round(rng.uniform(float(MARGIN_MIN), float(MARGIN_MAX)), 4))
    )

    unit_price = unit_cost * (Decimal("1") + margin)

    return unit_price.quantize(
        CENT,
        rounding=ROUND_HALF_UP,
    )


def convert_price_to_local_currency(
    price_eur,
    currency,
    target_date,
    rates,
):
    """Convertit un prix EUR vers la devise locale."""

    if currency == "EUR":
        return price_eur.quantize(
            CENT,
            rounding=ROUND_HALF_UP,
        )

    rate = get_fx_rate(currency, target_date, rates)

    if rate is None:
        raise ValueError(
            f"Taux de change introuvable pour {currency} le {target_date}"
        )

    local_price = price_eur / rate

    return local_price.quantize(
        CENT,
        rounding=ROUND_HALF_UP,
    )


def load_fx_rates(fx_path):
    """Charge les taux de change depuis le fichier CSV."""

    rates = {}

    with Path(fx_path).open(
        "r",
        encoding="utf-8",
        newline="",
    ) as file:
        reader = csv.DictReader(file)

        for row in reader:
            currency = row["currency"]
            rate_date = row["rate_date"]
            rate = Decimal(row["eur_per_unit"])

            rates[(currency, rate_date)] = rate

    print(f"Taux de change chargés : {len(rates)}")

    return rates


def load_opening_stock(opening_stock_path):
    """Charge le stock initial par produit et par magasin."""

    stock = {}

    with Path(opening_stock_path).open(
        "r",
        encoding="utf-8-sig",
        newline="",
    ) as file:
        reader = csv.DictReader(file)

        for row in reader:
            key = (row["product_id"], row["store_id"])

            if key in stock:
                raise ValueError(f"Stock initial dupliqué : {key}")

            quantity = int(row["opening_qty"])

            if quantity < 0:
                raise ValueError(f"Stock initial négatif : {key}")

            stock[key] = quantity

    if not stock:
        raise ValueError("Le fichier de stock initial est vide.")

    print(f"Stocks initiaux chargés : {len(stock)}")

    return stock


def get_fx_rate(currency, target_date, rates):
    """Retourne le dernier taux disponible, sans dépasser 7 jours."""

    if currency == "EUR":
        return Decimal("1.0")

    for days_back in range(8):
        rate_date = (
            target_date - timedelta(days=days_back)
        ).isoformat()

        rate = rates.get((currency, rate_date))

        if rate is not None:
            return rate

    return None


def load_orders(orders_path):
    """Charge les commandes depuis le fichier JSONL."""

    orders = []

    with Path(orders_path).open(
        "r",
        encoding="utf-8",
    ) as file:
        for line in file:
            if line.strip():
                orders.append(json.loads(line))

    print(f"Commandes chargées : {len(orders)}")

    return orders


def get_store_timezone(store_id):
    """Récupère le fuseau horaire d'une entité."""

    for store in STORES:
        if store["store_id"] == store_id:
            return store["timezone"]

    raise ValueError(f"Entité inconnue : {store_id}")


def generate_invoice_timestamp(order, rng):
    """Génère une date de facturation locale après la commande."""

    order_datetime = datetime.fromisoformat(order["order_ts"])

    timezone_name = get_store_timezone(order["store_id"])
    timezone = ZoneInfo(timezone_name)

    order_datetime = order_datetime.astimezone(timezone)

    invoice_datetime = order_datetime + timedelta(
        minutes=rng.randint(15, 180)
    )

    return invoice_datetime.isoformat()


def generate_line_quantities(order, rng):
    """Génère les quantités commandées et facturées."""

    qty_ordered = rng.randint(1, 10)

    if order["status"] == "INVOICED":
        qty_invoiced = rng.randint(1, qty_ordered)
    else:
        qty_invoiced = 0

    return qty_ordered, qty_invoiced


def generate_line_invoice_timestamp(order, qty_invoiced, rng):
    """Génère la date de facture uniquement pour une ligne facturée."""

    if qty_invoiced <= 0:
        return None

    return generate_invoice_timestamp(order, rng)


def generate_local_unit_price(product, order, target_date, rates, rng):
    """Génère le prix unitaire HT dans la devise de la commande."""

    price_eur = generate_unit_price(product, rng)

    currency = order["currency"]

    unit_price_ht = convert_price_to_local_currency(
        price_eur,
        currency,
        target_date,
        rates,
    )

    return unit_price_ht


def allocate_order_discount(order, lines):
    """Répartit la remise globale sur les lignes facturées."""

    # Réinitialiser les remises avant chaque nouvelle répartition.
    for line in lines:
        line["line_discount_ht"] = "0.00"

    order_discount = Decimal(order["order_discount"])

    if order_discount == Decimal("0.00"):
        return

    eligible_lines = [
        line for line in lines
        if int(line["qty_invoiced"]) > 0
        and not line["is_cancelled"]
    ]

    if not eligible_lines:
        raise ValueError(
            f"Allocation impossible : aucune ligne éligible "
            f"pour la commande {order['order_id']}"
        )

    # Calcul du montant brut de chaque ligne.
    gross_amounts = {
        line["line_id"]: (
            Decimal(line["qty_invoiced"])
            * Decimal(line["unit_price_ht"])
        )
        for line in eligible_lines
    }

    total_gross = sum(gross_amounts.values())

    if total_gross <= 0:
        raise ValueError(
            f"Montant brut invalide pour la commande {order['order_id']}"
        )

    if order_discount > total_gross:
        raise ValueError(
            f"Remise supérieure au montant brut pour "
            f"la commande {order['order_id']} : "
            f"{order_discount} > {total_gross}"
        )

    # Répartition proportionnelle avec arrondi à deux décimales.
    allocated_total = Decimal("0.00")

    for line in eligible_lines:
        gross = gross_amounts[line["line_id"]]

        discount = (
            gross * order_discount / total_gross
        ).quantize(CENT, rounding=ROUND_HALF_UP)

        line["line_discount_ht"] = str(discount)
        allocated_total += discount

    # Le résidu est affecté à la ligne ayant le plus grand montant brut.
    # En cas d'égalité, le plus petit line_id est retenu.
    residual = order_discount - allocated_total

    residual_line = min(
        eligible_lines,
        key=lambda line: (
            -gross_amounts[line["line_id"]],
            line["line_id"],
        ),
    )

    final_discount = (
        Decimal(residual_line["line_discount_ht"]) + residual
    )

    if final_discount < 0:
        raise ValueError(
            f"Remise négative après ajustement pour {order['order_id']}"
        )

    residual_line["line_discount_ht"] = str(
        final_discount.quantize(CENT)
    )

    # Vérification de la somme finale.
    final_total = sum(
        Decimal(line["line_discount_ht"])
        for line in eligible_lines
    )

    if final_total != order_discount:
        raise ValueError(
            f"Écart de remise pour {order['order_id']} : "
            f"{final_total} au lieu de {order_discount}"
        )



def generate_order_lines(order, products, rates, rng):
    """Génère les lignes d'une commande sans consommer le stock."""

    number_of_lines = rng.randint(
        MICRO_LINE_MIN,
        min(MICRO_LINE_MAX, len(products)),
    )

    selected_products = rng.sample(products, number_of_lines)

    lines = []

    for index, product in enumerate(selected_products, start=1):

        line_id = f"{LINE_ID_PREFIX}{index:03d}"

        qty_ordered, qty_invoiced = generate_line_quantities(
            order,
            rng,
        )

        invoice_ts = generate_line_invoice_timestamp(
            order,
            qty_invoiced,
            rng,
        )

        if invoice_ts is not None:
            target_date = datetime.fromisoformat(invoice_ts).date()
        else:
            target_date = datetime.fromisoformat(
                order["order_ts"]
            ).date()

        unit_price_ht = generate_local_unit_price(
            product,
            order,
            target_date,
            rates,
            rng,
        )

        updated_at = (
            invoice_ts
            if invoice_ts is not None
            else order["updated_at"]
        )

        line = {
            "order_id": order["order_id"],
            "line_id": line_id,
            "source_version": 1,
            "product_id": product["product_id"],
            "qty_ordered": qty_ordered,
            "qty_invoiced": qty_invoiced,
            "unit_price_ht": str(unit_price_ht),
            "line_discount_ht": "0.00",
            "invoice_ts": invoice_ts,
            "is_cancelled": False,
            "updated_at": updated_at,
        }

        lines.append(line)

    return lines



ORDER_LINE_FIELDS = [
    "order_id",
    "line_id",
    "source_version",
    "product_id",
    "qty_ordered",
    "qty_invoiced",
    "unit_price_ht",
    "line_discount_ht",
    "invoice_ts",
    "is_cancelled",
    "updated_at",
]


def save_order_lines(lines, output_path):
    """Enregistre les lignes de commande dans un fichier CSV."""

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with output_path.open(
        "w",
        encoding="utf-8",
        newline="",
    ) as file:
        writer = csv.DictWriter(
            file,
            fieldnames=ORDER_LINE_FIELDS,
        )

        writer.writeheader()
        writer.writerows(lines)

    print(f"Fichier order_lines généré : {output_path}")
    print(f"Nombre de lignes enregistrées : {len(lines)}")
