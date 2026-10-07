"""
Interfaz de línea de comandos del validador, pensada para que UiPath la llame
una vez por fila.

Uso:
    python validate_cli.py --seen-file ..\\data\\seen_ids.txt --reset
    python validate_cli.py --seen-file ..\\data\\seen_ids.txt \
        ORDER_ID EMAIL SKU QUANTITY ORDER_DATE UNIT_PRICE

Salida (una sola línea por stdout):
    VALID
    INVALID|<motivo>

Código de salida: 0 si pudo validar (sea válida o no), 2 si los argumentos son incorrectos.
"""

import argparse
import sys
from pathlib import Path

from generate_orders import CATALOG  # mismo catálogo que sql/02_seed_products.sql
from validator import validate_row

FIELDS = ["order_id", "customer_email", "sku", "quantity", "order_date", "unit_price"]


def load_seen(path: Path) -> set:
    if not path.exists():
        return set()
    return {line.strip() for line in path.read_text(encoding="utf-8").splitlines() if line.strip()}


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Valida una fila de pedido.")
    parser.add_argument("--seen-file", required=True, help="Archivo donde se guardan los order_id ya vistos")
    parser.add_argument("--reset", action="store_true", help="Vacía el archivo de order_id vistos y termina")
    parser.add_argument("fields", nargs="*", help="Los 6 campos de la fila, en orden")
    args = parser.parse_args(argv)

    seen_path = Path(args.seen_file)

    if args.reset:
        seen_path.parent.mkdir(parents=True, exist_ok=True)
        seen_path.write_text("", encoding="utf-8")
        print("OK")
        return 0

    if len(args.fields) != len(FIELDS):
        print(f"ERROR|se esperaban {len(FIELDS)} campos y llegaron {len(args.fields)}")
        return 2

    row = dict(zip(FIELDS, args.fields))
    seen = load_seen(seen_path)
    is_valid, reason = validate_row(row, set(CATALOG), seen)

    if is_valid:
        with open(seen_path, "a", encoding="utf-8") as f:
            f.write(row["order_id"].strip() + "\n")
        print("VALID")
    else:
        print(f"INVALID|{reason}")
    return 0


if __name__ == "__main__":
    sys.exit(main())