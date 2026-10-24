# Evidencias del laboratorio 1

Participante: Jeshua Romero Guadarrama  Fecha: 23-10-2026

Registra lo que observaste realmente. No pegues claves, tokens ni datos recuperados.

| Prueba | Resultado esperado | Resultado observado | Explicación o corrección |
| --- | --- | --- | --- |
| Recuperar correo en 1A | True | True (`Recuperacion coincidente: True`) | El correo ficticio se cifró con la clave local cargada en DATAOPS_KEY y al descifrar el token se obtuvo el mismo texto; el cifrado protege el dato sin perderlo. |
| Comparar original | True | True (`Original coincide con referencia: True`) | El SHA-256 calculado por bloques sobre datos/pedidos.csv es igual a referencia.sha256; el original no cambió desde el alta. |
| Comparar copia alterada | False | False (`Copia alterada coincide con referencia: False`) | La copia datos/pedidos_prueba_parte1.csv solo cambia 1850.00 por 1851.00, pero cualquier byte distinto produce otra huella; la alteración se detecta y la referencia no se recalculó. El comprobador terminó con `Laboratorio 1A verificado`. |
| Ejecutar como operador | 12 filas | No aplica en este laboratorio; ver bsg-seguridad-en-dataops-con-python-laboratorio-2 | En 1A autorizar conserva el TODO 2, así que el comando termina con `PENDIENTE: TODO 2: autorizar` (código 2) y no crea salidas. |
| Consultar como analista | 3 ciudades y total 10750.00 | No aplica en este laboratorio; ver bsg-seguridad-en-dataops-con-python-laboratorio-2 | Requiere el control de acceso del tramo 1B; en 1A la consulta queda pendiente. |
| Recuperar como operador | Muestra ficticia coincidente | No aplica en este laboratorio; ver bsg-seguridad-en-dataops-con-python-laboratorio-2 | La recuperación del pipeline depende de autorizar; la recuperación aislada sí se demostró arriba con comprobar_1a.py. |
| Ejecutar como analista | Bloqueado sin destino nuevo | No aplica en este laboratorio; ver bsg-seguridad-en-dataops-con-python-laboratorio-2 | La denegación por rol es objeto del tramo 1B. |
| Ejecutar con rol desconocido | Bloqueado sin destino nuevo | No aplica en este laboratorio; ver bsg-seguridad-en-dataops-con-python-laboratorio-2 | La denegación de roles desconocidos es objeto del tramo 1B. |
| Recuperar como auditor | Bloqueado | No aplica en este laboratorio; ver bsg-seguridad-en-dataops-con-python-laboratorio-2 | La denegación al auditor es objeto del tramo 1B. |
| Procesar copia alterada | Bloqueado sin salidas/alterada | No aplica en este laboratorio; ver bsg-seguridad-en-dataops-con-python-laboratorio-2 | El bloqueo dentro del pipeline se prueba en 1B; en 1A la alteración ya se detectó al comparar huellas. |

## Archivos de salida

Destino válido utilizado: ninguno. En el tramo 1A no se generan salidas del pipeline: `python lab1.py ejecutar --rol operador` termina con `PENDIENTE: TODO 2: autorizar` y no crea salidas/lab1. El único archivo nuevo es datos/pedidos_prueba_parte1.csv, la copia alterada que crea comprobar_1a.py para reutilizarla en 1B; está excluida de Git junto con datos/.

Filas de detalle: no aplica (sin ejecución del pipeline)  Filas de resumen: no aplica (sin ejecución del pipeline)

Totales observados por ciudad: no aplica en 1A; los totales se obtienen en el Laboratorio 2.

Comandos ejecutados en este repositorio y salida observada:

