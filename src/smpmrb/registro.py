"""Registro de puentes (HU-01): código, ubicación, componentes, sensores y criticidad."""

import sqlite3

COMPONENTES = (
    ("tablero", "Tablero"),
    ("viga", "Viga principal"),
    ("estribo", "Estribo"),
)
SENSORES_POR_COMPONENTE = ("vibracion", "inclinacion")


class RegistroError(ValueError):
    pass


def registrar_puente(
    con: sqlite3.Connection,
    codigo: str,
    nombre: str | None = None,
    ubicacion: str | None = None,
    criticidad: str | None = None,
    identidad_oficial: str = "pendiente_dom",
) -> int:
    codigo = (codigo or "").strip()
    if not codigo:
        raise RegistroError("El código del puente es obligatorio.")
    if identidad_oficial not in ("pendiente_dom", "confirmada"):
        raise RegistroError("identidad_oficial debe ser 'pendiente_dom' o 'confirmada'.")
    if identidad_oficial == "confirmada" and not (nombre and ubicacion):
        raise RegistroError("Para confirmar un puente se requieren nombre y ubicación.")
    try:
        cur = con.execute(
            """
            INSERT INTO puente (codigo, nombre, ubicacion, criticidad, identidad_oficial)
            VALUES (?, ?, ?, ?, ?)
            """,
            (codigo, nombre, ubicacion, criticidad, identidad_oficial),
        )
    except sqlite3.IntegrityError as exc:
        raise RegistroError(f"Ya existe un puente con el código {codigo}.") from exc
    con.commit()
    return int(cur.lastrowid)


def agregar_componente(con: sqlite3.Connection, puente_id: int, codigo: str, nombre: str) -> int:
    cur = con.execute(
        "INSERT INTO componente (puente_id, codigo, nombre) VALUES (?, ?, ?)",
        (puente_id, codigo, nombre),
    )
    con.commit()
    return int(cur.lastrowid)


def agregar_sensor(con: sqlite3.Connection, componente_id: int, tipo: str) -> int:
    if tipo not in SENSORES_POR_COMPONENTE:
        raise RegistroError("El tipo de sensor debe ser 'vibracion' o 'inclinacion'.")
    cur = con.execute(
        """
        INSERT INTO sensor_municipal (componente_id, tipo, codigo_proveedor, estado_acceso)
        VALUES (?, ?, NULL, 'sin_credencial')
        """,
        (componente_id, tipo),
    )
    con.commit()
    return int(cur.lastrowid)


def cargar_puentes_piloto(con: sqlite3.Connection) -> None:
    """Registra los dos puentes del piloto, pendientes de nombre y ubicación oficiales."""
    existentes = con.execute("SELECT COUNT(*) AS n FROM puente").fetchone()["n"]
    if existentes:
        return
    for n in (1, 2):
        puente_id = registrar_puente(con, codigo=f"PILOTO-0{n}")
        for codigo, nombre in COMPONENTES:
            componente_id = agregar_componente(con, puente_id, codigo, nombre)
            for tipo in SENSORES_POR_COMPONENTE:
                agregar_sensor(con, componente_id, tipo)


def ficha(con: sqlite3.Connection, codigo: str) -> dict | None:
    puente = con.execute("SELECT * FROM puente WHERE codigo = ?", (codigo,)).fetchone()
    if puente is None:
        return None
    componentes = []
    for componente in con.execute(
        "SELECT * FROM componente WHERE puente_id = ? ORDER BY codigo",
        (puente["id"],),
    ):
        sensores = con.execute(
            "SELECT tipo, codigo_proveedor, estado_acceso FROM sensor_municipal WHERE componente_id = ? ORDER BY tipo",
            (componente["id"],),
        ).fetchall()
        componentes.append({**dict(componente), "sensores": [dict(s) for s in sensores]})
    return {**dict(puente), "componentes": componentes}


def confirmar_identidad(
    con: sqlite3.Connection, codigo: str, nombre: str, ubicacion: str, criticidad: str | None = None
) -> None:
    if not nombre.strip() or not ubicacion.strip():
        raise RegistroError("Para confirmar un puente se requieren nombre y ubicación.")
    cur = con.execute(
        """
        UPDATE puente
        SET nombre = ?, ubicacion = ?, criticidad = ?, identidad_oficial = 'confirmada'
        WHERE codigo = ?
        """,
        (nombre.strip(), ubicacion.strip(), criticidad, codigo),
    )
    if cur.rowcount != 1:
        raise RegistroError(f"No existe el puente {codigo}.")
    con.commit()
