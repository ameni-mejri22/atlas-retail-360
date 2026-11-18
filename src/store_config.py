"""Configuration des 12 entités Atlas Retail."""

from datetime import date

STORES = [
    # France : 4 magasins + 1 centre logistique
    {
        "store_id": "ST001",
        "country": "FR",
        "timezone": "Europe/Paris",
        "opening_date": date(2024, 9, 1),
        "closing_date": None,
        "label": "Magasin Paris Centre",
    },
    {
        "store_id": "ST002",
        "country": "FR",
        "timezone": "Europe/Paris",
        "opening_date": date(2024, 9, 1),
        "closing_date": None,
        "label": "Magasin Lyon Part-Dieu",
    },
    {
        "store_id": "ST003",
        "country": "FR",
        "timezone": "Europe/Paris",
        "opening_date": date(2024, 9, 1),
        "closing_date": None,
        "label": "Magasin Marseille Centre",
    },
    {
        "store_id": "ST004",
        "country": "FR",
        "timezone": "Europe/Paris",
        "opening_date": date(2024, 9, 1),
        "closing_date": None,
        "label": "Magasin Lille Centre",
    },
    {
        "store_id": "ST005",
        "country": "FR",
        "timezone": "Europe/Paris",
        "opening_date": date(2024, 9, 1),
        "closing_date": None,
        "label": "Centre logistique Paris",
    },

    # Tunisie : 3 magasins + 1 centre logistique
    {
        "store_id": "ST006",
        "country": "TN",
        "timezone": "Africa/Tunis",
        "opening_date": date(2024, 9, 1),
        "closing_date": None,
        "label": "Magasin Tunis Centre",
    },
    {
        "store_id": "ST007",
        "country": "TN",
        "timezone": "Africa/Tunis",
        "opening_date": date(2024, 9, 1),
        "closing_date": None,
        "label": "Magasin Sousse Centre",
    },
    {
        "store_id": "ST008",
        "country": "TN",
        "timezone": "Africa/Tunis",
        "opening_date": date(2024, 9, 1),
        "closing_date": None,
        "label": "Magasin Sfax Centre",
    },
    {
        "store_id": "ST009",
        "country": "TN",
        "timezone": "Africa/Tunis",
        "opening_date": date(2024, 9, 1),
        "closing_date": None,
        "label": "Centre logistique Tunis",
    },

    # Suisse : 3 magasins
    {
        "store_id": "ST010",
        "country": "CH",
        "timezone": "Europe/Zurich",
        "opening_date": date(2024, 9, 1),
        "closing_date": None,
        "label": "Magasin Genève Centre",
    },
    {
        "store_id": "ST011",
        "country": "CH",
        "timezone": "Europe/Zurich",
        "opening_date": date(2024, 9, 1),
        "closing_date": None,
        "label": "Magasin Lausanne Centre",
    },
    {
        "store_id": "ST012",
        "country": "CH",
        "timezone": "Europe/Zurich",
        "opening_date": date(2024, 9, 1),
        "closing_date": None,
        "label": "Magasin Zurich Centre",
    },
]


def validate_stores():
    """Vérifie la cohérence de la configuration des entités."""

    assert len(STORES) == 12, "Il faut exactement 12 entités."

    store_ids = [store["store_id"] for store in STORES]
    assert len(store_ids) == len(set(store_ids)), "Identifiants en doublon."

    expected_countries = {"FR", "TN", "CH"}
    actual_countries = {store["country"] for store in STORES}
    assert actual_countries == expected_countries

    for store in STORES:
        assert store["opening_date"] is not None
        assert store["timezone"]
        assert store["label"]

    print("Configuration des entités valide : 12 entités.")