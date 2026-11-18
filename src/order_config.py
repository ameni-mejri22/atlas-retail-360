"""Configuration de la génération des commandes Atlas Retail."""

ORDER_STATUSES = [
    "PENDING",
    "INVOICED",
    "CANCELLED",
]

SALES_CHANNELS = [
    "STORE",
    "WEB",
]

COUNTRY_CURRENCIES = {
    "FR": "EUR",
    "TN": "TND",
    "CH": "CHF",
}

# Répartition indicative des statuts pour les données synthétiques.
STATUS_PROBABILITIES = {
    "PENDING": 0.15,
    "INVOICED": 0.75,
    "CANCELLED": 0.10,
}


def validate_order_config():
    """Vérifie la cohérence de la configuration des commandes."""

    assert set(ORDER_STATUSES) == {
        "PENDING",
        "INVOICED",
        "CANCELLED",
    }

    assert set(SALES_CHANNELS) == {"STORE", "WEB"}

    assert COUNTRY_CURRENCIES == {
        "FR": "EUR",
        "TN": "TND",
        "CH": "CHF",
    }

    assert abs(sum(STATUS_PROBABILITIES.values()) - 1.0) < 0.000001

    print("Configuration des commandes valide.")