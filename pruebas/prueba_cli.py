"""Pruebas de la línea de comandos y del TODO 2 pendiente."""
import json
import os
import subprocess
import sys

import pytest

import lab1
from lab1 import ControlAcceso, PipelineNova
from pruebas.conftest import RAIZ_REPOSITORIO


def ejecutar_cli(entorno, *argumentos):
    """Ejecuta lab1.py con la clave del entorno y rutas en tmp_path."""
    variables = dict(os.environ, PYTHONIOENCODING='utf-8',
                     DATAOPS_KEY=entorno.clave)
    return subprocess.run(
        [sys.executable, 'lab1.py', *argumentos,
         '--entrada', str(entorno.entrada),
         '--referencia', str(entorno.referencia)],
        cwd=RAIZ_REPOSITORIO, env=variables, capture_output=True,
        text=True, encoding='utf-8', timeout=60)


class PruebaInterfazLinea:
    """Comprueba los códigos de salida y mensajes de la CLI en 1A."""

    def prueba_inspeccionar_muestra_el_primer_pedido(self, entorno):
        """inspeccionar funciona y muestra el primer pedido ficticio."""
        resultado = ejecutar_cli(entorno, 'inspeccionar')
        assert resultado.returncode == 0, resultado.stderr
        primero = json.loads(resultado.stdout)
        assert primero['pedido_id'] == 'PED-1001'
        assert primero['correo'] == 'cliente001@example.com'

    @pytest.mark.parametrize('accion', ['ejecutar', 'resumen', 'recuperar'])
    def prueba_acciones_pendientes(self, entorno, accion):
        """ejecutar, resumen y recuperar terminan con código 2 y PENDIENTE."""
        destino = entorno.base / 'salidas' / f'cli_{accion}'
        resultado = ejecutar_cli(entorno, accion, '--rol', 'operador',
                                 '--destino', str(destino))
        assert resultado.returncode == 2
        assert resultado.stderr.strip() == 'PENDIENTE: TODO 2: autorizar'
        assert not destino.exists()

    def prueba_ejecutar_no_crea_el_destino(self, entorno):
        """Un ejecutar pendiente no crea el destino ni su carpeta padre."""
        destino = entorno.base / 'salidas' / 'lab1'
        resultado = ejecutar_cli(entorno, 'ejecutar', '--destino', str(destino))
        assert resultado.returncode == 2
        assert 'PENDIENTE: TODO 2: autorizar' in resultado.stderr
        assert not (entorno.base / 'salidas').exists()

    def prueba_inspeccionar_entrada_invalida_bloquea(self, entorno):
        """Una entrada que incumple el contrato termina con código 1."""
        entorno.entrada.write_text('a,b\r\n1,2\r\n', encoding='utf-8')
        resultado = ejecutar_cli(entorno, 'inspeccionar')
        assert resultado.returncode == 1
        assert resultado.stderr.strip() == (
            'BLOQUEADO: Columnas distintas del contrato')


class PruebaControlAccesoPendiente:
    """Comprueba que el TODO 2 sigue pendiente, como pide lab1.md en 1A."""

    def prueba_permisos_conservan_el_contrato(self):
        """PERMISOS conserva la matriz original del laboratorio."""
        assert lab1.PERMISOS == {
            'operador': {'ejecutar', 'recuperar'},
            'analista': {'resumen'},
            'auditor': {'evidencias'},
        }
        assert ControlAcceso().permisos is lab1.PERMISOS

    def prueba_autorizar_pendiente(self):
        """autorizar lanza NotImplementedError con el texto del TODO 2."""
        with pytest.raises(NotImplementedError, match='^TODO 2: autorizar$'):
            lab1.autorizar('operador', 'ejecutar')
        with pytest.raises(NotImplementedError):
            ControlAcceso().autorizar('auditor', 'evidencias')

    def prueba_pipeline_se_detiene_antes_de_crear_destino(self, entorno):
        """El pipeline consulta el permiso primero y no crea el destino."""
        destino = entorno.base / 'salidas' / 'pipeline'
        with pytest.raises(NotImplementedError):
            PipelineNova().ejecutar('operador', entorno.entrada,
                                    entorno.referencia, destino)
        assert not destino.exists()
