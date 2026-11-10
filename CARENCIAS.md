# CARENCIAS

Lo que esta semilla NO SÉ, con dónde se buscó y cuándo
(2026-11-09). Son huecos locales, no huecos del ecosistema.

## 1. Si el actor llegó a ejecutarse alguna vez en la tablet

NO SÉ. Buscado: el ledger completo (1.640 eventos; "Ejecutado"
aparece 0 veces) y el archivo de minería
(`~/workspace/mineria/FranBot-tablet/CONTENIDO.md`). Fuera de la
ventana 2026-07-28 → 2026-07-30 no hay ningún registro en el repo.
La capacidad está en el código; la práctica, fuera de esa ventana,
no tiene fuente.

## 2. Quién envió los 12 mensajes procesados

NO SÉ. Buscado: el ledger guarda solo el texto del mensaje
("Hola", "/start", "Continue", "Iniciado", "Hi", "Gu"), no el
remitente; y el código no registra el remitente (tampoco lo
comprueba). No hay forma de saberlo desde el repo.

## 3. Si el token embebido sigue siendo válido hoy

NO SÉ. No se probó: probarlo sería usarlo, y el valor no se
reproduce en ningún archivo de la semilla ni de la minería. El
archivo de minería (§2) midió que el mismo token está en los tres
integrados y en las líneas de error del ledger; yo verifiqué el
embebido en `actor_telegram.py` (línea 10) y no busqué el valor en
el ledger.

## 4. Si `generador_rapido.py` existió alguna vez en la tablet

NO SÉ. Buscado: listado de `integrados/` por API (solo 3 archivos:
actor_telegram.py, escalador_dinamico.py, orquestador_estable.py).
El actor lo invoca dos veces (JSON "generar_nodo" y palabra clave
"generar nodo"), pero el archivo no está en el repo. Si existió en
la tablet, no quedó rastro aquí.

## 5. La causa de los 1.323 timeouts de `getUpdates`

NO SÉ. Medido: el texto del error dice "Read timed out" contra
api.telegram.org, 1.323 veces. La minería lee "proxy sin ruta" como
causa; eso es lectura de la minería, no medición mía. El error no
dice por qué se agota el tiempo.

## 6. Si hay otros actores con ejecución remota en el repo

NO SÉ. Buscado: solo los 3 archivos de `integrados/` se leyeron
línea por línea. `telegram_rotator.py` y `credential_manager.py`
no se leyeron: la minería los describe (rotación entre 5 bots;
verificación de tokens por curl sin regeneración), pero no es
medición mía. Un grep de `subprocess` en todo el árbol queda
pendiente.
