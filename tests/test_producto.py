import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from smpmrb.catalogo import canales_desde_encabezado, cargar_encabezado
from smpmrb.db import conectar, crear_umbrales, nivel_umbral
from smpmrb.estado import evaluar, preparar
from smpmrb.medicion import registrar_medicion
from smpmrb.proveedor_simulado import TOKEN_SIMULADO, capturar
from smpmrb.registro import RegistroError, confirmar_identidad, ficha, registrar_puente, cargar_puentes_piloto

RAIZ = Path(__file__).resolve().parents[1]
ENCABEZADO = RAIZ / "data" / "encabezado_inc_munich.txt"


class RegistroTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.con = conectar(Path(self.tmp.name) / "t.sqlite")

    def tearDown(self):
        self.con.close()
        self.tmp.cleanup()

    def test_rechaza_puente_sin_codigo(self):
        with self.assertRaises(RegistroError):
            registrar_puente(self.con, "  ")

    def test_no_duplica_codigo(self):
        registrar_puente(self.con, "P-1")
        with self.assertRaises(RegistroError):
            registrar_puente(self.con, "P-1")

    def test_puentes_piloto_quedan_pendientes_de_confirmar(self):
        cargar_puentes_piloto(self.con)
        uno = ficha(self.con, "PILOTO-01")
        self.assertEqual(uno["identidad_oficial"], "pendiente_dom")
        self.assertIsNone(uno["nombre"])
        self.assertEqual(len(uno["componentes"]), 3)
        sensores = [s["tipo"] for c in uno["componentes"] for s in c["sensores"]]
        self.assertEqual(sensores.count("vibracion"), 3)
        self.assertEqual(sensores.count("inclinacion"), 3)
        self.assertTrue(all(s["estado_acceso"] == "sin_credencial" for c in uno["componentes"] for s in c["sensores"]))

    def test_confirmar_exige_nombre_y_ubicacion(self):
        registrar_puente(self.con, "P-9")
        with self.assertRaises(RegistroError):
            confirmar_identidad(self.con, "P-9", " ", "centro")


class CatalogoTest(unittest.TestCase):
    def test_encabezado_munich_solo_tiene_inclinacion(self):
        linea = ENCABEZADO.read_text(encoding="utf-8")
        canales = canales_desde_encabezado(linea)
        self.assertEqual([c["canal"] for c in canales], ["INC-01", "INC-01 Filtered"])
        self.assertEqual(canales[0]["unidad"], "deg")
        self.assertNotIn("vibracion", linea.lower())


class MedicionTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.con = conectar(Path(self.tmp.name) / "t.sqlite")
        cargar_puentes_piloto(self.con)

    def tearDown(self):
        self.con.close()
        self.tmp.cleanup()

    def test_rechaza_medicion_sin_credencial(self):
        sensor_id = self.con.execute("SELECT id FROM sensor_municipal LIMIT 1").fetchone()["id"]
        with self.assertRaises(RegistroError):
            registrar_medicion(self.con, sensor_id, 0.01, "deg", "2026-10-20T00:00:00", "api_proveedor_municipal")
        self.assertEqual(self.con.execute("SELECT COUNT(*) AS n FROM medicion").fetchone()["n"], 0)

    def test_captura_simulada_no_habilita_la_api(self):
        n = capturar(self.con, TOKEN_SIMULADO, "2026-10-21T12:00:00")
        self.assertEqual(n, 12)
        self.assertEqual(capturar(self.con, TOKEN_SIMULADO, "2026-10-21T12:00:00"), 12)
        origenes = {fila["origen"] for fila in self.con.execute("SELECT origen FROM medicion")}
        self.assertEqual(origenes, {"simulado"})
        sin_acceso = self.con.execute(
            "SELECT COUNT(*) AS n FROM sensor_municipal WHERE estado_acceso = 'sin_credencial'"
        ).fetchone()["n"]
        self.assertEqual(sin_acceso, 12)
        por_edt = {fila["edt"]: fila["estado"] for fila in evaluar(self.con)}
        self.assertEqual(por_edt["1.3.4"], "bloqueado")
        self.assertEqual(por_edt["1.4.3"], "bloqueado")

    def test_rechaza_token_distinto_del_simulado(self):
        with self.assertRaises(RegistroError):
            capturar(self.con, "credencial-del-proveedor", "2026-10-21T12:00:00")
        self.assertEqual(self.con.execute("SELECT COUNT(*) AS n FROM medicion").fetchone()["n"], 0)


class UmbralTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.con = conectar(Path(self.tmp.name) / "t.sqlite")
        crear_umbrales(self.con)

    def tearDown(self):
        self.con.close()
        self.tmp.cleanup()

    def test_clasifica_vibracion_e_inclinacion_por_nivel(self):
        self.assertEqual(nivel_umbral(self.con, "vibracion", 0.3), "normal")
        self.assertEqual(nivel_umbral(self.con, "vibracion", 0.5), "atencion")
        self.assertEqual(nivel_umbral(self.con, "vibracion", 1.2), "alerta")
        self.assertEqual(nivel_umbral(self.con, "vibracion", 3.0), "critico")
        self.assertEqual(nivel_umbral(self.con, "inclinacion", -0.25), "alerta")
        self.assertEqual(nivel_umbral(self.con, "inclinacion", 0.5), "critico")


class EstadoTest(unittest.TestCase):
    def test_estado_al_21_10_2026(self):
        tmp = tempfile.TemporaryDirectory()
        con = conectar(Path(tmp.name) / "t.sqlite")
        preparar(con, ENCABEZADO)
        por_edt = {fila["edt"]: fila["estado"] for fila in evaluar(con)}
        self.assertEqual(por_edt["1.4.2"], "atrasado_parcial")
        self.assertEqual(por_edt["1.3.4"], "bloqueado")
        self.assertEqual(por_edt["1.3.2"], "atrasado_hecho")
        self.assertEqual(por_edt["1.4.3"], "bloqueado")
        self.assertEqual(por_edt["1.4.4"], "no_iniciado")
        self.assertEqual(con.execute("SELECT COUNT(*) AS n FROM canal_publico").fetchone()["n"], 2)
        con.close()
        tmp.cleanup()


if __name__ == "__main__":
    unittest.main()
