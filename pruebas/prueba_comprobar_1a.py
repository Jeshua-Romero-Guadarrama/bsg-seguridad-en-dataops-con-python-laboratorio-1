"""Pruebas del comprobador del tramo 1A ejecutado como proceso."""
import os
import subprocess
import sys

from pruebas.conftest import RAIZ_REPOSITORIO

SALIDA_ESPERADA = [
    'Recuperacion coincidente: True',
    'Original coincide con referencia: True',
    'Copia alterada coincide con referencia: False',
    'Laboratorio 1A verificado',
]


def ejecutar_comprobador(base, clave):
    """Ejecuta comprobar_1a.py con --base y la clave indicada."""
    entorno = dict(os.environ, PYTHONIOENCODING='utf-8')
    entorno.pop('DATAOPS_KEY', None)
    if clave is not None:
        entorno['DATAOPS_KEY'] = clave
    return subprocess.run(
        [sys.executable, 'comprobar_1a.py', '--base', str(base)],
        cwd=RAIZ_REPOSITORIO, env=entorno, capture_output=True,
        text=True, encoding='utf-8', timeout=60)


class PruebaComprobador1A:
    """Comprueba la salida exacta de comprobar_1a.py sobre un entorno temporal."""

    def prueba_imprime_las_cuatro_lineas(self, entorno):
        """Con la clave correcta imprime las cuatro líneas en orden."""
        resultado = ejecutar_comprobador(entorno.base, entorno.clave)
        assert resultado.returncode == 0, resultado.stderr
        assert resultado.stdout.splitlines() == SALIDA_ESPERADA

    def prueba_crea_la_copia_y_conserva_el_original(self, entorno):
        """Crea la copia alterada sin tocar el original ni la referencia."""
        original = entorno.entrada.read_bytes()
        referencia = entorno.referencia.read_bytes()
        ejecutar_comprobador(entorno.base, entorno.clave)
        copia = entorno.entrada.with_name('pedidos_prueba_parte1.csv')
        assert copia.read_bytes() == original.replace(
            b'1850.00', b'1851.00', 1)
        assert entorno.entrada.read_bytes() == original
        assert entorno.referencia.read_bytes() == referencia

    def prueba_sin_clave_pide_revisar(self, entorno):
        """Sin DATAOPS_KEY termina con código 1 y el mensaje REVISAR."""
        resultado = ejecutar_comprobador(entorno.base, None)
        assert resultado.returncode == 1
        assert 'REVISAR: Falta DATAOPS_KEY en el entorno' in resultado.stderr

    def prueba_original_alterado_pide_revisar(self, entorno):
        """Si el original no coincide, se detiene sin recalcular la referencia."""
        referencia = entorno.referencia.read_bytes()
        entorno.entrada.write_bytes(entorno.entrada.read_bytes() + b'\n')
        resultado = ejecutar_comprobador(entorno.base, entorno.clave)
        assert resultado.returncode == 1
        assert 'Original coincide con referencia: False' in resultado.stdout
        assert 'REVISAR: Revisar el original' in resultado.stderr
        assert entorno.referencia.read_bytes() == referencia
