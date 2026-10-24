"""Pruebas del contrato de datos de los pedidos."""
import pytest

import lab1
from lab1 import CAMPOS, ValidadorPedidos

ENCABEZADO = ','.join(CAMPOS) + '\r\n'
FILA_VALIDA = ('PED-1,CLI-001,Cliente Prueba 001,cliente001@example.com,'
               'Merida,10.00,Confirmado\r\n')


class PruebaValidadorPedidos:
    """Comprueba cada regla del contrato con su mensaje exacto."""

    def prueba_doce_filas_validas(self, entorno):
        """El dataset preparado tiene 12 filas que cumplen el contrato."""
        filas = ValidadorPedidos().leer(entorno.entrada)
        assert len(filas) == 12
        assert list(filas[0]) == CAMPOS
        assert filas[0]['pedido_id'] == 'PED-1001'
        assert len(lab1.leer_pedidos(entorno.entrada)) == 12

    def prueba_columnas_distintas(self, escribir_csv_prueba):
        """Un orden de columnas distinto se rechaza."""
        campos = CAMPOS[::-1]
        ruta = escribir_csv_prueba('columnas.csv', ','.join(campos) + '\r\n')
        with pytest.raises(ValueError, match='^Columnas distintas del contrato$'):
            ValidadorPedidos().leer(ruta)

    def prueba_dataset_vacio(self, escribir_csv_prueba):
        """Un CSV con solo encabezado se rechaza."""
        ruta = escribir_csv_prueba('vacio.csv', ENCABEZADO)
        with pytest.raises(ValueError, match='^Dataset vacio$'):
            ValidadorPedidos().leer(ruta)

    def prueba_identificadores_duplicados(self, escribir_csv_prueba):
        """Dos filas con el mismo pedido_id se rechazan."""
        ruta = escribir_csv_prueba('duplicados.csv',
                                   ENCABEZADO + FILA_VALIDA * 2)
        with pytest.raises(ValueError, match='^Identificadores duplicados$'):
            ValidadorPedidos().leer(ruta)

    @pytest.mark.parametrize('importe', ['-1.00', 'NaN', 'Infinity', 'abc'])
    def prueba_importe_invalido(self, escribir_csv_prueba, importe):
        """Importes negativos, no finitos o no numéricos se rechazan."""
        fila = FILA_VALIDA.replace('10.00', importe)
        ruta = escribir_csv_prueba('importe.csv', ENCABEZADO + fila)
        with pytest.raises(ValueError, match='^Importe invalido$'):
            ValidadorPedidos().leer(ruta)

    def prueba_estado_invalido(self, escribir_csv_prueba):
        """Un estado fuera de Confirmado y Cancelado se rechaza."""
        fila = FILA_VALIDA.replace('Confirmado', 'Pendiente')
        ruta = escribir_csv_prueba('estado.csv', ENCABEZADO + fila)
        with pytest.raises(ValueError, match='^Estado invalido$'):
            ValidadorPedidos().leer(ruta)
