"""Pruebas de validator.py con pytest."""

import csv
import json
from datetime import date
from pathlib import Path

import pytest

from validator import (
    validar_order_id_presente, validar_order_id_unico, validar_email,
    validar_sku, validar_cantidad, validar_fecha, validar_precio,
    validate_row,
)

CATALOG = {f"SKU-{i:03d}" for i in range(1, 21)}
TODAY = date(2026, 10, 7)


def fila_valida(**cambios):
    row = {
        "order_id": "ORD-00001",
        "customer_email": "ana.mora5@gmail.com",
        "sku": "SKU-001",
        "quantity": "3",
        "order_date": "2026-05-10",
        "unit_price": "2.50",
    }
    row.update(cambios)
    return row


# --- Regla 1a: order_id obligatorio ---
def test_order_id_presente_ok():
    assert validar_order_id_presente("ORD-00001")


@pytest.mark.parametrize("valor", ["", "   ", None])
def test_order_id_presente_falla(valor):
    assert not validar_order_id_presente(valor)


# --- Regla 1b: order_id sin duplicados ---
def test_order_id_unico_ok():
    assert validar_order_id_unico("ORD-00002", {"ORD-00001"})


def test_order_id_unico_falla():
    assert not validar_order_id_unico("ORD-00001", {"ORD-00001"})


# --- Regla 2: email ---
def test_email_ok():
    assert validar_email("luis.vargas10@outlook.com")


@pytest.mark.parametrize("valor", [
    "luis.vargas10outlook.com", "luis.vargas10", "luis@@outlook.com",
    "luis @outlook.com", "", None,
])
def test_email_falla(valor):
    assert not validar_email(valor)


# --- Regla 3: sku en catálogo ---
def test_sku_ok():
    assert validar_sku("SKU-020", CATALOG)


@pytest.mark.parametrize("valor", ["SKU-999", "XXX-123", "", None])
def test_sku_falla(valor):
    assert not validar_sku(valor, CATALOG)


# --- Regla 4: cantidad entera > 0 ---
@pytest.mark.parametrize("valor", ["1", "10", 5])
def test_cantidad_ok(valor):
    assert validar_cantidad(valor)


@pytest.mark.parametrize("valor", ["0", "-1", "2.5", "abc", "", None])
def test_cantidad_falla(valor):
    assert not validar_cantidad(valor)


# --- Regla 5: fecha válida y no futura ---
def test_fecha_ok():
    assert validar_fecha("2026-10-07", TODAY)  # hoy cuenta como válida


@pytest.mark.parametrize("valor", [
    "2026-02-30", "2026-13-05", "2026-04-31",   # imposibles
    "2027-03-15",                                # futura
    "10/05/2026", "", None,                      # formato incorrecto
])
def test_fecha_falla(valor):
    assert not validar_fecha(valor, TODAY)


# --- Regla 6: precio numérico > 0 ---
@pytest.mark.parametrize("valor", ["0.01", "24.90", 3])
def test_precio_ok(valor):
    assert validar_precio(valor)


@pytest.mark.parametrize("valor", ["0.00", "-3.50", "abc", "nan", "inf", "", None])
def test_precio_falla(valor):
    assert not validar_precio(valor)


# --- validate_row: integración de reglas ---
def test_validate_row_valida():
    seen = set()
    assert validate_row(fila_valida(), CATALOG, seen, TODAY) == (True, None)
    assert "ORD-00001" in seen


@pytest.mark.parametrize("cambios, motivo", [
    ({"order_id": ""}, "order_id_vacio"),
    ({"customer_email": "sin-arroba.com"}, "email_invalido"),
    ({"sku": "SKU-999"}, "sku_inexistente"),
    ({"quantity": "-2"}, "cantidad_invalida"),
    ({"order_date": "2026-02-30"}, "fecha_invalida"),
    ({"unit_price": "abc"}, "precio_invalido"),
])
def test_validate_row_motivos(cambios, motivo):
    seen = set()
    assert validate_row(fila_valida(**cambios), CATALOG, seen, TODAY) == (False, motivo)
    assert seen == set()  # una fila rechazada no registra su order_id


def test_validate_row_duplicado():
    seen = set()
    assert validate_row(fila_valida(), CATALOG, seen, TODAY)[0] is True
    assert validate_row(fila_valida(), CATALOG, seen, TODAY) == (False, "order_id_duplicado")


# --- Prueba contra los datos reales sembrados ---
def test_contra_datos_sembrados():
    data_dir = Path(__file__).resolve().parent.parent / "data"
    csv_path = data_dir / "orders.csv"
    summary_path = data_dir / "seeded_errors.json"
    if not (csv_path.exists() and summary_path.exists()):
        pytest.skip("Ejecuta generate_orders.py primero")

    esperado = json.loads(summary_path.read_text(encoding="utf-8"))
    seen, validas, rechazos = set(), 0, {}

    with open(csv_path, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            ok, motivo = validate_row(row, CATALOG, seen, TODAY)
            if ok:
                validas += 1
            else:
                rechazos[motivo] = rechazos.get(motivo, 0) + 1

    assert validas == esperado["expected_valid"]
    esperado_por_tipo = {k: v for k, v in esperado["errors_by_type"].items() if v > 0}
    assert rechazos == esperado_por_tipo