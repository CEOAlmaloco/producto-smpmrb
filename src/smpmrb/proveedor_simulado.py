"""Proveedor local de prueba.

No es la API del proveedor de los sensores y no guarda credenciales reales.
Cada lectura queda con origen 'simulado'. Las tareas 1.3.4 y 1.3.5 siguen bloqueadas.
"""

import sqlite3
from pathlib import Path

from smpmrb.db import conectar
from smpmrb.medicion import registrar_medicion
from smpmrb.registro import RegistroError, cargar_puentes_piloto

TOKEN_SIMULADO = "simulado-local"
URL_SIMULADA = "simulado://local/mediciones"
INSTANTE_DEMO = "2026-10-21T12:00:00"

# Valores bajo el umbral de atención, para no inventar una alerta.
VALORES_NORMALES = {
    "vibracion": (0.2, "m/s2"),
    "inclinacion": (0.05, "deg"),
}


def exigir_token(token: str) -> None:
    if token != TOKEN_SIMULADO:
        raise RegistroError(
            "El token no corresponde al proveedor simulado. No reemplaza las credenciales del proveedor."
        )


def consultar(con: sqlite3.Connection, token: str, instante: str) -> list[dict]:
    """Devuelve una lectura de prueba por sensor, con los cinco campos acordados."""
    exigir_token(token)
    filas = con.execute(
        """
        SELECT s.id AS sensor_id, s.tipo, p.codigo AS puente, c.codigo AS componente
        FROM sensor_municipal s
        JOIN componente c ON c.id = s.componente_id
        JOIN puente p ON p.id = c.puente_id
        ORDER BY p.codigo, c.codigo, s.tipo
        """
    ).fetchall()
    if not filas:
        raise RegistroError("No hay sensores registrados para simular.")
    lecturas = []
    for fila in filas:
        valor, unidad = VALORES_NORMALES[fila["tipo"]]
        lecturas.append(
            {
                "puente": fila["puente"],
                "sensor": f"SIM-{fila['puente']}-{fila['componente']}-{fila['tipo']}",
                "sensor_id": fila["sensor_id"],
                "tipo": fila["tipo"],
                "valor": valor,
                "unidad": unidad,
                "instante": instante,
                "origen": "simulado",
            }
        )
    return lecturas


def capturar(con: sqlite3.Connection, token: str, instante: str) -> int:
    """Reemplaza las lecturas simuladas de ese instante. No toca el estado de acceso de los sensores."""
    lecturas = consultar(con, token, instante)
    con.execute("DELETE FROM medicion WHERE origen = 'simulado' AND instante = ?", (instante,))
    for lectura in lecturas:
        registrar_medicion(
            con,
            lectura["sensor_id"],
            lectura["valor"],
            lectura["unidad"],
            lectura["instante"],
            "simulado",
        )
    return len(lecturas)


def main() -> None:
    raiz = Path(__file__).resolve().parents[2]
    con = conectar(raiz / "data" / "smpmrb.sqlite")
    cargar_puentes_piloto(con)
    n = capturar(con, TOKEN_SIMULADO, INSTANTE_DEMO)
    print(f"{n} mediciones simuladas guardadas ({URL_SIMULADA}). No provienen del proveedor.")
    con.close()


if __name__ == "__main__":
    main()
