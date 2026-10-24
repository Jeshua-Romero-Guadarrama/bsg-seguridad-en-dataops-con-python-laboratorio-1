# Comercial Nova · Laboratorio 1: protección de datos (cifrado, recuperación e integridad)

Repositorio de entrega del **Laboratorio 1 (tramo 1A, Protección e integridad)** del curso de DataOps Security, caso Comercial Nova. Autor: Jeshua Romero Guadarrama. Fecha: 23-10-2026.

Comercial Nova procesa pedidos con nombre y correo de clientes. Antes de integrar el pipeline completo, este laboratorio demuestra con funciones aisladas tres capacidades: cifrar un dato personal y recuperarlo idéntico con la misma clave, calcular la huella SHA-256 de un archivo y detectar que una copia con un solo importe cambiado ya no coincide con la referencia confiable. Todos los clientes y pedidos son ficticios.

## Objetivo del laboratorio

- Implementar TODO 1 (`calcular_hash`), TODO 3 (`cifrar`) y TODO 4 (`descifrar`) respetando los contratos del módulo original.
- Conservar TODO 2 (`autorizar`) pendiente, tal como pide [lab1.md](lab1.md): en 1A no se ejecuta todavía el pipeline. Su implementación está en el [Laboratorio 2](https://github.com/Jeshua-Romero-Guadarrama/bsg-seguridad-en-dataops-con-python-laboratorio-2).
- Verificar con `comprobar_1a.py` que el correo se recupera, que el original coincide con la referencia y que la copia alterada no coincide.
- Registrar los resultados reales en [evidencias.md](evidencias.md).

Las guías del curso se incluyen sin cambios: [preparar.md](preparar.md) y [lab1.md](lab1.md). El listado del código base original, con los cuatro TODO, aparece en esas guías; la solución de este repositorio está en los archivos `.py`.

## Estructura del repositorio

| Ruta | Contenido |
| --- | --- |
| `lab1.py` | Módulo del laboratorio con diseño orientado a objetos; TODO 1, 3 y 4 resueltos y TODO 2 pendiente |
| `preparar.py` | Clase `PreparadorEntorno`: genera dataset, referencia y clave una sola vez |
| `comprobar_1a.py` | Comprobador del tramo 1A (clase `ComprobadorLaboratorio1A`), con opción `--base` para pruebas |
| `pruebas/` | Pruebas automatizadas con pytest (51 pruebas) |
| `pytest.ini` | Configuración de pytest en español (`prueba_*.py`, `Prueba*`, `prueba_*`) |
| `evidencias.md` | Plantilla del curso rellenada con resultados observados y reflexión |
| `preparar.md`, `lab1.md` | Guías originales del curso |
| `requirements.txt` | `cryptography==50.0.2` y `pytest==9.1.1` |
| `.github/workflows/pruebas.yml` | Integración continua en Ubuntu y Windows con Python 3.12 |
| `.gitignore` | Excluye `.venv/`, `.secrets/`, `datos/`, `referencia.sha256` y cachés |

Los archivos `datos/pedidos.csv`, `datos/pedidos_prueba_parte1.csv`, `referencia.sha256` y `.secrets/fernet.key` se generan localmente y nunca se suben a Git.

## Requisitos

- Python 3.12 con `venv` y `pip`.
- Conexión a Internet para instalar las dependencias.
- Una terminal: Windows PowerShell, o bien WSL o Linux. Elige una sola alternativa y no mezcles un entorno virtual de Windows con WSL.

## Instalación

En Windows PowerShell:

```text
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

Si PowerShell bloquea la activación, no cambies las políticas del equipo. Instala con el intérprete del entorno y sustituye `python` por `.\.venv\Scripts\python.exe` en los comandos posteriores:

```text
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

En WSL o Linux:

```text
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

Comprueba la dependencia (debe mostrar 50.0.2):

```text
python --version
python -c "import cryptography; print(cryptography.__version__)"
```

## Preparar el entorno y cargar la clave

Genera el entorno una sola vez:

```text
python preparar.py
```

Resultado esperado: `Dataset, referencia y clave creados sin mostrarlos`. Si ya existe alguno de los tres archivos, el programa se detiene con `Entorno existente; revisar antes de recrear` y no reemplaza nada.

Carga la clave en la terminal actual, sin imprimirla.

En Windows PowerShell:

```text
$env:DATAOPS_KEY = (Get-Content .secrets/fernet.key -Raw).Trim()
```

En WSL o Linux:

```text
export DATAOPS_KEY="$(cat .secrets/fernet.key)"
```

Vuelve a cargarla al abrir otra terminal. No copies la clave al código, a Git, a capturas ni a las evidencias. Una clave nueva no recupera datos cifrados con otra.

## Orden exacto de comandos para reproducir

```text
python preparar.py
python lab1.py inspeccionar
python comprobar_1a.py
python lab1.py ejecutar --rol operador
python -m pytest -q
```

(Entre `preparar.py` y `inspeccionar`, carga `DATAOPS_KEY` como se indica arriba.)

## Resultados esperados

`python lab1.py inspeccionar` muestra el primer pedido ficticio (PED-1001, Cliente Prueba 001, cliente001@example.com, Villahermosa, 1850.00, Confirmado). Esta inspección omite permisos a propósito: sirve para identificar qué campos proteger.

`python comprobar_1a.py` imprime, en este orden:

```text
Recuperacion coincidente: True
Original coincide con referencia: True
Copia alterada coincide con referencia: False
Laboratorio 1A verificado
```

El comprobador crea `datos/pedidos_prueba_parte1.csv` cambiando solo 1850.00 por 1851.00. El original y `referencia.sha256` permanecen intactos.

| TODO | Función | Contrato | Estado en este repositorio |
| --- | --- | --- | --- |
| 1 | `calcular_hash` | Recibe una ruta y devuelve SHA-256 hexadecimal sobre los bytes del archivo | Resuelto |
| 2 | `autorizar` | Permite solo las operaciones de `PERMISOS`; deniega sin datos personales | Pendiente por diseño (Laboratorio 2) |
| 3 | `cifrar` | Texto, UTF-8, cifrado Fernet, token como texto ASCII | Resuelto |
| 4 | `descifrar` | Token ASCII, descifrado Fernet, texto UTF-8 original | Resuelto |

Como `autorizar` conserva el TODO 2, las acciones que lo usan terminan con código 2 y sin crear salidas:

```text
python lab1.py ejecutar --rol operador
PENDIENTE: TODO 2: autorizar
```

Lo mismo ocurre con `resumen` y `recuperar`. Los bloqueos por permisos, integridad o validación terminan con código 1 (`BLOQUEADO: ...`) y los TODO pendientes con código 2 (`PENDIENTE: ...`).

Resultados que se obtendrán en el Laboratorio 2, una vez completado el TODO 2 (tabla de lab1.md):

| Ciudad | total_ventas |
| --- | --- |
| Merida | 4000.00 |
| Puebla | 2500.00 |
| Villahermosa | 4250.00 |
| Total de control | 10750.00 |

## Pruebas automatizadas

```text
python -m pytest -q
```

Resultado observado: `51 passed`. Las pruebas no dependen de `.secrets/`, `datos/` ni `referencia.sha256` del repositorio: cada una crea un entorno completo en una carpeta temporal con `PreparadorEntorno`, inyecta su clave en `DATAOPS_KEY` sin imprimirla y ejecuta `comprobar_1a.py --base <carpeta>` y `lab1.py` como procesos con rutas temporales.

| Módulo | Qué comprueba |
| --- | --- |
| `prueba_huella.py` | SHA-256 igual a hashlib directo, estable para el mismo archivo, distinto tras alterar un byte, correcto en archivos de varios bloques |
| `prueba_cifrado.py` | Ida y vuelta, token ASCII distinto del original, token alterado y otra clave lanzan InvalidToken, tokens distintos para el mismo valor, acentos y ñ, falta de `DATAOPS_KEY` |
| `prueba_integridad.py` | Original coincide, copia con 1851.00 bloquea, la referencia no se modifica |
| `prueba_validador.py` | 12 filas válidas, columnas distintas, dataset vacío, duplicados, importe inválido, estado inválido |
| `prueba_preparar.py` | Crea los tres archivos, no reemplaza un entorno existente, 12 filas con el contrato, referencia igual a la huella |
| `prueba_comprobar_1a.py` | Las cuatro líneas exactas del comprobador y sus mensajes `REVISAR` |
| `prueba_cli.py` | `inspeccionar` funciona; `ejecutar`, `resumen` y `recuperar` terminan con código 2 y `PENDIENTE: TODO 2: autorizar` sin crear el destino |
| `prueba_pipeline.py` | Con un control de acceso simulado que permite todo, el resto del pipeline cifra, totaliza y bloquea la copia alterada sin crear destino |

## Diseño de clases

`lab1.py` conserva las funciones y constantes del módulo original (`calcular_hash`, `autorizar`, `cifrar`, `descifrar`, `cargar_cifrador`, `leer_pedidos`, `verificar_integridad`, `escribir_csv`, `ejecutar`, `consultar_resumen`, `recuperar_muestra`, `main`, `BASE`, `DATOS`, `SALIDAS`, `PERMISOS`, `CAMPOS`) como envoltorios finos que delegan en estas clases:

| Clase | Responsabilidad |
| --- | --- |
| `CalculadoraHuella` | SHA-256 hexadecimal de un archivo leído por bloques de 65536 bytes |
| `CifradorCampos` | Cifrar y descifrar texto con Fernet; `desde_entorno()` lee la clave de `DATAOPS_KEY` |
| `ControlAcceso` | Matriz de permisos por rol y operación; `autorizar` pendiente (TODO 2) hasta el Laboratorio 2 |
| `ValidadorPedidos` | Contrato de columnas, dataset no vacío, identificadores únicos, importes y estados válidos |
| `VerificadorIntegridad` | Comparar la huella de la entrada con la referencia confiable |
| `EscritorCsv` | Escribir CSV UTF-8 con encabezado |
| `PipelineNova` | Orquestar permiso, integridad, validación, cifrado y escritura; crear el destino solo tras los controles |
| `InterfazLinea` | CLI `inspeccionar`, `ejecutar`, `resumen`, `recuperar`; traduce errores a códigos 1 y 2 |
| `PreparadorEntorno` (`preparar.py`) | Generar dataset, referencia y clave sin reemplazar un entorno existente |
| `ComprobadorLaboratorio1A` (`comprobar_1a.py`) | Comprobaciones aisladas de recuperación e integridad |

## Riesgos, controles y pruebas

| Riesgo | Control | Prueba que lo demuestra |
| --- | --- | --- |
| Exposición de nombre y correo | Cifrado Fernet de campos | `comprobar_1a.py` (`Recuperacion coincidente: True`), `prueba_cifrado.py` |
| Pérdida del dato al cifrar | Recuperación con la misma clave, texto UTF-8 completo | `prueba_ida_y_vuelta`, `prueba_texto_con_acentos_y_enie` |
| Token manipulado o clave equivocada | Cifrado autenticado (InvalidToken) | `prueba_token_alterado_lanza_invalid_token`, `prueba_otra_clave_no_recupera` |
| Clave escrita en el código o ausente | Clave solo en `DATAOPS_KEY`; error explícito si falta | `prueba_falta_la_variable`, `prueba_sin_clave_pide_revisar` |
| Entrada modificada sin aviso | Huella SHA-256 frente a referencia confiable | `comprobar_1a.py` (`Copia alterada coincide con referencia: False`), `prueba_integridad.py` |
| Ocultar una alteración recalculando la referencia | La referencia nunca se reescribe al verificar | `prueba_no_modifica_la_referencia`, `prueba_original_alterado_pide_revisar` |
| Datos fuera de contrato | Validación de columnas, filas, identificadores, importes y estados | `prueba_validador.py` |
| Reemplazo accidental del entorno o de la clave | `preparar.py` se niega a sobrescribir | `prueba_no_reemplaza_si_existe` |
| Ejecutar el pipeline sin control de acceso | `autorizar` pendiente detiene la CLI con código 2 sin crear salidas | `prueba_acciones_pendientes`, `prueba_ejecutar_no_crea_el_destino` |

## Límites del laboratorio frente a producción

Este laboratorio no es una arquitectura de producción. El original permanece legible en disco y el cifrado no anonimiza los identificadores restantes. Los roles se simulan en la aplicación y un usuario con acceso local puede leer los archivos directamente. La referencia y la clave requieren protección propia. En producción haría falta:

- **Custodia y rotación de claves** en un gestor de secretos, sin archivos locales.
- **Publicación y versiones protegidas** de la referencia, independientes de quien puede modificar los datos.
- **Identidad verificada** con autenticación real y permisos del sistema, no un argumento `--rol`.
- **Auditoría** de cada ejecución, consulta y recuperación.
- **Recuperación probada** mediante respaldos restaurados periódicamente.

## Relación con el Laboratorio 2

Este repositorio cubre el tramo 1A y deja el TODO 2 pendiente por diseño. El tramo 1B (autorización por rol e integración del pipeline completo: ejecutar como operador, resumen como analista, recuperación de la muestra y pruebas de denegación e integridad) está en el repositorio del Laboratorio 2:

https://github.com/Jeshua-Romero-Guadarrama/bsg-seguridad-en-dataops-con-python-laboratorio-2

Ambos repositorios comparten el mismo diseño de clases de `lab1.py`; el Laboratorio 2 parte de 1A verificado, la misma entrada y la misma clave.

Este repositorio: https://github.com/Jeshua-Romero-Guadarrama/bsg-seguridad-en-dataops-con-python-laboratorio-1
