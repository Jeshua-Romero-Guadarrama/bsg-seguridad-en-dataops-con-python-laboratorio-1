"""Fixtures comunes de las pruebas del Laboratorio 1.

Cada prueba trabaja sobre un entorno completo creado en una carpeta
temporal con PreparadorEntorno, de modo que nunca depende de datos/,
.secrets/ ni referencia.sha256 del repositorio. La clave generada se
inyecta en DATAOPS_KEY sin imprimirla.
"""
from dataclasses import dataclass
from pathlib import Path

import pytest
from cryptography.fernet import Fernet

from preparar import PreparadorEntorno

RAIZ_REPOSITORIO = Path(__file__).resolve().parent.parent


@dataclass
class EntornoPrueba:
    """Rutas y clave de un entorno temporal preparado."""

    base: Path
    entrada: Path
    referencia: Path
    clave: str

    @property
    def fernet(self):
        """Fernet construido con la clave del entorno."""
        return Fernet(self.clave.encode('ascii'))


@pytest.fixture
def entorno(tmp_path, monkeypatch, capsys):
    """Prepara un entorno temporal y carga su clave en DATAOPS_KEY.

    Devuelve:
        EntornoPrueba con las rutas de entrada, referencia y la clave.
    """
    preparador = PreparadorEntorno(tmp_path)
    preparador.preparar()
    capsys.readouterr()
    clave = preparador.clave.read_text(encoding='ascii').strip()
    monkeypatch.setenv('DATAOPS_KEY', clave)
    return EntornoPrueba(
        base=tmp_path,
        entrada=preparador.entrada,
        referencia=preparador.referencia,
        clave=clave,
    )


@pytest.fixture
def escribir_csv_prueba(tmp_path):
    """Devuelve una función que escribe un CSV de texto en tmp_path.

    Devuelve:
        Función (nombre, texto) -> Path.
    """
    def _escribir(nombre, texto):
        ruta = tmp_path / nombre
        ruta.write_text(texto, encoding='utf-8', newline='')
        return ruta
    return _escribir
