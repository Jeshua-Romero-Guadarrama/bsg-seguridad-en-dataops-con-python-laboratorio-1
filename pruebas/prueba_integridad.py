"""Pruebas de la verificación de integridad frente a la referencia."""
import pytest

import lab1
from lab1 import VerificadorIntegridad


class PruebaVerificadorIntegridad:
    """Comprueba que solo el original conocido supera la verificación."""

    def prueba_original_coincide(self, entorno):
        """El original devuelve su huella, igual a la referencia."""
        huella = VerificadorIntegridad().verificar(
            entorno.entrada, entorno.referencia)
        assert huella == entorno.referencia.read_text(encoding='ascii').strip()
        assert lab1.verificar_integridad(
            entorno.entrada, entorno.referencia) == huella

    def prueba_copia_alterada_bloquea(self, entorno):
        """Cambiar 1850.00 por 1851.00 hace fallar la verificación."""
        contenido = entorno.entrada.read_bytes()
        alterado = contenido.replace(b'1850.00', b'1851.00', 1)
        assert alterado != contenido
        copia = entorno.entrada.with_name('pedidos_prueba_parte1.csv')
        copia.write_bytes(alterado)
        with pytest.raises(ValueError) as error:
            VerificadorIntegridad().verificar(copia, entorno.referencia)
        assert str(error.value) == 'Integridad de entrada no valida'

    def prueba_no_modifica_la_referencia(self, entorno):
        """Un fallo de integridad no recalcula ni toca la referencia."""
        antes = entorno.referencia.read_bytes()
        copia = entorno.entrada.with_name('otra.csv')
        copia.write_bytes(entorno.entrada.read_bytes() + b'\n')
        with pytest.raises(ValueError):
            lab1.verificar_integridad(copia, entorno.referencia)
        assert entorno.referencia.read_bytes() == antes

    def prueba_referencia_ausente(self, entorno, tmp_path):
        """Sin archivo de referencia se lanza OSError."""
        with pytest.raises(OSError):
            VerificadorIntegridad().verificar(
                entorno.entrada, tmp_path / 'no_existe.sha256')
