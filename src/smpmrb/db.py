import sqlite3
from pathlib import Path

ESQUEMA = """
CREATE TABLE IF NOT EXISTS puente (
    id INTEGER PRIMARY KEY,
    codigo TEXT NOT NULL UNIQUE,
    nombre TEXT,
    ubicacion TEXT,
    criticidad TEXT,
    identidad_oficial TEXT NOT NULL DEFAULT 'pendiente_dom'
        CHECK (identidad_oficial IN ('pendiente_dom', 'confirmada'))
);

CREATE TABLE IF NOT EXISTS componente (
    id INTEGER PRIMARY KEY,
    puente_id INTEGER NOT NULL REFERENCES puente(id),
    codigo TEXT NOT NULL,
    nombre TEXT NOT NULL,
    UNIQUE (puente_id, codigo)
);

CREATE TABLE IF NOT EXISTS sensor_municipal (
    id INTEGER PRIMARY KEY,
    componente_id INTEGER NOT NULL REFERENCES componente(id),
    tipo TEXT NOT NULL CHECK (tipo IN ('vibracion', 'inclinacion')),
    codigo_proveedor TEXT,
    estado_acceso TEXT NOT NULL DEFAULT 'sin_credencial'
        CHECK (estado_acceso IN ('sin_credencial', 'con_credencial'))
);

CREATE TABLE IF NOT EXISTS canal_publico (
    id INTEGER PRIMARY KEY,
    fuente TEXT NOT NULL,
    archivo TEXT NOT NULL,
    canal TEXT NOT NULL,
    unidad TEXT,
    en_archivo_abierto INTEGER NOT NULL CHECK (en_archivo_abierto IN (0, 1)),
    UNIQUE (fuente, archivo, canal)
);

CREATE TABLE IF NOT EXISTS umbral (
    variable TEXT PRIMARY KEY,
    valor REAL,
    unidad TEXT NOT NULL,
    firmado_por TEXT,
    estado TEXT NOT NULL
        CHECK (estado IN ('pendiente_contraparte', 'firmado'))
);

CREATE TABLE IF NOT EXISTS medicion (
    id INTEGER PRIMARY KEY,
    sensor_id INTEGER NOT NULL REFERENCES sensor_municipal(id),
    valor REAL NOT NULL,
    unidad TEXT NOT NULL,
    instante TEXT NOT NULL,
    origen TEXT NOT NULL
);
"""


def conectar(ruta: Path) -> sqlite3.Connection:
    ruta.parent.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(ruta)
    con.row_factory = sqlite3.Row
    con.execute("PRAGMA foreign_keys = ON")
    con.executescript(ESQUEMA)
    return con


def crear_umbrales(con: sqlite3.Connection) -> None:
    """Crea los umbrales de vibración e inclinación sin valor."""
    con.executemany(
        """
        INSERT INTO umbral (variable, valor, unidad, firmado_por, estado)
        VALUES (?, NULL, ?, NULL, 'pendiente_contraparte')
        ON CONFLICT(variable) DO NOTHING
        """,
        [("vibracion", "m/s2"), ("inclinacion", "deg")],
    )
    con.commit()
