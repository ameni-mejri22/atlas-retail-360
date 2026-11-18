"""Génération de la source order_lines au format CSV."""
import json
import csv
import random
from datetime import datetime, timedelta
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path

import pyarrow.parquet as pq

from src.store_config import STORES

MICRO_LINE_MIN = 1
MICRO_LINE_MAX = 5

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
        str(round(rng.uniform(0.15, 0.50), 4))
    )

    unit_price = unit_cost * (Decimal("1") + margin)

    return unit_price.quantize(
        CENT,
        rounding=ROUND_HALF_UP,
    )
    
def convert_price_to_local_currency(price_eur, currency, target_date, rates):
    """Convertit un prix EUR vers la devise locale."""
    if currency == "EUR":
        return price_eur.quantize(CENT, rounding=ROUND_HALF_UP)

    rate = get_fx_rate(currency, target_date, rates)

    if rate is None:
        raise ValueError(
            f"Taux de change introuvable pour {currency} le {target_date}"
        )

    local_price = price_eur / rate

    return local_price.quantize(CENT, rounding=ROUND_HALF_UP)    
    
       
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

    from zoneinfo import ZoneInfo
    timezone = ZoneInfo(timezone_name)

    order_datetime = order_datetime.astimezone(timezone)

    invoice_datetime = order_datetime + timedelta(
        minutes=rng.randint(15, 180)
    )

    return invoice_datetime.isoformat()