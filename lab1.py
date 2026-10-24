"""Pipeline protegido de pedidos de Comercial Nova (Laboratorio 1, tramo 1A).

Este módulo resuelve el tramo 1A del laboratorio: calcula la huella SHA-256
de la entrada, cifra y descifra campos personales con Fernet y verifica la
integridad del CSV frente a una referencia confiable. El control de acceso
(TODO 2) se conserva pendiente a propósito, tal como indica lab1.md, y se
resuelve en el Laboratorio 2 (repositorio bsg-seguridad-en-dataops-con-python-laboratorio-2).

Las funciones del módulo original (calcular_hash, cifrar, descifrar,
ejecutar, etc.) se conservan con el mismo nombre, parámetros y contrato, y
delegan en las clases definidas aquí.

Uso:
    python lab1.py inspeccionar
    python lab1.py ejecutar --rol operador   (termina con PENDIENTE en 1A)
"""
import argparse
import csv
import hashlib
import json
import os
from decimal import Decimal, InvalidOperation
from pathlib import Path

from cryptography.fernet import Fernet

BASE = Path(__file__).resolve().parent
DATOS = BASE / 'datos'
SALIDAS = BASE / 'salidas'
PERMISOS = {
    'operador': {'ejecutar', 'recuperar'},
    'analista': {'resumen'},
    'auditor': {'evidencias'},
}
CAMPOS = [
    'pedido_id', 'cliente_id', 'nombre_cliente',
    'correo', 'ciudad', 'importe', 'estado',
]
CAMPOS_PROTEGIDOS = ('nombre_cliente', 'correo')
ESTADOS_VALIDOS = frozenset({'Confirmado', 'Cancelado'})


class CalculadoraHuella:
    """Calcula la huella SHA-256 de un archivo.

    Lee el archivo por bloques para no cargarlo completo en memoria, de modo
    que sirve igual para un CSV pequeño que para uno de varios gigabytes. Los
    mismos bytes en el mismo orden producen siempre la misma huella.
    """

    TAMANO_BLOQUE = 65536

    def calcular(self, ruta):
        """Devuelve la huella SHA-256 hexadecimal de un archivo.

        Argumentos:
            ruta: ruta del archivo (str o Path).

        Devuelve:
            Cadena hexadecimal de 64 caracteres.

        Lanza:
            OSError: si el archivo no existe o no se puede leer.
        """
        huella = hashlib.sha256()
        with Path(ruta).open('rb') as archivo:
            for bloque in iter(lambda: archivo.read(self.TAMANO_BLOQUE), b''):
                huella.update(bloque)
        return huella.hexdigest()


class CifradorCampos:
    """Cifra y descifra campos de texto con un objeto Fernet.

    El cifrado es simétrico y autenticado: quien tenga la misma clave puede
    recuperar el valor original, y un token alterado se rechaza con
    InvalidToken. La clave nunca se imprime ni se guarda en el código.
    """

    def __init__(self, fernet):
        """Crea el cifrador a partir de un Fernet ya construido.

        Argumentos:
            fernet: instancia de cryptography.fernet.Fernet.
        """
        self.fernet = fernet

    @classmethod
    def desde_entorno(cls, variable='DATAOPS_KEY'):
        """Construye el cifrador con la clave de una variable de entorno.

        Argumentos:
            variable: nombre de la variable que contiene la clave Fernet.

        Devuelve:
            Instancia de CifradorCampos.

        Lanza:
            ValueError: si la variable no existe o está vacía.
        """
        clave = os.environ.get(variable)
        if not clave:
            raise ValueError('Falta DATAOPS_KEY en el entorno')
        return cls(Fernet(clave.encode('ascii')))

    def cifrar(self, valor):
        """Cifra un texto y devuelve el token como texto ASCII.

        Argumentos:
            valor: texto original (str), puede contener acentos.

        Devuelve:
            Token Fernet en texto ASCII.
        """
        return self.fernet.encrypt(valor.encode('utf-8')).decode('ascii')

    def descifrar(self, token):
        """Descifra un token ASCII y devuelve el texto UTF-8 original.

        Argumentos:
            token: token Fernet en texto ASCII.

        Devuelve:
            Texto original.

        Lanza:
            cryptography.fernet.InvalidToken: si el token fue alterado o
                se cifró con otra clave.
        """
        return self.fernet.decrypt(token.encode('ascii')).decode('utf-8')


