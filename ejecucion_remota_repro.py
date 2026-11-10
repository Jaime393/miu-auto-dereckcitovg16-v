#!/usr/bin/env python3
"""ejecucion_remota_repro.py — reproduce el hecho sembrado en
miu-auto-dereckcitovg16-v: `integrados/actor_telegram.py` (repo
Jaime393/FranBot-tablet, cabeza b9c9e52d, 2026-08-04) ejecuta comandos
shell recibidos por mensaje de Telegram sin comprobar quién los envía,
y el ledger `_registro/ledger.jsonl` muestra que en la ventana
registrada (2026-07-28 → 2026-07-30) nunca se ejecutó un comando.

Descarga los dos archivos por la API de GitHub (conector local, solo
lectura, cabeza fijada) o por raw.githubusercontent.com, y comprueba:
  actor: 96 líneas, 4.398 B, blob 8ad55e33, 5 comandos distintos,
         8 llamadas ejecutar_si(True, ...), 0 comprobaciones de remitente.
  ledger: 1.641 líneas (1 comentario + 1.640 eventos), 118 nodos,
          1.335 eventos de actor_telegram, 1.323 errores getUpdates,
          12 mensajes procesados, 0 ejecuciones, 0 recomendaciones.

Nunca imprime el valor del token embebido: solo cuenta líneas y
comandos. El token es un secreto del repo minado y no se reproduce.

Uso: python3 ejecucion_remota_repro.py
Sale 0 si TODO COINCIDE, 1 si algo difiere.
"""

import hashlib
import json
import subprocess
import sys
import urllib.request
from datetime import datetime, timezone

OWNER = "Jaime393"
REPO = "FranBot-tablet"
HEAD = "b9c9e52db7f6097a4375302a4aef8eb481370c04"
ACTOR_PATH = "integrados/actor_telegram.py"
LEDGER_PATH = "_registro/ledger.jsonl"

ESPERADO_ACTOR = {
    "lineas": 96,
    "bytes": 4398,
    "blob": "8ad55e3355a1ebcde4a9322e5aacc22a12c3948d",
    "comandos_distintos": 5,
    "llamadas_ejecutar_si_true": 8,
    "tiene_comprobacion_remitente": False,
}

# Los 5 comandos shell distintos que el actor puede lanzar.
COMANDOS = [
    "pkill -f nodo_",
    "sync && echo 3 > /proc/sys/vm/drop_caches",
    "python3 integrados/generador_rapido.py",
    "pkill -f python3 && tmux kill-session -t franbot && tmux new-session -d -s franbot",
    "pkill -f python3 && tmux kill-session -t franbot",
]

# Patrones que indicarían una comprobación de quién envía el mensaje.
# El "from" de "from pathlib import Path" no cuenta: se busca '"from"'.
PATRONES_REMITENTE = [
    '"from"', "'from'", "from_id", "sender", "allowed",
    "whitelist", "AUTHORIZED", "ADMIN", "firma",
    "verificar_remitente",
]

ESPERADO_LEDGER = {
    "lineas_totales": 1641,
    "eventos_validos": 1640,
    "nodos_distintos": 118,
    "eventos_actor_telegram": 1335,
    "errores_getupdates": 1323,
    "mensajes_procesados": 12,
    "ejecuciones_registradas": 0,
    "recomendaciones_recibidas": 0,
    "primer_evento": "2026-07-28T17:08:11.448445+00:00",
    "ultimo_evento": "2026-07-30T19:21:18.329029+00:00",
}


def blob_sha1(datos: bytes) -> str:
    """SHA-1 del objeto blob de git para estos bytes."""
    cabecera = b"blob " + str(len(datos)).encode() + b"\x00"
    return hashlib.sha1(cabecera + datos).hexdigest()


def fetch_por_raw(path: str):
    """Descarga por raw.githubusercontent.com (sin auth; falla si el
    repo es privado). Devuelve el texto o None."""
    url = ("https://raw.githubusercontent.com/%s/%s/%s/%s"
           % (OWNER, REPO, HEAD, path))
    try:
        with urllib.request.urlopen(url, timeout=30) as resp:
            return resp.read().decode("utf-8")
    except Exception:
        return None


