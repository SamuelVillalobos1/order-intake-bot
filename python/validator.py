"""
Módulo de validación de pedidos (Order Intake Bot).

Una función por regla de negocio, más validate_row() que las junta y
devuelve (es_valida, motivo). Los motivos coinciden con los tipos de error
sembrados en generate_orders.py.
"""

import math
import re
from datetime import date, datetime
from typing import Optional

# Motivos de rechazo (mismos nombres que seeded_errors.json)
ORDER_ID_VACIO = "order_id_vacio"
ORDER_ID_DUPLICADO = "order_id_duplicado"
EMAIL_INVALIDO = "email_invalido"
SKU_INEXISTENTE = "sku_inexistente"
CANTIDAD_INVALIDA = "cantidad_invalida"
FECHA_INVALIDA = "fecha_invalida"
PRECIO_INVALIDO = "precio_invalido"

_EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def validar_order_id_presente(order_id) -> bool:
    """Regla 1a: el order_id es obligatorio (no vacío ni solo espacios)."""
    return order_id is not None and str(order_id).strip() != ""


def validar_order_id_unico(order_id, seen_ids: set) -> bool:
    """Regla 1b: el order_id no debe haber aparecido antes."""
    return str(order_id).strip() not in seen_ids


def validar_email(email) -> bool:
    """Regla 2: formato usuario@dominio.ext, con una sola arroba y sin espacios."""
    if email is None:
        return False
    return bool(_EMAIL_RE.match(str(email).strip()))


def validar_sku(sku, catalog_skus: set) -> bool:
    """Regla 3: el sku debe existir en el catálogo."""
    return sku is not None and str(sku).strip() in catalog_skus


def validar_cantidad(quantity) -> bool:
    """Regla 4: entero mayor a 0. Rechaza decimales como '2.5'."""
    try:
        value = int(str(quantity).strip())
    except (ValueError, TypeError):
        return False
    return value > 0


def validar_fecha(order_date, today: Optional[date] = None) -> bool:
    """Regla 5: fecha real en formato AAAA-MM-DD y no futura."""
    today = today or date.today()
    try:
        parsed = datetime.strptime(str(order_date).strip(), "%Y-%m-%d").date()
    except (ValueError, TypeError):
        return False
    return parsed <= today


def validar_precio(unit_price) -> bool:
    """Regla 6: número finito mayor a 0."""
    try:
        value = float(str(unit_price).strip())
    except (ValueError, TypeError):
        return False
    return math.isfinite(value) and value > 0


def validate_row(row: dict, catalog_skus: set, seen_ids: set,
                 today: Optional[date] = None):
    """
    Valida una fila contra las 6 reglas (7 motivos posibles).

    Devuelve (True, None) si es válida o (False, motivo) si no.
    Si la fila es válida, agrega su order_id a seen_ids, así una repetición
    posterior se rechaza como duplicada.
    """
    order_id = row.get("order_id")

    if not validar_order_id_presente(order_id):
        return False, ORDER_ID_VACIO
    if not validar_order_id_unico(order_id, seen_ids):
        return False, ORDER_ID_DUPLICADO
    if not validar_email(row.get("customer_email")):
        return False, EMAIL_INVALIDO
    if not validar_sku(row.get("sku"), catalog_skus):
        return False, SKU_INEXISTENTE
    if not validar_cantidad(row.get("quantity")):
        return False, CANTIDAD_INVALIDA
    if not validar_fecha(row.get("order_date"), today):
        return False, FECHA_INVALIDA
    if not validar_precio(row.get("unit_price")):
        return False, PRECIO_INVALIDO

    seen_ids.add(str(order_id).strip())
    return True, None