class ControlAcceso:
    """Matriz de permisos por rol y operación.

    En el Laboratorio 1 (tramo 1A) la autorización se conserva pendiente a
    propósito: lab1.md pide no completar el TODO 2 hasta el tramo 1B.
    """

    def __init__(self, permisos=None):
        """Crea el control con una matriz de permisos.

        Argumentos:
            permisos: dict rol -> conjunto de operaciones; por omisión,
                la constante PERMISOS del módulo.
        """
        self.permisos = PERMISOS if permisos is None else permisos

    def autorizar(self, rol, operacion):
        """Autoriza una operación para un rol (pendiente en este laboratorio).

        TODO 2: la implementación corresponde al Laboratorio 2 (tramo 1B),
        disponible en el repositorio bsg-seguridad-en-dataops-con-python-laboratorio-2:
        https://github.com/Jeshua-Romero-Guadarrama/bsg-seguridad-en-dataops-con-python-laboratorio-2
        Allí devuelve True si el rol tiene la operación y lanza
        PermissionError, sin datos personales, en cualquier otro caso.

        Argumentos:
            rol: rol simulado que solicita la operación.
            operacion: nombre de la operación solicitada.

        Lanza:
            NotImplementedError: siempre, porque el TODO 2 sigue pendiente.
        """
        raise NotImplementedError('TODO 2: autorizar')


class ValidadorPedidos:
    """Lee un CSV de pedidos y valida su contrato de datos.

    Comprueba el orden exacto de columnas, que haya filas, que los
    identificadores sean únicos, que los importes sean decimales finitos y
    no negativos y que el estado sea Confirmado o Cancelado.
    """

    def __init__(self, campos=None):
        """Crea el validador con un contrato de columnas.

        Argumentos:
            campos: lista ordenada de columnas; por omisión, CAMPOS.
        """
        self.campos = list(CAMPOS if campos is None else campos)

    def leer(self, ruta):
        """Lee y valida el CSV de pedidos.

        Argumentos:
            ruta: ruta del CSV (str o Path).

        Devuelve:
            Lista de filas como diccionarios.

        Lanza:
            ValueError: si el archivo incumple el contrato.
            OSError: si el archivo no se puede leer.
        """
        with Path(ruta).open(encoding='utf-8', newline='') as archivo:
            lector = csv.DictReader(archivo)
            if lector.fieldnames != self.campos:
                raise ValueError('Columnas distintas del contrato')
            filas = list(lector)
        if not filas:
            raise ValueError('Dataset vacio')
        identificadores = [fila['pedido_id'] for fila in filas]
        if len(identificadores) != len(set(identificadores)):
            raise ValueError('Identificadores duplicados')
        for fila in filas:
            self._validar_fila(fila)
        return filas

    @staticmethod
    def _validar_fila(fila):
        try:
            monto = Decimal(fila['importe'])
        except (InvalidOperation, TypeError):
            raise ValueError('Importe invalido') from None
        if not monto.is_finite() or monto < 0:
            raise ValueError('Importe invalido')
        if fila['estado'] not in ESTADOS_VALIDOS:
            raise ValueError('Estado invalido')


class VerificadorIntegridad:
    """Compara la huella de la entrada con una referencia confiable."""

    def __init__(self, calculadora=None):
        """Crea el verificador.

        Argumentos:
            calculadora: CalculadoraHuella a usar; por omisión, una nueva.
        """
        self.calculadora = calculadora or CalculadoraHuella()

    def verificar(self, entrada, referencia):
        """Verifica que la entrada coincida con la huella de referencia.

        La referencia nunca se recalcula: si no coincide, el proceso se
        detiene.

        Argumentos:
            entrada: ruta del archivo a verificar.
            referencia: ruta del archivo con la huella hexadecimal esperada.

        Devuelve:
            Huella SHA-256 de la entrada.

        Lanza:
            ValueError: si la huella no coincide con la referencia.
            OSError: si alguno de los archivos no se puede leer.
        """
        esperado = Path(referencia).read_text(encoding='ascii').strip()
        actual = self.calculadora.calcular(entrada)
        if actual != esperado:
            raise ValueError('Integridad de entrada no valida')
        return actual


class EscritorCsv:
    """Escribe filas en un CSV UTF-8 con encabezado."""

    @staticmethod
    def escribir(ruta, campos, filas):
        """Escribe el encabezado y las filas en un CSV.

        Argumentos:
            ruta: ruta del archivo de salida.
            campos: lista ordenada de columnas.
            filas: iterable de diccionarios con esas columnas.
        """
        with Path(ruta).open('w', encoding='utf-8', newline='') as archivo:
            escritor = csv.DictWriter(archivo, fieldnames=campos)
            escritor.writeheader()
            escritor.writerows(filas)


