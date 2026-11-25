
import argparse
import random
from pathlib import Path

from src.product_catalog import generate_product_versions, save_product_versions
from src.store_catalog import save_stores
from src.fx_catalog import generate_fx_rates, save_fx_rates
from src.order_catalog import generate_orders, save_orders
from src.order_line_catalog import (
    load_product_catalog,
    load_fx_rates,
    load_opening_stock,
    generate_order_lines,
    save_order_lines,
)

DEFAULT_SEED = 42
VALID_PROFILES = ("MICRO", "STANDARD", "SCALE")
ORDER_COUNTS = {
    "MICRO": 100,
    "STANDARD": 30000,
    "SCALE": 300000,
}


def parse_args():
    parser = argparse.ArgumentParser(
        description="Générateur de données synthétiques Atlas Retail 360"
    )
    parser.add_argument("--seed", type=int, default=DEFAULT_SEED)
    parser.add_argument(
        "--profile",
        choices=VALID_PROFILES,
        default="MICRO",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("data/generated"),
    )
    parser.add_argument(
        "--scenario",
        choices=("clean", "perturbed"),
        default="clean",
    )
    return parser.parse_args()


def generate_demo_values(seed, count=5):
    """Produit des valeurs reproductibles pour vérifier la graine."""
    rng = random.Random(seed)
    return [rng.randint(1, 1000) for _ in range(count)]


def main():
    args = parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)

    print("Atlas Retail 360 — Générateur")
    print(f"Seed       : {args.seed}")
    print(f"Profil     : {args.profile}")
    print(f"Répertoire : {args.output_dir}")
    print(f"Scénario   : {args.scenario}")

    demo_values = generate_demo_values(args.seed)
    print(f"Valeurs de vérification : {demo_values}")

    # 1. Génération de product_versions
    product_rows = generate_product_versions(seed=args.seed)
    product_output = args.output_dir / "product_versions.parquet"

    product_table = save_product_versions(
        product_rows,
        product_output,
    )

    print("Source product_versions générée avec succès.")
    print(f"Nombre de produits : {product_table.num_rows}")
    print(f"Fichier : {product_output}")

    # 2. Génération de stores
    store_output = args.output_dir / "stores.csv"
    save_stores(store_output)

    # 3. Génération de fx_rates
    fx_rows = generate_fx_rates(seed=args.seed)
    fx_output = args.output_dir / "fx_rates.csv"
    save_fx_rates(fx_rows, fx_output)

    # 4. Génération de orders
    order_count = ORDER_COUNTS[args.profile]

    order_rows = generate_orders(
        seed=args.seed,
        count=order_count,
    )

    order_output = args.output_dir / "orders.jsonl"
    save_orders(order_rows, order_output)

    print("Source orders générée avec succès.")
    print(f"Nombre de commandes : {len(order_rows)}")

    # 5. Chargement des produits, taux et stocks initiaux
    products = load_product_catalog(product_output)
    rates = load_fx_rates(fx_output)

    opening_stock = load_opening_stock(
        args.output_dir / "opening_stock.csv"
    )

    # Copie de travail du stock initial
    stock = opening_stock.copy()

    # 6. Génération des lignes de commande
    rng = random.Random(args.seed)
    order_line_rows = []

    # Traitement des commandes dans l'ordre chronologique
    sorted_orders = sorted(
        order_rows,
        key=lambda order: (
            order["order_ts"],
            order["order_id"],
        ),
    )

    for order in sorted_orders:
        lines = generate_order_lines(
            order=order,
            products=products,
            rates=rates,
            rng=rng,
            stock=stock,
        )
        order_line_rows.extend(lines)

    # 7. Enregistrement de order_lines.csv
    order_line_output = args.output_dir / "order_lines.csv"

    save_order_lines(
        order_line_rows,
        order_line_output,
    )

    print("Source order_lines générée avec succès.")
    print(f"Nombre de lignes : {len(order_line_rows)}")
    print(f"Fichier : {order_line_output}")


if __name__ == "__main__":
    main()