def fetch_por_cli(path: str):
    """Descarga por el conector GitHub local (solo lectura, cabeza
    fijada). Devuelve el texto o None."""
    try:
        out = subprocess.run(
            ["/opt/hatch/bin/github", "call-read-tool",
             "--name", "get_file_contents", "--arguments-json",
             json.dumps({"owner": OWNER, "repo": REPO,
                         "path": path, "ref": HEAD})],
            capture_output=True, text=True, timeout=120)
        d = json.loads(out.stdout)
        for c in d["result"]["content"]:
            if "resource" in c:
                return c["resource"].get("text")
    except Exception:
        return None
    return None


def fetch(path: str):
    """Primero raw (público), luego el conector (privado)."""
    texto = fetch_por_raw(path)
    if texto is not None:
        return texto, "raw"
    texto = fetch_por_cli(path)
    if texto is not None:
        return texto, "conector"
    return None, None


def analizar_actor(texto: str) -> dict:
    """Mide el actor: tamaño, comandos, llamadas y comprobación."""
    datos = texto.encode()
    comandos = [c for c in COMANDOS if c in texto]
    return {
        "lineas": len(texto.splitlines()),
        "bytes": len(datos),
        "blob": blob_sha1(datos),
        "comandos_distintos": len(comandos),
        "comandos": comandos,
        "llamadas_ejecutar_si_true": texto.count("ejecutar_si(True,"),
        "tiene_comprobacion_remitente": any(
            p in texto for p in PATRONES_REMITENTE),
    }


def contar_ledger(texto: str) -> dict:
    """Cuenta el ledger línea por línea. La primera línea es un
    comentario (# Ledger del Micelio...), no un evento JSON."""
    lineas = texto.splitlines()
    eventos = []
    for ln in lineas:
        ln = ln.strip()
        if not ln:
            continue
        try:
            eventos.append(json.loads(ln))
        except ValueError:
            continue
    actor = [e for e in eventos if e.get("nodo") == "actor_telegram"]
    marcas = [e.get("timestamp") for e in eventos
              if isinstance(e.get("timestamp"), (int, float))]
    primero = (datetime.fromtimestamp(min(marcas), timezone.utc).isoformat()
               if marcas else None)
    ultimo = (datetime.fromtimestamp(max(marcas), timezone.utc).isoformat()
              if marcas else None)
    return {
        "lineas_totales": len(lineas),
        "eventos_validos": len(eventos),
        "nodos_distintos": len({e.get("nodo") for e in eventos}),
        "eventos_actor_telegram": len(actor),
        "errores_getupdates": sum(
            1 for e in actor if "getUpdates" in str(e.get("accion", ""))),
        "mensajes_procesados": sum(
            1 for e in actor
            if str(e.get("accion", "")).startswith("Mensaje procesado")),
        "ejecuciones_registradas": sum(
            1 for e in eventos if "Ejecutado" in str(e.get("accion", ""))),
        "recomendaciones_recibidas": sum(
            1 for e in eventos
            if "Recomendación recibida" in str(e.get("accion", ""))),
        "primer_evento": primero,
        "ultimo_evento": ultimo,
    }


def main() -> int:
    actor_texto, via_actor = fetch(ACTOR_PATH)
    if actor_texto is None:
        print("FALLO: no se pudo descargar %s" % ACTOR_PATH)
        return 1
    ledger_texto, via_ledger = fetch(LEDGER_PATH)
    if ledger_texto is None:
        print("FALLO: no se pudo descargar %s" % LEDGER_PATH)
        return 1
    print("Descargado por %s: %s (%d B)" % (via_actor, ACTOR_PATH,
                                            len(actor_texto.encode())))
    print("Descargado por %s: %s (%d B)" % (via_ledger, LEDGER_PATH,
                                            len(ledger_texto.encode())))

    medido_actor = analizar_actor(actor_texto)
    medido_ledger = contar_ledger(ledger_texto)
    ok = True

    print("--- actor_telegram.py ---")
    for clave, esperado in ESPERADO_ACTOR.items():
        medido = medido_actor[clave]
        coincide = medido == esperado
        ok = ok and coincide
        print("%s: medido=%r esperado=%r %s"
              % (clave, medido, esperado,
                 "OK" if coincide else "DIFIERE"))
    print("comandos encontrados:")
    for c in medido_actor["comandos"]:
        print("  - %s" % c)

    print("--- ledger.jsonl ---")
    for clave, esperado in ESPERADO_LEDGER.items():
        medido = medido_ledger[clave]
        coincide = medido == esperado
        ok = ok and coincide
        print("%s: medido=%r esperado=%r %s"
              % (clave, medido, esperado,
                 "OK" if coincide else "DIFIERE"))

    print("TODO COINCIDE" if ok else "DIFERENCIAS ENCONTRADAS")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
