"""Pruebas de cifrado y recuperación con Fernet (TODO 3 y TODO 4)."""
import pytest
from cryptography.fernet import Fernet, InvalidToken

import lab1
from lab1 import CifradorCampos


class PruebaCifradorCampos:
    """Comprueba que el cifrado protege el valor y permite recuperarlo."""

    def prueba_ida_y_vuelta(self, entorno):
        """Descifrar el token devuelve exactamente el correo original."""
        correo = 'cliente001@example.com'
        token = lab1.cifrar(correo, entorno.fernet)
        assert lab1.descifrar(token, entorno.fernet) == correo

    def prueba_token_ascii_distinto_del_original(self, entorno):
        """El token es texto ASCII y no contiene el valor legible."""
        correo = 'cliente001@example.com'
        token = lab1.cifrar(correo, entorno.fernet)
        assert isinstance(token, str)
        assert token.isascii()
        assert token != correo
        assert correo not in token

    def prueba_token_alterado_lanza_invalid_token(self, entorno):
        """Un token modificado se rechaza en lugar de devolver basura."""
        cifrador = CifradorCampos(entorno.fernet)
        token = cifrador.cifrar('Cliente Prueba 001')
        posicion = len(token) // 2
        sustituto = 'A' if token[posicion] != 'A' else 'B'
        alterado = token[:posicion] + sustituto + token[posicion + 1:]
        with pytest.raises(InvalidToken):
            cifrador.descifrar(alterado)

    def prueba_otra_clave_no_recupera(self, entorno):
        """Una clave distinta no recupera tokens cifrados con la original."""
        token = lab1.cifrar('cliente001@example.com', entorno.fernet)
        with pytest.raises(InvalidToken):
            lab1.descifrar(token, Fernet(Fernet.generate_key()))

    def prueba_dos_cifrados_producen_tokens_distintos(self, entorno):
        """Cifrar dos veces el mismo valor da tokens distintos."""
        cifrador = CifradorCampos(entorno.fernet)
        primero = cifrador.cifrar('cliente001@example.com')
        segundo = cifrador.cifrar('cliente001@example.com')
        assert primero != segundo
        assert cifrador.descifrar(primero) == cifrador.descifrar(segundo)

    def prueba_texto_con_acentos_y_enie(self, entorno):
        """Los textos con acentos y ñ se recuperan sin pérdida."""
        valor = 'Señora Úrsula Peña, Mérida'
        cifrador = CifradorCampos(entorno.fernet)
        assert cifrador.descifrar(cifrador.cifrar(valor)) == valor


class PruebaCifradorDesdeEntorno:
    """Comprueba la carga de la clave desde DATAOPS_KEY."""

    def prueba_carga_la_clave_del_entorno(self, entorno):
        """Con la variable presente, el cifrador recupera lo que cifra."""
        cifrador = CifradorCampos.desde_entorno()
        assert cifrador.descifrar(cifrador.cifrar('dato')) == 'dato'
        fernet = lab1.cargar_cifrador()
        assert lab1.descifrar(lab1.cifrar('dato', fernet), fernet) == 'dato'

    def prueba_falta_la_variable(self, monkeypatch):
        """Sin DATAOPS_KEY se lanza ValueError con el mensaje exacto."""
        monkeypatch.delenv('DATAOPS_KEY', raising=False)
        with pytest.raises(ValueError) as error:
            CifradorCampos.desde_entorno()
        assert str(error.value) == 'Falta DATAOPS_KEY en el entorno'
        with pytest.raises(ValueError, match='Falta DATAOPS_KEY en el entorno'):
            lab1.cargar_cifrador()

    def prueba_variable_vacia(self, monkeypatch):
        """Una variable vacía se trata igual que una ausente."""
        monkeypatch.setenv('DATAOPS_KEY', '')
        with pytest.raises(ValueError, match='Falta DATAOPS_KEY en el entorno'):
            CifradorCampos.desde_entorno()
