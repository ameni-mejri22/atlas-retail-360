
"""Génération des sources CRM et de l'historique des segments clients."""

import csv
import json
import random
from datetime import datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

from src.customer_config import (
    START_DATE,
    END_DATE,
    CUSTOMER_COUNT,
    CUSTOMER_ID_PREFIX,
    COUNTRIES,
    COUNTRY_TIMEZONES,
    CUSTOMER_SEGMENTS,
    DEFAULT_SEED,
)

from src.store_config import STORES


def load_customer_data(orders_path):
    """
    Récupère le premier magasin et la première date de commande
    associés à chaque client.
    """
    customer_stores = {}
    first_order_dates = {}

    with open(orders_path, encoding="utf-8") as file:
        for line in file:
            order = json.loads(line)

            customer_id = order["customer_id"]
            store_id = order["store_id"]
            order_date = datetime.fromisoformat(
                order["order_ts"]
            ).date()

            if customer_id not in customer_stores:
                customer_stores[customer_id] = store_id

            if (
                customer_id not in first_order_dates
                or order_date < first_order_dates[customer_id]
            ):
                first_order_dates[customer_id] = order_date

    return customer_stores, first_order_dates


def generate_crm_customers(
    seed=DEFAULT_SEED,
    orders_path="data/generated/orders.jsonl",
):
    """Génère les clients CRM et leurs événements de segment."""

    rng = random.Random(seed)

    # Association magasin / pays
    store_countries = {
        store["store_id"]: store["country"]
        for store in STORES
    }

    # Lecture des commandes une seule fois
    customer_stores, first_order_dates = load_customer_data(
        orders_path
    )

    # Pays de rattachement des clients déjà présents dans les commandes
    customer_countries = {
        customer_id: store_countries[store_id]
        for customer_id, store_id in customer_stores.items()
    }

    customers = []
    events = []

    for number in range(1, CUSTOMER_COUNT + 1):

        customer_id = (
            f"{CUSTOMER_ID_PREFIX}{number:06d}"
        )

        # Pays du client
        country = customer_countries.get(customer_id)

        if country is None:
            country = rng.choice(COUNTRIES)

        timezone = ZoneInfo(COUNTRY_TIMEZONES[country])

        # Date d'inscription antérieure à la première commande
        first_order_date = first_order_dates.get(customer_id)

        if first_order_date is not None:
            max_days = (first_order_date - START_DATE).days
        else:
            max_days = (END_DATE - START_DATE).days

        signup_date = START_DATE + timedelta(
            days=rng.randint(0, max_days)
        )

        # Premier segment attribué à l'inscription
        current_segment = rng.choice(CUSTOMER_SEGMENTS)

        # Entre 1 et 3 événements par client
        event_count = rng.randint(1, 3)

        possible_days = (END_DATE - signup_date).days
        event_days = {0}

        for _ in range(event_count - 1):
            if possible_days > 0:
                event_days.add(
                    rng.randint(1, possible_days)
                )

        sorted_days = sorted(event_days)

        customer_events = []

        for version, day_offset in enumerate(
            sorted_days,
            start=1,
        ):

            effective_date = signup_date + timedelta(
                days=day_offset
            )

            # Changement de segment
            if version > 1:
                available_segments = [
                    segment
                    for segment in CUSTOMER_SEGMENTS
                    if segment != current_segment
                ]

                current_segment = rng.choice(
                    available_segments
                )

            effective_from = datetime(
                effective_date.year,
                effective_date.month,
                effective_date.day,
                rng.randint(8, 18),
                rng.randint(0, 59),
                tzinfo=timezone,
            )

            recorded_at = effective_from + timedelta(
                minutes=rng.randint(0, 120)
            )

            event = {
                "event_id": (
                    f"EVT-{customer_id}-{version:03d}"
                ),
                "customer_id": customer_id,
                "segment": current_segment,
                "effective_from": effective_from.isoformat(),
                "source_version": version,
                "recorded_at": recorded_at.isoformat(),
            }

            customer_events.append(event)

        events.extend(customer_events)

        # Le CRM contient le dernier segment connu
        latest_event = customer_events[-1]

        customers.append({
            "customer_id": customer_id,
            "country": country,
            "segment": latest_event["segment"],
            "signup_date": signup_date.isoformat(),
            "email_synthetic": (
                f"{customer_id.lower()}@example.test"
            ),
            "updated_at": latest_event["recorded_at"],
        })

    return customers, events


def save_crm_sources(
    customers,
    events,
    output_dir="data/generated",
):
    """Enregistre les deux sources CRM."""

    output_path = Path(output_dir)
    output_path.mkdir(
        parents=True,
        exist_ok=True,
    )

    # Enregistrement du CRM
    customers_path = output_path / "crm_customers.csv"

    with open(
        customers_path,
        "w",
        encoding="utf-8-sig",
        newline="",
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=[
                "customer_id",
                "country",
                "segment",
                "signup_date",
                "email_synthetic",
                "updated_at",
            ],
        )

        writer.writeheader()
        writer.writerows(customers)

    # Enregistrement de l'historique des segments
    events_path = (
        output_path / "customer_segment_events.jsonl"
    )

    with open(
        events_path,
        "w",
        encoding="utf-8",
    ) as file:

        for event in events:
            file.write(
                json.dumps(event, ensure_ascii=False) + "\n"
            )

    print(f"Clients CRM générés : {len(customers)}")
    print(f"Événements de segment générés : {len(events)}")
    print(f"Fichier créé : {customers_path}")
    print(f"Fichier créé : {events_path}")


if __name__ == "__main__":

    generated_customers, generated_events = generate_crm_customers()

    save_crm_sources(
        generated_customers,
        generated_events,
    )
