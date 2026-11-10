# Ejecución remota por Telegram sin autenticación

Epígrafe — el stub íntegro de la cáscara (README.md de
`miu-auto-dereckcitovg16-v`, 28 B, blob git 67ea7f56):

```
# miu-auto-dereckcitovg16-v
```

## La cáscara

- Repo `Jaime393/miu-auto-dereckcitovg16-v`, cáscara #14 del censo
  (`~/workspace/mineria/CENSO_MIU_AUTO_2026-11-09.md`).
- 2 commits, autor FranBot-Evolucion: "Initial commit" 67ee66bf
  (2026-08-25T17:25:38Z); "polen v133 - suelo que sostiene a otros"
  0815e693 (2026-08-25T17:42:14Z, cabeza).
- El segundo commit añadió `polen_v133.html` (844 B, blob git
  47717d47): el mismo archivo byte a byte que en las cáscaras #6–8.
- El stub no afirma nada falso: es solo el título. No hay
  corrección que hacer.

## El hecho

`integrados/actor_telegram.py` del repo `Jaime393/FranBot-tablet`
(privado; cabeza b9c9e52d, 2026-08-04T17:16:11Z; 159 archivos,
2.133.510 B) ejecuta comandos shell recibidos por mensaje de
Telegram sin comprobar quién envía el mensaje.

Cómo funciona (archivo entero leído el 2026-11-09: 96 líneas,
4.398 B, blob git 8ad55e33):

- Sondea `getUpdates` cada 5 segundos
  (`while True: leer_mensajes(); time.sleep(5)`).
- Si el texto es un JSON con `accion`, ejecuta:
  - `podar_nodos_inactivos` → `pkill -f nodo_`
  - `liberar_ram` → `sync && echo 3 > /proc/sys/vm/drop_caches`
  - `generar_nodo` → `python3 integrados/generador_rapido.py`
  - `reiniciar_sistema` → `pkill -f python3 && tmux kill-session -t franbot && tmux new-session -d -s franbot`
- Si el texto es plano, las palabras clave "generar nodo",
  "liberar ram", "podar nodos" y "reiniciar" lanzan los mismos
  comandos (reiniciar sin el `new-session`); "estado" corre `uptime`
  y `free -m` y responde el resultado.
- La función que ejecuta es `ejecutar_si(True, ...)` — la condición
  es siempre verdadera; se llama 8 veces en el archivo.
- No hay comprobación de remitente: el código lee
  `u["message"]["text"]` y nunca compara
  `u["message"]["from"]["id"]` con nada. Búsqueda de patrones
  `"from"`, `sender`, `allowed`, `whitelist`, `ADMIN`, `firma`:
  0 ocurrencias. El único `chat_id` del archivo es el destino fijo
  al que responde.
- El token del bot está embebido en el mismo archivo (línea 10,
  asignación de `TELEGRAM_BOT`); su valor no se reproduce aquí ni en
  ningún archivo de la semilla. El archivo de minería
  (`~/workspace/mineria/FranBot-tablet/CONTENIDO.md` §2) midió además
  que el mismo token aparece en los otros dos integrados
  (`orquestador_estable.py`, `escalador_dinamico.py`) y en las líneas
  de error del ledger.
- `generador_rapido.py`, que el actor invoca dos veces, no existe en
  el repo: `integrados/` tiene solo 3 archivos
  (actor_telegram.py, escalador_dinamico.py, orquestador_estable.py).

## Lo que pasó en la práctica

El ledger `_registro/ledger.jsonl` (664.211 B) cubre
2026-07-28T17:08:11Z → 2026-07-30T19:21:18Z: 1.641 líneas
(1 comentario de cabecera + 1.640 eventos), 118 nodos distintos.

- actor_telegram: 1.335 eventos; 1.323 son errores de `getUpdates`
  (timeout leyendo api.telegram.org) — el 80,7% de todos los eventos
  del ledger.
- 12 mensajes procesados, todos saludos: Hola 3, /start 4,
  Continue 2, Iniciado 1, Hi 1, Gu 1.
- 0 ejecuciones registradas ("Ejecutado" no aparece nunca);
  0 recomendaciones JSON recibidas.
- El último evento es del 2026-07-30T19:21:18Z, 4 días y 22 horas
  antes de la cabeza del repo (2026-08-04T17:16:11Z).

La capacidad es real y está en el código; la práctica no está
registrada: en la ventana que el ledger cubre, el actor solo recibió
saludos y su sondeo falló 1.323 veces.

## Cómo reproducir

`python3 ejecucion_remota_repro.py` — descarga los dos archivos en
la cabeza fijada (conector GitHub local, solo lectura; raw si el repo
fuera público) y comprueba todos los números. Sale 0 si
TODO COINCIDE.

`python3 test_ejecucion_remota.py` — 8 tests (4 sin red, 1 vivo,
3 guardas).

## Fuentes

- `Jaime393/FranBot-tablet`, cabeza b9c9e52d (2026-08-04):
  `integrados/actor_telegram.py` (96 l., 4.398 B, blob 8ad55e33),
  `_registro/ledger.jsonl` (664.211 B). Leídos por API el 2026-11-09.
- Minería ola 6: `~/workspace/mineria/FranBot-tablet/CONTENIDO.md`
  (§2, §3), `INVENTARIO.md`, `LECTURA.md` (2026-11-09).
- Cáscara: `Jaime393/miu-auto-dereckcitovg16-v`, cabeza 0815e693
  (2026-08-25); censo `~/workspace/mineria/CENSO_MIU_AUTO_2026-11-09.md`
  (#14).
