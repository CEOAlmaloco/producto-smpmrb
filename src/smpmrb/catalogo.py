"""Catálogo de canales del conjunto de datos público de Múnich."""

import sqlite3
from pathlib import Path

FUENTE = "imcs-compsim/munich-bridge-data"
ARCHIVO = "ReferenceState/ReferenceStateINCAt100Hz.csv.zip"
URL = (
    "https://raw.githubusercontent.com/imcs-compsim/munich-bridge-data/main/"
    "ReferenceState/ReferenceStateINCAt100Hz.csv.zip"
)


def canales_desde_encabezado(linea: str) -> list[dict]:
    canales = []
    for parte in linea.strip().split(","):
        parte = parte.strip()
        if not parte or parte.lower().startswith("time"):
            continue
        unidad = None
        nombre = parte
        if "[" in parte and parte.endswith("]"):
            nombre, resto = parte.rsplit("[", 1)
            nombre = nombre.strip()
            unidad = resto[:-1].strip()
        canales.append({"canal": nombre, "unidad": unidad})
    return canales


def cargar_encabezado(ruta: Path, con: sqlite3.Connection) -> int:
    linea = ruta.read_text(encoding="utf-8").splitlines()[0]
    canales = canales_desde_encabezado(linea)
    for canal in canales:
        con.execute(
            """
            INSERT INTO canal_publico (fuente, archivo, canal, unidad, en_archivo_abierto)
            VALUES (?, ?, ?, ?, 1)
            ON CONFLICT(fuente, archivo, canal) DO NOTHING
            """,
            (FUENTE, ARCHIVO, canal["canal"], canal["unidad"]),
        )
    con.commit()
    return len(canales)
