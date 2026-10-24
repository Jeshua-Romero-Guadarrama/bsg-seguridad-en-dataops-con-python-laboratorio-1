"""Comprobaciones aisladas del tramo 1A; no contiene la solución de los TODO.

Importa lab1.py y usa sus funciones para demostrar tres hechos:

1. Un correo cifrado con la clave local se recupera idéntico.
2. La huella del original coincide con referencia.sha256.
3. Una copia con un solo importe alterado (1850.00 -> 1851.00) ya no
   coincide. La copia se guarda en datos/pedidos_prueba_parte1.csv para
   reutilizarla en el tramo 1B.

Uso:
    python comprobar_1a.py
    python comprobar_1a.py --base <carpeta>

Sin argumentos usa lab1.BASE y lab1.DATOS, igual que el original. La opción
--base, añadida para las pruebas automatizadas, toma la entrada y la
referencia de otra carpeta preparada con preparar.py.
"""
import argparse
import sys
from pathlib import Path

import lab1


class ComprobadorLaboratorio1A:
    """Ejecuta las comprobaciones del tramo 1A e imprime sus resultados."""

    CORREO_PRUEBA = 'cliente001@example.com'

    def __init__(self, base=None):
        """Define las rutas que se van a comprobar.

        Argumentos:
            base: carpeta con datos/ y referencia.sha256; por omisión,
                lab1.BASE y lab1.DATOS.
        """
        if base is None:
            self.base, self.datos = lab1.BASE, lab1.DATOS
        else:
            self.base = Path(base)
            self.datos = self.base / 'datos'

    def comprobar(self):
        """Ejecuta las tres comprobaciones en orden.

        Lanza:
            NotImplementedError: si falta algún TODO de 1A.
            AssertionError: si una comprobación no da el resultado esperado.
            ValueError, OSError: si falta la clave o algún archivo.
        """
        self.comprobar_recuperacion()
        referencia = (self.base / 'referencia.sha256').read_text().strip()
        self.comprobar_original(referencia)
        self.comprobar_copia_alterada(referencia)
        print('Laboratorio 1A verificado')

    def comprobar_recuperacion(self):
        """Cifra y descifra un correo ficticio y compara el resultado."""
        fernet = lab1.cargar_cifrador()
        token = lab1.cifrar(self.CORREO_PRUEBA, fernet)
        recuperado = lab1.descifrar(token, fernet) == self.CORREO_PRUEBA
        print(f'Recuperacion coincidente: {recuperado}')
        assert recuperado, 'El dato recuperado no coincide'

    def comprobar_original(self, referencia):
        """Compara la huella del original con la referencia.

        Argumentos:
            referencia: huella hexadecimal confiable.
        """
        entrada = self.datos / 'pedidos.csv'
        original = lab1.calcular_hash(entrada) == referencia
        print(f'Original coincide con referencia: {original}')
        assert original, 'Revisar el original; no recalcular la referencia'

    def comprobar_copia_alterada(self, referencia):
        """Crea una copia con un importe alterado y comprueba que no coincide.

        Argumentos:
            referencia: huella hexadecimal confiable.
        """
        entrada = self.datos / 'pedidos.csv'
        copia = self.datos / 'pedidos_prueba_parte1.csv'
        contenido = entrada.read_bytes()
        alterado = contenido.replace(b'1850.00', b'1851.00', 1)
        assert alterado != contenido, 'No se encontro el importe de prueba'
        copia.write_bytes(alterado)
        coincide = lab1.calcular_hash(copia) == referencia
        print(f'Copia alterada coincide con referencia: {coincide}')
        assert not coincide, 'La alteracion no fue detectada'


def main(argv=None):
    """Interpreta --base y ejecuta las comprobaciones.

    Argumentos:
        argv: lista de argumentos; por omisión, sys.argv[1:].
    """
    parser = argparse.ArgumentParser(description='Comprobaciones de 1A.')
    parser.add_argument('--base', type=Path, default=None,
                        help='carpeta con datos/ y referencia.sha256')
    args = parser.parse_args(argv)
    ComprobadorLaboratorio1A(args.base).comprobar()


if __name__ == '__main__':
    try:
        main()
    except NotImplementedError as exc:
        sys.exit(f'PENDIENTE: {exc}')
    except (AssertionError, ValueError, OSError) as exc:
        sys.exit(f'REVISAR: {exc}')
