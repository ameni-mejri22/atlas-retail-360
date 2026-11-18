
"""Configuration du catalogue Atlas Retail 360."""

PRODUCT_FAMILIES = [
    {
        "family_id": "F01",
        "label": "Fruits et légumes",
        "product_count": 150,
    },
    {
        "family_id": "F02",
        "label": "Produits laitiers et œufs",
        "product_count": 150,
    },
    {
        "family_id": "F03",
        "label": "Épicerie et céréales",
        "product_count": 200,
    },
    {
        "family_id": "F04",
        "label": "Viandes et poissons",
        "product_count": 150,
    },
    {
        "family_id": "F05",
        "label": "Boissons",
        "product_count": 150,
    },
    {
        "family_id": "F06",
        "label": "Biscuits, confiseries et snacks",
        "product_count": 200,
    },
]


def validate_product_families():
    assert len(PRODUCT_FAMILIES) == 6
    assert sum(
        family["product_count"] for family in PRODUCT_FAMILIES
    ) == 1000
