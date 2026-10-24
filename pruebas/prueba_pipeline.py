"""Pruebas del pipeline con un control de acceso simulado.

En 1A el TODO 2 sigue pendiente, así que estas pruebas inyectan un control
que permite todo solo para comprobar que el resto del pipeline (integridad,
validación, cifrado y escritura) ya funciona. La autorización real se
implementa y prueba en el Laboratorio 2.
"""
import csv

import pytest

from lab1 import CAMPOS, CifradorCampos, ControlAcceso, PipelineNova


class ControlPermisivoDePrueba(ControlAcceso):
    """Control de acceso que permite todo; solo para pruebas aisladas."""

    def autorizar(self, rol, operacion):
        """Permite cualquier operación."""
        return True


@pytest.fixture
def pipeline():
    """Pipeline con el control permisivo de prueba."""
    return PipelineNova(control_acceso=ControlPermisivoDePrueba())


class PruebaPipelineNova:
    """Comprueba integridad, validación, cifrado y escritura del pipeline."""

    def prueba_ejecutar_protege_y_totaliza(self, entorno, pipeline):
        """Procesa 12 filas, cifra nombre y correo y totaliza por ciudad."""
        destino = entorno.base / 'salidas' / 'lab1'
        r = pipeline.ejecutar('operador', entorno.entrada,
                              entorno.referencia, destino)
        assert r['filas'] == 12
        assert r['hash_entrada'] == entorno.referencia.read_text().strip()
        with r['detalle'].open(encoding='utf-8', newline='') as f:
            lector = csv.DictReader(f)
            detalle = list(lector)
        assert lector.fieldnames == CAMPOS
        assert len(detalle) == 12
        texto = r['detalle'].read_text(encoding='utf-8')
        assert '@example.com' not in texto
        assert 'Cliente Prueba' not in texto
        assert r['resumen'].read_text(encoding='utf-8').splitlines() == [
            'ciudad,total_ventas',
            'Merida,4000.00',
            'Puebla,2500.00',
            'Villahermosa,4250.00',
        ]

    def prueba_recuperar_muestra(self, entorno, pipeline):
        """La primera muestra se descifra al valor ficticio original."""
        destino = entorno.base / 'salidas' / 'lab1'
        pipeline.ejecutar('operador', entorno.entrada,
                          entorno.referencia, destino)
        assert pipeline.recuperar_muestra('operador', destino) == {
            'nombre_cliente': 'Cliente Prueba 001',
            'correo': 'cliente001@example.com',
        }

    def prueba_entrada_alterada_no_crea_destino(self, entorno, pipeline):
        """La copia alterada se bloquea antes de crear el destino."""
        copia = entorno.entrada.with_name('pedidos_prueba_parte1.csv')
        copia.write_bytes(entorno.entrada.read_bytes().replace(
            b'1850.00', b'1851.00', 1))
        destino = entorno.base / 'salidas' / 'alterada'
        with pytest.raises(ValueError, match='Integridad de entrada no valida'):
            pipeline.ejecutar('operador', copia, entorno.referencia, destino)
        assert not destino.exists()

    def prueba_destino_existente_no_se_sobrescribe(self, entorno, pipeline):
        """Un destino que ya existe se rechaza."""
        destino = entorno.base / 'salidas' / 'lab1'
        destino.mkdir(parents=True)
        with pytest.raises(FileExistsError):
            pipeline.ejecutar('operador', entorno.entrada,
                              entorno.referencia, destino)

    def prueba_cifrador_inyectado(self, entorno):
        """Acepta un cifrador inyectado en lugar de leer el entorno."""
        cifrador = CifradorCampos(entorno.fernet)
        pipeline = PipelineNova(control_acceso=ControlPermisivoDePrueba(),
                                cifrador=cifrador)
        assert pipeline.cifrador is cifrador