class PipelineNova:
    """Orquesta los controles del pipeline de pedidos.

    Orden obligatorio de ejecutar: permiso, integridad, validación, cifrado y
    escritura. El destino se crea solo después de superar los controles, de
    modo que un bloqueo nunca deja un destino nuevo.
    """

    def __init__(self, control_acceso=None, validador=None, verificador=None,
                 cifrador=None):
        """Crea el pipeline con sus colaboradores.

        Argumentos:
            control_acceso: ControlAcceso; por omisión, uno con PERMISOS.
            validador: ValidadorPedidos; por omisión, uno con CAMPOS.
            verificador: VerificadorIntegridad; por omisión, uno nuevo.
            cifrador: CifradorCampos; si se omite, se construye desde
                DATAOPS_KEY en el momento de cifrar o descifrar.
        """
        self.control_acceso = control_acceso or ControlAcceso()
        self.validador = validador or ValidadorPedidos()
        self.verificador = verificador or VerificadorIntegridad()
        self._cifrador = cifrador

    @property
    def cifrador(self):
        """Cifrador en uso, cargado desde el entorno si no se inyectó."""
        if self._cifrador is None:
            self._cifrador = CifradorCampos.desde_entorno()
        return self._cifrador

    def ejecutar(self, rol, entrada, referencia, destino):
        """Procesa la entrada y escribe el detalle protegido y el resumen.

        Argumentos:
            rol: rol simulado que ejecuta.
            entrada: CSV de pedidos.
            referencia: archivo con la huella confiable de la entrada.
            destino: carpeta nueva para las salidas.

        Devuelve:
            dict con hash_entrada, filas, detalle y resumen.

        Lanza:
            NotImplementedError: mientras autorizar siga pendiente (TODO 2).
            PermissionError, ValueError, OSError: si falla un control o el
                destino ya existe.
        """
        self.control_acceso.autorizar(rol, 'ejecutar')
        hash_entrada = self.verificador.verificar(entrada, referencia)
        filas = self.validador.leer(entrada)
        protegidas, totales = self._proteger_y_totalizar(filas)
        destino = Path(destino)
        destino.mkdir(parents=True, exist_ok=False)
        detalle = destino / 'detalle_protegido.csv'
        resumen = destino / 'resumen.csv'
        EscritorCsv.escribir(detalle, CAMPOS, protegidas)
        EscritorCsv.escribir(resumen, ['ciudad', 'total_ventas'], [
            {'ciudad': ciudad, 'total_ventas': f'{total:.2f}'}
            for ciudad, total in sorted(totales.items())
        ])
        return {
            'hash_entrada': hash_entrada,
            'filas': len(filas),
            'detalle': detalle,
            'resumen': resumen,
        }

    def _proteger_y_totalizar(self, filas):
        cifrador = self.cifrador
        protegidas, totales = [], {}
        for fila in filas:
            copia = dict(fila)
            for campo in CAMPOS_PROTEGIDOS:
                copia[campo] = cifrador.cifrar(fila[campo])
            protegidas.append(copia)
            if fila['estado'] == 'Confirmado':
                ciudad = fila['ciudad']
                totales[ciudad] = (
                    totales.get(ciudad, Decimal('0'))
                    + Decimal(fila['importe'])
                )
        return protegidas, totales

    def consultar_resumen(self, rol, destino):
        """Devuelve el texto del resumen por ciudad.

        Argumentos:
            rol: rol simulado que consulta.
            destino: carpeta de una ejecución válida.

        Devuelve:
            Contenido de resumen.csv.

        Lanza:
            NotImplementedError: mientras autorizar siga pendiente (TODO 2).
            PermissionError, OSError: si el rol no puede o falta el archivo.
        """
        self.control_acceso.autorizar(rol, 'resumen')
        return (Path(destino) / 'resumen.csv').read_text(encoding='utf-8')

    def recuperar_muestra(self, rol, destino):
        """Descifra los campos protegidos de la primera fila del detalle.

        Argumentos:
            rol: rol simulado que recupera.
            destino: carpeta de una ejecución válida.

        Devuelve:
            dict con nombre_cliente y correo descifrados.

        Lanza:
            NotImplementedError: mientras autorizar siga pendiente (TODO 2).
            PermissionError, ValueError, OSError: si falla un control.
        """
        self.control_acceso.autorizar(rol, 'recuperar')
        ruta = Path(destino) / 'detalle_protegido.csv'
        fila = self.validador.leer(ruta)[0]
        cifrador = self.cifrador
        return {
            campo: cifrador.descifrar(fila[campo])
            for campo in CAMPOS_PROTEGIDOS
        }


