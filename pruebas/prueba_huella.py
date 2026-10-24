"""Pruebas de la huella SHA-256 (TODO 1)."""
import hashlib

import lab1
from lab1 import CalculadoraHuella


class PruebaCalculadoraHuella:
    """Comprueba que la huella identifica exactamente los bytes del archivo."""

    def prueba_coincide_con_hashlib_directo(self, entorno):
        """La huella es la misma que da hashlib sobre los bytes completos."""
        esperado = hashlib.sha256(entorno.entrada.read_bytes()).hexdigest()
        assert CalculadoraHuella().calcular(entorno.entrada) == esperado
        assert lab1.calcular_hash(entorno.entrada) == esperado

    def prueba_devuelve_hexadecimal_de_64(self, entorno):
        """La huella es texto hexadecimal de 64 caracteres."""
        huella = lab1.calcular_hash(str(entorno.entrada))
        assert len(huella) == 64
        assert set(huella) <= set('0123456789abcdef')

    def prueba_mismo_archivo_misma_huella(self, entorno):
        """Calcular dos veces sobre el mismo archivo da la misma huella."""
        calculadora = CalculadoraHuella()
        assert (calculadora.calcular(entorno.entrada)
                == calculadora.calcular(entorno.entrada))

    def prueba_un_byte_alterado_cambia_la_huella(self, entorno, tmp_path):
        """Cambiar un solo byte produce una huella distinta."""
        contenido = bytearray(entorno.entrada.read_bytes())
        contenido[-2] ^= 0x01
        copia = tmp_path / 'alterada.csv'
        copia.write_bytes(bytes(contenido))
        assert lab1.calcular_hash(copia) != lab1.calcular_hash(entorno.entrada)

    def prueba_archivo_grande_por_bloques(self, tmp_path):
        """Un archivo mayor que varios bloques da la huella correcta."""
        datos = bytes(range(256)) * 1000 + b'fin'
        assert len(datos) > 3 * CalculadoraHuella.TAMANO_BLOQUE
        ruta = tmp_path / 'grande.bin'
        ruta.write_bytes(datos)
        assert (CalculadoraHuella().calcular(ruta)
                == hashlib.sha256(datos).hexdigest())

    def prueba_coincide_con_la_referencia(self, entorno):
        """La huella del original preparado coincide con la referencia."""
        referencia = entorno.referencia.read_text(encoding='ascii').strip()
        assert lab1.calcular_hash(entorno.entrada) == referencia
