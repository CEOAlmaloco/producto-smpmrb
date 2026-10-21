"""Estado de las tareas del cronograma a partir de los datos de la base."""

import sqlite3
from pathlib import Path

from smpmrb.catalogo import cargar_encabezado
from smpmrb.db import conectar, crear_umbrales
from smpmrb.registro import cargar_puentes_piloto

HOY = "2026-10-20"

PLAN = (
    {
        "edt": "1.4.1",
        "nombre": "Ambiente de desarrollo",
        "debio_cerrar": "2026-09-11",
        "clave": "ambiente",
    },
    {
        "edt": "1.3.1",
        "nombre": "Levantamiento de la plataforma IoT",
        "debio_cerrar": "2026-09-16",
        "clave": "iot",
    },
    {
        "edt": "1.3.3",
        "nombre": "Correspondencia sensor-componente",
        "debio_cerrar": "2026-09-23",
        "clave": "correspondencia",
    },
    {
        "edt": "1.4.2",
        "nombre": "Registro de infraestructura",
        "debio_cerrar": "2026-09-29",
        "clave": "registro",
    },
    {
        "edt": "1.3.2",
        "nombre": "Umbrales preliminares",
        "debio_cerrar": "2026-09-30",
        "clave": "umbrales",
    },
    {
        "edt": "1.3.4",
        "nombre": "Acceso a la API del proveedor",
        "debio_cerrar": "2026-09-30",
        "clave": "api",
    },
    {
        "edt": "1.3.5",
        "nombre": "Validación de conectividad",
        "debio_cerrar": "2026-10-12",
        "clave": "conectividad",
    },
    {
        "edt": "1.4.3",
        "nombre": "Captura de mediciones",
        "debio_cerrar": "después de 1.3.5",
        "clave": "captura",
    },
    {
        "edt": "1.4.4",
        "nombre": "Reglas de alerta",
        "debio_cerrar": "2026-11-03",
        "clave": "alertas",
    },
)


def preparar(con: sqlite3.Connection, encabezado: Path) -> None:
    crear_umbrales(con)
    cargar_puentes_piloto(con)
    cargar_encabezado(encabezado, con)


def evaluar(con: sqlite3.Connection) -> list[dict]:
    puentes = con.execute("SELECT COUNT(*) AS n FROM puente").fetchone()["n"]
    confirmados = con.execute(
        "SELECT COUNT(*) AS n FROM puente WHERE identidad_oficial = 'confirmada'"
    ).fetchone()["n"]
    sensores = con.execute("SELECT COUNT(*) AS n FROM sensor_municipal").fetchone()["n"]
    sin_credencial = con.execute(
        "SELECT COUNT(*) AS n FROM sensor_municipal WHERE estado_acceso = 'sin_credencial'"
    ).fetchone()["n"]
    canales = con.execute("SELECT COUNT(*) AS n FROM canal_publico").fetchone()["n"]
    umbrales_firmados = con.execute(
        "SELECT COUNT(*) AS n FROM umbral WHERE estado = 'firmado' AND valor IS NOT NULL"
    ).fetchone()["n"]
    mediciones = con.execute("SELECT COUNT(*) AS n FROM medicion").fetchone()["n"]

    evidencias = {
        "ambiente": (
            "atrasado_hecho",
            "Repositorio y base SQLite disponibles. Planificado para el 11/09.",
        ),
        "iot": (
            "atrasado_parcial",
            f"Se revisó un conjunto de datos público ({canales} canales de inclinación). "
            "Falta la documentación de la API del proveedor.",
        ),
        "correspondencia": (
            "atrasado_parcial",
            f"{sensores} sensores asociados a componentes. Falta el código asignado por el proveedor.",
        ),
        "registro": (
            "atrasado_parcial" if confirmados < 2 else "hecho",
            f"{puentes} puentes registrados, {confirmados} con nombre y ubicación confirmados por la DOM.",
        ),
        "umbrales": (
            "bloqueado",
            f"{umbrales_firmados} umbrales con valor. Pendiente la validación de ingeniería estructural.",
        ),
        "api": (
            "bloqueado",
            f"{sin_credencial} sensores sin acceso. Faltan la URL y las credenciales del proveedor.",
        ),
        "conectividad": (
            "bloqueado",
            "Requiere acceso a la API para probar la recepción de datos en ambos puentes.",
        ),
        "captura": (
            "bloqueado",
            f"{mediciones} mediciones guardadas. Requiere acceso a la API.",
        ),
        "alertas": (
            "no_iniciado",
            "Requiere umbrales validados y mediciones.",
        ),
    }
    filas = []
    for item in PLAN:
        estado, evidencia = evidencias[item["clave"]]
        filas.append({**item, "estado": estado, "evidencia": evidencia, "medido": HOY})
    return filas


def render(filas: list[dict]) -> str:
    lineas = [f"Estado al {HOY}", ""]
    for fila in filas:
        lineas.append(
            f"{fila['edt']} {fila['nombre']} | término planificado: {fila['debio_cerrar']} | {fila['estado']}"
        )
        lineas.append(f"    {fila['evidencia']}")
    return "\n".join(lineas)


def main() -> None:
    raiz = Path(__file__).resolve().parents[2]
    base = raiz / "data" / "smpmrb.sqlite"
    encabezado = raiz / "data" / "encabezado_inc_munich.txt"
    con = conectar(base)
    preparar(con, encabezado)
    print(render(evaluar(con)))


if __name__ == "__main__":
    main()
