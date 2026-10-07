"""
Genera data/orders.csv con 200 pedidos ficticios, de los cuales el 15%
traen un error sembrado a propósito. Cada fila mala tiene UN solo error,
para que el conteo por tipo coincida 1 a 1 con los rechazos del bot.

También guarda data/seeded_errors.json con cuántos errores se sembraron
de cada tipo.

Uso (desde la carpeta python/):
    python generate_orders.py
"""

import csv
import json
import random
from datetime import date, timedelta
from pathlib import Path

# --- Configuración -----------------------------------------------------
TOTAL_ROWS = 200
ERROR_RATE = 0.15
RANDOM_SEED = 42  # misma semilla = mismos datos siempre (reproducible)

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
CSV_PATH = DATA_DIR / "orders.csv"
SUMMARY_PATH = DATA_DIR / "seeded_errors.json"

HEADERS = ["order_id", "customer_email", "sku", "quantity", "order_date", "unit_price"]

# Mismo catálogo que sql/02_seed_products.sql
CATALOG = {
    "SKU-001": 2.50, "SKU-002": 0.80, "SKU-003": 0.80, "SKU-004": 1.20,
    "SKU-005": 0.60, "SKU-006": 6.90, "SKU-007": 1.50, "SKU-008": 3.40,
    "SKU-009": 1.10, "SKU-010": 1.30, "SKU-011": 12.00, "SKU-012": 24.90,
    "SKU-013": 4.75, "SKU-014": 0.95, "SKU-015": 2.20, "SKU-016": 1.60,
    "SKU-017": 7.80, "SKU-018": 9.50, "SKU-019": 8.30, "SKU-020": 5.40,
}

FIRST_NAMES = ["ana", "luis", "maria", "jose", "carla", "pedro", "sofia",
               "diego", "laura", "andres", "valeria", "mateo"]
LAST_NAMES = ["mora", "vargas", "rojas", "jimenez", "solano", "campos",
              "araya", "chaves", "salas", "quesada"]
DOMAINS = ["gmail.com", "outlook.com", "yahoo.com", "empresa.cr"]

# Fechas válidas: desde 2026-01-01 hasta 2026-10-05 (nunca en el futuro)
START_DATE = date(2026, 1, 1)
END_DATE = date(2026, 10, 5)

ERROR_TYPES = [
    "order_id_vacio",
    "order_id_duplicado",
    "email_invalido",
    "sku_inexistente",
    "cantidad_invalida",
    "fecha_invalida",
    "precio_invalido",
]


# --- Generación de filas válidas ----------------------------------------
def random_date() -> date:
    days = (END_DATE - START_DATE).days
    return START_DATE + timedelta(days=random.randint(0, days))


def make_valid_row(index: int) -> dict:
    sku = random.choice(list(CATALOG))
    email = (
        f"{random.choice(FIRST_NAMES)}.{random.choice(LAST_NAMES)}"
        f"{random.randint(1, 99)}@{random.choice(DOMAINS)}"
    )
    return {
        "order_id": f"ORD-{index + 1:05d}",
        "customer_email": email,
        "sku": sku,
        "quantity": random.randint(1, 10),
        "order_date": random_date().isoformat(),
        "unit_price": f"{CATALOG[sku]:.2f}",
    }


# --- Siembra de errores -------------------------------------------------
def break_row(row: dict, error_type: str, clean_rows_before: list) -> None:
    """Modifica la fila para que falle exactamente una regla."""
    if error_type == "order_id_vacio":
        row["order_id"] = ""
    elif error_type == "order_id_duplicado":
        # Copia el order_id de una fila limpia que aparece ANTES en el archivo,
        # así la primera ocurrencia es válida y solo la repetida se rechaza.
        row["order_id"] = random.choice(clean_rows_before)["order_id"]
    elif error_type == "email_invalido":
        row["customer_email"] = random.choice([
            row["customer_email"].replace("@", ""),   # sin arroba
            row["customer_email"].split("@")[0],      # sin dominio
            row["customer_email"].replace(".", "", 1).replace("@", "@@"),
        ])
    elif error_type == "sku_inexistente":
        row["sku"] = random.choice(["SKU-999", "SKU-000", "XXX-123", "SKU-ABC"])
    elif error_type == "cantidad_invalida":
        row["quantity"] = random.choice([0, -1, -5, -10])
    elif error_type == "fecha_invalida":
        row["order_date"] = random.choice([
            "2026-02-30",   # día imposible
            "2026-13-05",   # mes imposible
            "2026-04-31",   # abril no tiene 31
            "2027-03-15",   # fecha futura
            "2030-01-01",   # fecha futura
        ])
    elif error_type == "precio_invalido":
        row["unit_price"] = random.choice(["0.00", "-3.50", "abc", "-1.00"])


def main() -> None:
    random.seed(RANDOM_SEED)
    DATA_DIR.mkdir(exist_ok=True)

    rows = [make_valid_row(i) for i in range(TOTAL_ROWS)]

    # Elegimos qué filas se dañan. Empezamos en la 10 para que siempre
    # existan filas limpias antes (necesario para los duplicados).
    num_errors = round(TOTAL_ROWS * ERROR_RATE)
    bad_indexes = sorted(random.sample(range(10, TOTAL_ROWS), num_errors))

    # Reparto parejo entre tipos, luego mezclado
    error_assignments = [ERROR_TYPES[i % len(ERROR_TYPES)] for i in range(num_errors)]
    random.shuffle(error_assignments)

    bad_set = set(bad_indexes)
    counts = {t: 0 for t in ERROR_TYPES}

    for idx, error_type in zip(bad_indexes, error_assignments):
        clean_before = [rows[i] for i in range(idx) if i not in bad_set]
        break_row(rows[idx], error_type, clean_before)
        counts[error_type] += 1

    # Escribir CSV
    with open(CSV_PATH, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=HEADERS)
        writer.writeheader()
        writer.writerows(rows)

    # Escribir resumen de errores sembrados
    summary = {
        "total_rows": TOTAL_ROWS,
        "rows_with_errors": num_errors,
        "expected_valid": TOTAL_ROWS - num_errors,
        "errors_by_type": counts,
    }
    with open(SUMMARY_PATH, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)

    print(f"Archivo generado: {CSV_PATH}")
    print(f"Filas totales: {TOTAL_ROWS} | con error: {num_errors} | válidas esperadas: {TOTAL_ROWS - num_errors}")
    print("Errores sembrados por tipo:")
    for error_type, count in counts.items():
        print(f"  {error_type}: {count}")


if __name__ == "__main__":
    main()