"""Pruebas de la preparación del entorno."""
import csv
import hashlib

import pytest
from cryptography.fernet import Fernet

import preparar
from preparar import PreparadorEntorno


class PruebaPreparadorEntorno:
    """Comprueba que el entorno se crea completo y nunca se reemplaza."""

    def prueba_crea_los_tres_archivos(self, tmp_path, capsys):
        """Crea entrada, referencia y clave y avisa sin mostrarlas."""
        preparador = PreparadorEntorno(tmp_path)
        preparador.preparar()
        salida = capsys.readouterr().out
        assert salida == 'Dataset, referencia y clave creados sin mostrarlos\n'
        assert preparador.entrada == tmp_path / 'datos' / 'pedidos.csv'
        assert preparador.referencia == tmp_path / 'referencia.sha256'
        assert preparador.clave == tmp_path / '.secrets' / 'fernet.key'
        for ruta in (preparador.entrada, preparador.referencia,
                     preparador.clave):
            assert ruta.is_file()
        clave = preparador.clave.read_bytes()
        assert clave not in salida.encode('ascii')
        Fernet(clave)

    def prueba_no_reemplaza_si_existe(self, tmp_path, capsys):
        """Una segunda preparación falla y deja los archivos intactos."""
        preparador = PreparadorEntorno(tmp_path)
        preparador.preparar()
        antes = {r: r.read_bytes() for r in (
            preparador.entrada, preparador.referencia, preparador.clave)}
        with pytest.raises(FileExistsError,
                           match='^Entorno existente; revisar antes de recrear$'):
            PreparadorEntorno(tmp_path).preparar()
        assert {r: r.read_bytes() for r in antes} == antes

    def prueba_no_reemplaza_si_solo_existe_la_clave(self, tmp_path):
        """Basta con que exista uno de los tres archivos para detenerse."""
        preparador = PreparadorEntorno(tmp_path)
        preparador.secretos.mkdir(parents=True)
        preparador.clave.write_bytes(b'existente')
        with pytest.raises(FileExistsError):
            preparador.preparar()
        assert not preparador.entrada.exists()
        assert preparador.clave.read_bytes() == b'existente'

    def prueba_csv_con_doce_filas_y_contrato(self, entorno):
        """El CSV tiene el contrato de columnas y 12 pedidos ficticios."""
        with entorno.entrada.open(encoding='utf-8', newline='') as f:
            lector = csv.DictReader(f)
            filas = list(lector)
        assert lector.fieldnames == preparar.CAMPOS
        assert len(filas) == len(preparar.PEDIDOS) == 12
        assert filas[0] == {
            'pedido_id': 'PED-1001',
            'cliente_id': 'CLI-001',
            'nombre_cliente': 'Cliente Prueba 001',
            'correo': 'cliente001@example.com',
            'ciudad': 'Villahermosa',
            'importe': '1850.00',
            'estado': 'Confirmado',
        }
        assert filas[-1]['pedido_id'] == 'PED-1012'

    def prueba_referencia_igual_a_la_huella_del_csv(self, entorno):
        """La referencia es el SHA-256 del CSV recién creado."""
        esperado = hashlib.sha256(entorno.entrada.read_bytes()).hexdigest()
        assert entorno.referencia.read_text(encoding='ascii') == esperado
