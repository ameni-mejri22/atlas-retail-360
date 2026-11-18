
import argparse
import random
from pathlib import Path
from src.product_catalog import generate_product_versions, save_product_versions
from src.store_catalog import save_stores
from src.fx_catalog import generate_fx_rates, save_fx_rates
from src.order_catalog import generate_orders, save_orders

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

    print("Atlas Retail 360 — Générateur")
    print(f"Seed       : {args.seed}")
    print(f"Profil     : {args.profile}")
    print(f"Répertoire : {args.output_dir}")
    print(f"Scénario   : {args.scenario}")

    demo_values = generate_demo_values(args.seed)
    print(f"Valeurs de vérification : {demo_values}")
        # Génération de la source product_versions
    product_rows = generate_product_versions(seed=args.seed)

    product_output = args.output_dir / "product_versions.parquet"
    
        # Génération de la source stores
    store_output = args.output_dir / "stores.csv"
    save_stores(store_output)
    
        # Génération de la source fx_rates
    fx_rows = generate_fx_rates(seed=args.seed)
    fx_output = args.output_dir / "fx_rates.csv"
    save_fx_rates(fx_rows, fx_output)
    
        # Génération de la source orders
    order_count = ORDER_COUNTS[args.profile]

    order_rows = generate_orders(
        seed=args.seed,
        count=order_count,
    )

    order_output = args.output_dir / "orders.jsonl"
    save_orders(order_rows, order_output)

    product_table = save_product_versions(
        product_rows,
        product_output,
    )

    print("Source product_versions générée avec succès.")
    print(f"Nombre de produits : {product_table.num_rows}")
    print(f"Fichier : {product_output}")


if __name__ == "__main__":
    main()