| Comando | Salida observada | Código de salida |
| --- | --- | --- |
| `python preparar.py` | `Dataset, referencia y clave creados sin mostrarlos` | 0 |
| `python preparar.py` (segunda vez) | `FileExistsError: Entorno existente; revisar antes de recrear` | 1 |
| `python comprobar_1a.py` | Las cuatro líneas esperadas, en orden | 0 |
| `python comprobar_1a.py` sin DATAOPS_KEY | `REVISAR: Falta DATAOPS_KEY en el entorno` | 1 |
| `python lab1.py inspeccionar` | Primer pedido ficticio (PED-1001, Villahermosa, 1850.00, Confirmado) | 0 |
| `python lab1.py ejecutar --rol operador` | `PENDIENTE: TODO 2: autorizar`, sin crear salidas/ | 2 |
| `python lab1.py resumen --rol operador` | `PENDIENTE: TODO 2: autorizar` | 2 |
| `python lab1.py recuperar --rol operador` | `PENDIENTE: TODO 2: autorizar` | 2 |
| `python -m pytest -q` | `51 passed` | 0 |

## Reflexión

1. ¿Qué protege cada control y qué prueba lo demuestra?

   En 1A intervienen dos controles. El cifrado Fernet protege la confidencialidad de nombre y correo: quien vea el token no puede leer el dato sin la clave, y quien tenga la clave lo recupera intacto; lo demuestra `Recuperacion coincidente: True` y las pruebas que comprueban la ida y vuelta, que el token no contiene el correo, que dos cifrados del mismo valor dan tokens distintos y que un token alterado se rechaza con InvalidToken. La huella SHA-256 protege la integridad de la entrada: permite saber si el CSV es exactamente el que se dio de alta; lo demuestran `Original coincide con referencia: True` y `Copia alterada coincide con referencia: False`, donde un solo dígito cambiado basta para que la comparación falle. El tercer control, la autorización por rol, queda pendiente a propósito y se demuestra en el Laboratorio 2.

2. ¿Por qué no debes recalcular la referencia ante una alteración?

   La referencia vale porque se calculó sobre datos conocidos y confiables en el alta inicial. Si al ver que la copia no coincide se recalcula la referencia, la nueva huella describe el archivo sospechoso y el control pasa a aprobar justo lo que debía detener: la evidencia de la alteración desaparece. Ante un fallo lo correcto es detener el proceso, conservar el archivo y revisar su origen; la referencia solo se renueva mediante un alta nueva y autorizada de datos verificados.

3. ¿Por qué --rol no equivale a autenticar una identidad?

   `--rol` es un texto que cualquiera puede escribir en la línea de comandos; el programa no comprueba contraseña, certificado ni sesión, así que solo simula una identidad que se supone ya autenticada. Además, quien tiene acceso local puede abrir los archivos directamente sin pasar por lab1.py. En este repositorio el control ni siquiera decide todavía, porque autorizar conserva el TODO 2; en el Laboratorio 2 la matriz de permisos limita las operaciones de la aplicación, pero seguirá sin probar quién es la persona que la ejecuta.

4. ¿Qué riesgos quedan en el original, los identificadores y la clave?

   El original datos/pedidos.csv sigue en claro en el disco, con nombres y correos legibles, y la copia alterada también. Los identificadores pedido_id y cliente_id, la ciudad y el importe no se cifran, por lo que permiten enlazar pedidos de un mismo cliente: el cifrado protege campos concretos, no anonimiza el dataset. La clave está en un archivo local y en una variable de entorno; quien la obtenga descifra todo, y si se pierde no hay forma de recuperar los tokens. La referencia vive junto a los datos, de modo que quien pueda modificar ambos archivos podría hacer coincidir una alteración.

5. ¿Qué añadirías para utilizar este enfoque en producción?

   Añadiría custodia y rotación de claves en un gestor de secretos o un servicio de claves, con acceso registrado y sin archivos en el equipo del operador; publicación de la referencia en un lugar protegido e independiente, con versiones firmadas o inmutables; identidad verificada con autenticación real y permisos del sistema de archivos o de la plataforma en lugar de un argumento de línea de comandos; auditoría de cada ejecución, consulta y recuperación; y respaldos con recuperación probada. El siguiente paso inmediato, ya dentro del curso, es completar el control de acceso y conectar todos los controles en el pipeline, que es lo que resuelve el Laboratorio 2.
