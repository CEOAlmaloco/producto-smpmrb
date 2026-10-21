"""Captura de mediciones desde la API del proveedor."""

import sqlite3

from smpmrb.registro import RegistroError


def registrar_medicion(
    con: sqlite3.Connection,
    sensor_id: int,
    valor: float,
    unidad: str,
    instante: str,
    origen: str,
) -> int:
    sensor = con.execute(
        "SELECT estado_acceso, codigo_proveedor FROM sensor_municipal WHERE id = ?",
        (sensor_id,),
    ).fetchone()
    if sensor is None:
        raise RegistroError(f"No existe el sensor {sensor_id}.")
    if sensor["estado_acceso"] != "con_credencial" or not sensor["codigo_proveedor"]:
        raise RegistroError(f"El sensor {sensor_id} no tiene código ni credenciales del proveedor.")
    if origen != "api_proveedor_municipal":
        raise RegistroError("Solo se aceptan mediciones provenientes de la API del proveedor.")
    cur = con.execute(
        """
        INSERT INTO medicion (sensor_id, valor, unidad, instante, origen)
        VALUES (?, ?, ?, ?, ?)
        """,
        (sensor_id, valor, unidad, instante, origen),
    )
    con.commit()
    return int(cur.lastrowid)