class InterfazLinea:
    """Interfaz de línea de comandos del laboratorio.

    Traduce NotImplementedError a salida 2 con PENDIENTE y los bloqueos
    (PermissionError, ValueError, OSError) a salida 1 con BLOQUEADO.
    """

    ACCIONES = ('inspeccionar', 'ejecutar', 'resumen', 'recuperar')

    def __init__(self, pipeline=None):
        """Crea la interfaz.

        Argumentos:
            pipeline: PipelineNova a usar; por omisión, uno nuevo.
        """
        self.pipeline = pipeline or PipelineNova()
        self.parser = self.construir_parser()

    def construir_parser(self):
        """Construye el analizador de argumentos con sus valores por omisión.

        Devuelve:
            argparse.ArgumentParser configurado.
        """
        parser = argparse.ArgumentParser(
            description='Pipeline protegido de pedidos de Comercial Nova.')
        parser.add_argument('accion', choices=list(self.ACCIONES))
        parser.add_argument('--rol', default='operador')
        parser.add_argument('--entrada', type=Path,
                            default=DATOS / 'pedidos.csv')
        parser.add_argument('--referencia', type=Path,
                            default=BASE / 'referencia.sha256')
        parser.add_argument('--destino', type=Path,
                            default=SALIDAS / 'lab1')
        return parser

    def ejecutar(self, argv=None):
        """Interpreta los argumentos y ejecuta la acción solicitada.

        Argumentos:
            argv: lista de argumentos; por omisión, sys.argv[1:].

        Lanza:
            SystemExit: con código 2 si hay un TODO pendiente y con código 1
                si un control bloquea la operación.
        """
        args = self.parser.parse_args(argv)
        try:
            self._despachar(args)
        except NotImplementedError as exc:
            self.parser.exit(2, f'PENDIENTE: {exc}\n')
        except (PermissionError, ValueError, OSError) as exc:
            self.parser.exit(1, f'BLOQUEADO: {exc}\n')

    def _despachar(self, args):
        if args.accion == 'inspeccionar':
            # Diagnóstico previo con datos ficticios; omite permisos a propósito.
            print(json.dumps(self.pipeline.validador.leer(args.entrada)[0],
                             ensure_ascii=False, indent=2))
        elif args.accion == 'ejecutar':
            r = self.pipeline.ejecutar(args.rol, args.entrada,
                                       args.referencia, args.destino)
            print(f"Proceso terminado: {r['filas']} filas")
        elif args.accion == 'resumen':
            print(self.pipeline.consultar_resumen(args.rol, args.destino))
        else:
            print(json.dumps(self.pipeline.recuperar_muestra(
                args.rol, args.destino), ensure_ascii=False))


def calcular_hash(ruta):
    """Devuelve el SHA-256 hexadecimal del archivo (TODO 1)."""
    return CalculadoraHuella().calcular(ruta)


def autorizar(rol, operacion):
    """Autoriza una operación; pendiente hasta el Laboratorio 2 (TODO 2)."""
    return ControlAcceso().autorizar(rol, operacion)


def cifrar(valor, fernet):
    """Cifra un texto con el Fernet recibido y devuelve un token ASCII (TODO 3)."""
    return CifradorCampos(fernet).cifrar(valor)


def descifrar(token, fernet):
    """Descifra un token ASCII con el Fernet recibido (TODO 4)."""
    return CifradorCampos(fernet).descifrar(token)


def cargar_cifrador():
    """Devuelve el Fernet construido con la clave de DATAOPS_KEY."""
    return CifradorCampos.desde_entorno().fernet


def leer_pedidos(ruta):
    """Lee y valida el CSV de pedidos con el contrato CAMPOS."""
    return ValidadorPedidos().leer(ruta)


def verificar_integridad(entrada, referencia):
    """Compara la huella de la entrada con la referencia confiable."""
    return VerificadorIntegridad().verificar(entrada, referencia)


def escribir_csv(ruta, campos, filas):
    """Escribe filas en un CSV UTF-8 con encabezado."""
    EscritorCsv.escribir(ruta, campos, filas)


def ejecutar(rol, entrada, referencia, destino):
    """Ejecuta el pipeline completo y devuelve el dict de resultados."""
    return PipelineNova().ejecutar(rol, entrada, referencia, destino)


def consultar_resumen(rol, destino):
    """Devuelve el resumen por ciudad de una ejecución válida."""
    return PipelineNova().consultar_resumen(rol, destino)


def recuperar_muestra(rol, destino):
    """Descifra la primera muestra ficticia de una ejecución válida."""
    return PipelineNova().recuperar_muestra(rol, destino)


def main():
    """Punto de entrada de la línea de comandos."""
    InterfazLinea().ejecutar()


if __name__ == '__main__':
    main()
