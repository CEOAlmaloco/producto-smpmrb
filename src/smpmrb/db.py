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
    variable TEXT NOT NULL CHECK (variable IN ('vibracion', 'inclinacion')),
    nivel TEXT NOT NULL CHECK (nivel IN ('atencion', 'alerta', 'critico')),
    desde REAL NOT NULL,
    unidad TEXT NOT NULL,
    base_calculo TEXT NOT NULL,
    fuente TEXT NOT NULL,
    estado TEXT NOT NULL
        CHECK (estado IN ('adoptado_equipo', 'revisado_contraparte')),
    PRIMARY KEY (variable, nivel)
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


VIBRACION_BASE = "Aceleración vertical pico del componente en ventanas de 1 minuto."
INCLINACION_BASE = "Cambio respecto de la referencia del sensor (promedio de sus primeros 30 días), promedio móvil de 1 hora."
SETRA = "Sétra 2006 / HiVoSS, clases de confort; EN 1990 Anexo A2 recomienda 0,7 m/s2."
AASHTO = "AASHTO LRFD 10.5.2.2: distorsión angular 0,004 rad (continuos) y 0,008 rad (tramo simple)."

UMBRALES = (
    ("vibracion", "atencion", 0.5, "m/s2", VIBRACION_BASE, SETRA),
    ("vibracion", "alerta", 1.0, "m/s2", VIBRACION_BASE, SETRA),
    ("vibracion", "critico", 2.5, "m/s2", VIBRACION_BASE, SETRA),
    ("inclinacion", "atencion", 0.115, "deg", INCLINACION_BASE, AASHTO),
    ("inclinacion", "alerta", 0.229, "deg", INCLINACION_BASE, AASHTO),
    ("inclinacion", "critico", 0.458, "deg", INCLINACION_BASE, AASHTO),
)
ORDEN_NIVELES = ("atencion", "alerta", "critico")


def crear_umbrales(con: sqlite3.Connection) -> None:
    """Carga los umbrales adoptados por el equipo; la contraparte los revisa antes de la puesta en marcha."""
    con.executemany(
        """
        INSERT INTO umbral (variable, nivel, desde, unidad, base_calculo, fuente, estado)
        VALUES (?, ?, ?, ?, ?, ?, 'adoptado_equipo')
        ON CONFLICT(variable, nivel) DO NOTHING
        """,
        UMBRALES,
    )
    con.commit()


def nivel_umbral(con: sqlite3.Connection, variable: str, valor: float) -> str:
    """Devuelve 'normal' o el nivel más alto cuyo valor 'desde' se alcanza; para inclinación se usa el valor absoluto."""
    filas = con.execute(
        "SELECT nivel, desde FROM umbral WHERE variable = ?", (variable,)
    ).fetchall()
    if not filas:
        raise ValueError(f"No hay umbrales cargados para {variable}.")
    medido = abs(valor)
    alcanzados = [f["nivel"] for f in filas if medido >= f["desde"]]
    if not alcanzados:
        return "normal"
    return max(alcanzados, key=ORDEN_NIVELES.index)
