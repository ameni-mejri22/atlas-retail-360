
"""Configuration de la génération des données clients."""

from datetime import date

# Période du projet
START_DATE = date(2024, 9, 1)
END_DATE = date(2026, 8, 31)

# Population CRM
CUSTOMER_COUNT = 6000
CUSTOMER_ID_PREFIX = "C"

# Pays et fuseaux horaires
COUNTRIES = ("FR", "TN", "CH")

COUNTRY_TIMEZONES = {
    "FR": "Europe/Paris",
    "TN": "Africa/Tunis",
    "CH": "Europe/Zurich",
}

# Segments définis par notre groupe
# Ces valeurs ne sont pas imposées par le contrat du professeur.
CUSTOMER_SEGMENTS = (
    "NEW",
    "REGULAR",
    "LOYAL",
    "VIP",
)

# Paramètres de génération
DEFAULT_SEED = 42
