# HUESO — La puerta que nadie cruzó

**Un programa que obedece a cualquiera con el token es una puerta,
aunque nadie la haya cruzado.**

`actor_telegram.py` no pide quién eres: lee el texto, y si el texto
dice "reiniciar", mata el sistema. La condición que guarda la
ejecución es `ejecutar_si(True, ...)` — verdadera siempre, escrita
así en el código, 8 veces. La única llave es un token embebido en el
mismo repo que lo usa.

El ledger es la segunda mitad del hueso: 1.640 eventos y ni una sola
ejecución. El actor pasó dos días recibiendo saludos y fallando al
sondear. La ausencia de "Ejecutado" en 1.640 líneas no es una
suposición: es un conteo. Capacidad y práctica son dos medidas
distintas, y aquí divergen: la puerta existe, el cruce no está
registrado.

Lección reutilizable: **mide la capacidad en el código y la práctica
en el registro, por separado.** Un programa puede ser una puerta
abierta y, a la vez, un registro de dos días sin nadie cruzándola.
Confundirlas es afirmar de más en ambos sentidos: ni "nadie entró
nunca" (fuera de la ventana no hay registro) ni "esto se usó para
atacar" (dentro de la ventana no hay ejecución).

Cruces:

- Con la cáscara #13 (el README de FranBot-tablet miente sobre las
  claves): el token está en el repo, y eso es exactamente lo que
  convierte a este actor en una puerta abierta. Sin el token
  embebido, el código sería solo un programa que obedece a su dueño.
- Con el cuarto worker fijo (cáscara #2): otro programa sin
  autenticación, pero pasivo — devuelve un JSON fijo. Este es activo:
  ejecuta.
- Con el modelo cipher-0: un hecho medido por cáscara, no prosa.
  Aquí el hecho son dos conteos (5 comandos, 0 ejecuciones) y una
  ausencia comprobada por programa (0 comprobaciones de remitente).

Fuente: `Jaime393/FranBot-tablet`, cabeza b9c9e52d (2026-08-04);
`integrados/actor_telegram.py` y `_registro/ledger.jsonl`, leídos el
2026-11-09. Repro: `python3 ejecucion_remota_repro.py` (TODO COINCIDE).
