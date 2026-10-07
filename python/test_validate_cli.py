"""Pruebas de validate_cli.py."""

from validate_cli import main

FILA = ["ORD-00001", "ana.mora5@gmail.com", "SKU-001", "3", "2026-05-10", "2.50"]


def test_valida_y_detecta_duplicado(tmp_path, capsys):
    seen = str(tmp_path / "seen.txt")
    assert main(["--seen-file", seen, "--reset"]) == 0
    capsys.readouterr()

    assert main(["--seen-file", seen, *FILA]) == 0
    assert capsys.readouterr().out.strip() == "VALID"

    assert main(["--seen-file", seen, *FILA]) == 0
    assert capsys.readouterr().out.strip() == "INVALID|order_id_duplicado"


def test_fila_rechazada_no_queda_registrada(tmp_path, capsys):
    seen = str(tmp_path / "seen.txt")
    main(["--seen-file", seen, "--reset"])
    capsys.readouterr()

    mala = FILA.copy()
    mala[3] = "-1"
    main(["--seen-file", seen, *mala])
    assert capsys.readouterr().out.strip() == "INVALID|cantidad_invalida"

    main(["--seen-file", seen, *FILA])
    assert capsys.readouterr().out.strip() == "VALID"


def test_order_id_vacio(tmp_path, capsys):
    seen = str(tmp_path / "seen.txt")
    main(["--seen-file", seen, "--reset"])
    capsys.readouterr()

    fila = FILA.copy()
    fila[0] = ""
    main(["--seen-file", seen, *fila])
    assert capsys.readouterr().out.strip() == "INVALID|order_id_vacio"


def test_cantidad_de_campos_incorrecta(tmp_path, capsys):
    assert main(["--seen-file", str(tmp_path / "seen.txt"), "solo", "dos"]) == 2