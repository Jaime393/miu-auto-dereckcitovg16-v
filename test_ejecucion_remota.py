#!/usr/bin/env python3
"""Tests de ejecucion_remota_repro.py.

- Fixtures sin red: el análisis del actor y el conteo del ledger se
  prueban con textos pequeños embebidos (un actor con 2 comandos y sin
  comprobación de remitente; una variante protegida que SÍ la tiene; un
  mini ledger con cabecera, errores y saludos).
- Prueba viva (con red/conector): descarga actor_telegram.py y
  ledger.jsonl del repo FranBot-tablet en la cabeza fijada y comprueba
  los números exactos medidos el 2026-11-09.
- Guardas de la semilla: el README conserva el stub íntegro como
  epígrafe; ningún archivo de la semilla contiene la cadena prohibida
  (dieciséis barra dieciséis) ni la palabra prohibida (va-lidado);
  ningún archivo contiene un valor con forma de token de
  bot de Telegram (patrón, no valor).

Uso: python3 test_ejecucion_remota.py
"""

import os
import re
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import ejecucion_remota_repro as repro

BASE = os.path.dirname(os.path.abspath(__file__))

ACTOR_MINI = '''#!/usr/bin/env python3
import time, json, requests, subprocess
TELEGRAM_BOT = "TOKEN"
TELEGRAM_CHAT = "123"

def ejecutar_si(condicion, comando):
    if condicion:
        subprocess.run(comando, shell=True, timeout=30)

def leer_mensajes():
    texto = "hola"
    if texto.strip().startswith("{"):
        data = json.loads(texto)
        if data.get("accion") == "podar_nodos_inactivos":
            ejecutar_si(True, "pkill -f nodo_")
        elif data.get("accion") == "liberar_ram":
            ejecutar_si(True, "sync && echo 3 > /proc/sys/vm/drop_caches")
    else:
        if "reiniciar" in texto.lower():
            ejecutar_si(True, "pkill -f python3 && tmux kill-session -t franbot")
'''

ACTOR_PROTEGIDO = ACTOR_MINI + '''
def leer_mensajes_protegido(updates):
    for u in updates:
        if u["message"]["from"]["id"] != 1390883480:
            continue
        texto = u["message"]["text"]
'''

LEDGER_MINI = """# Ledger del Micelio — cada nodo escribe aquí sus acciones
{"timestamp": 1785264140.6, "nodo": "actor_telegram", "accion": "Error en getUpdates: Read timed out."}
{"timestamp": 1785264145.6, "nodo": "actor_telegram", "accion": "Error en getUpdates: Read timed out."}
{"timestamp": 1785264150.6, "nodo": "actor_telegram", "accion": "Mensaje procesado: Hola"}
{"timestamp": 1785264155.6, "nodo": "nodo_1", "accion": "vivo"}
{"timestamp": 1785264160.6, "nodo": "actor_telegram", "accion": "Mensaje procesado: /start"}
"""


class TestAnalizarActor(unittest.TestCase):
    """El análisis del actor con textos pequeños, sin red."""

    def test_mini_sin_comprobacion(self):
        m = repro.analizar_actor(ACTOR_MINI)
        self.assertEqual(m["comandos_distintos"], 3)
        self.assertIn("pkill -f nodo_", m["comandos"])
        self.assertIn("sync && echo 3 > /proc/sys/vm/drop_caches",
                      m["comandos"])
        self.assertIn("pkill -f python3 && tmux kill-session -t franbot",
                      m["comandos"])
        self.assertEqual(m["llamadas_ejecutar_si_true"], 3)
        self.assertFalse(m["tiene_comprobacion_remitente"])

    def test_protegido_si_detecta(self):
        m = repro.analizar_actor(ACTOR_PROTEGIDO)
        self.assertTrue(m["tiene_comprobacion_remitente"])

    def test_blob_sha1(self):
        datos = b"hola\n"
        import hashlib
        esperado = hashlib.sha1(b"blob 5\x00hola\n").hexdigest()
        self.assertEqual(repro.blob_sha1(datos), esperado)


class TestContarLedger(unittest.TestCase):
    """El conteo del ledger con un mini ledger, sin red."""

    def test_mini(self):
        c = repro.contar_ledger(LEDGER_MINI)
        self.assertEqual(c["lineas_totales"], 6)
        self.assertEqual(c["eventos_validos"], 5)
        self.assertEqual(c["nodos_distintos"], 2)
        self.assertEqual(c["eventos_actor_telegram"], 4)
        self.assertEqual(c["errores_getupdates"], 2)
        self.assertEqual(c["mensajes_procesados"], 2)
        self.assertEqual(c["ejecuciones_registradas"], 0)
        self.assertEqual(c["recomendaciones_recibidas"], 0)


class TestVivo(unittest.TestCase):
    """Prueba viva: descarga y comprueba los números exactos."""

    def test_repro_completo(self):
        actor_texto, _ = repro.fetch(repro.ACTOR_PATH)
        self.assertIsNotNone(actor_texto, "no se pudo descargar el actor")
        ledger_texto, _ = repro.fetch(repro.LEDGER_PATH)
        self.assertIsNotNone(ledger_texto, "no se pudo descargar el ledger")
        m = repro.analizar_actor(actor_texto)
        for clave, esperado in repro.ESPERADO_ACTOR.items():
            self.assertEqual(m[clave], esperado, "actor: %s" % clave)
        c = repro.contar_ledger(ledger_texto)
        for clave, esperado in repro.ESPERADO_LEDGER.items():
            self.assertEqual(c[clave], esperado, "ledger: %s" % clave)


class TestSemilla(unittest.TestCase):
    """Guardas de la propia semilla."""

    def test_readme_conserva_stub(self):
        with open(os.path.join(BASE, "README.md"), encoding="utf-8") as fh:
            texto = fh.read()
        self.assertIn("# miu-auto-dereckcitovg16-v", texto)

    def test_sin_afirmaciones_prohibidas(self):
        for nombre in os.listdir(BASE):
            if nombre.startswith("__pycache__"):
                continue
            ruta = os.path.join(BASE, nombre)
            if not os.path.isfile(ruta):
                continue
            with open(ruta, encoding="utf-8", errors="replace") as fh:
                texto = fh.read()
            # Las cadenas prohibidas se construyen por partes para que
            # este mismo archivo no las contenga como literales.
            self.assertNotIn("16" + "/" + "16", texto, nombre)
            self.assertNotIn("val" + "idado", texto, nombre)
            self.assertNotIn("Val" + "idado", texto, nombre)

    def test_sin_valor_de_token(self):
        # Patrón de un token de bot de Telegram (dígitos:cadena larga).
        # Es un patrón, no un valor: ningún archivo debe casar con él.
        patron = re.compile(r"\b\d{8,10}:[A-Za-z0-9_-]{35}\b")
        for nombre in os.listdir(BASE):
            if nombre.startswith("__pycache__"):
                continue
            ruta = os.path.join(BASE, nombre)
            if not os.path.isfile(ruta):
                continue
            with open(ruta, encoding="utf-8", errors="replace") as fh:
                texto = fh.read()
            self.assertIsNone(patron.search(texto), nombre)


if __name__ == "__main__":
    unittest.main(verbosity=2)
