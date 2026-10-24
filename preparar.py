"""Preparación del entorno del Laboratorio 1 de Comercial Nova.

Genera una sola vez el dataset ficticio datos/pedidos.csv, la huella de
referencia referencia.sha256 y la clave local .secrets/fernet.key, sin
mostrarlos. Si alguno de los tres ya existe, no reemplaza nada.

Uso:
    python preparar.py
"""
import csv
import hashlib
from pathlib import Path

from cryptography.fernet import Fernet

BASE = Path(__file__).resolve().parent
CAMPOS = [
    'pedido_id', 'cliente_id', 'nombre_cliente',
    'correo', 'ciudad', 'importe', 'estado',
]
# Todos los clientes y pedidos son ficticios.
# Número de cliente, ciudad, importe y estado por pedido.
PEDIDOS = [
    (1, 'Villahermosa', '1850.00', 'Confirmado'),
    (2, 'Merida', '950.50', 'Confirmado'),
    (3, 'Puebla', '1200.00', 'Cancelado'),
    (1, 'Villahermosa', '650.00', 'Confirmado'),
    (4, 'Merida', '1499.50', 'Confirmado'),
    (5, 'Puebla', '2100.00', 'Confirmado'),
    (6, 'Villahermosa', '800.00', 'Cancelado'),
    (7, 'Puebla', '400.00', 'Confirmado'),
    (8, 'Merida', '300.00', 'Confirmado'),
    (9, 'Villahermosa', '1750.00', 'Confirmado'),
    (10, 'Puebla', '550.00', 'Cancelado'),
    (11, 'Merida', '1250.00', 'Confirmado'),
]


class PreparadorEntorno:
    """Crea el dataset, la referencia y la clave de una práctica.

    Reproduce exactamente el preparar.py del material: mismas 12 filas, mismo
    orden de columnas y misma negativa a reemplazar un entorno existente.
    """

    def __init__(self, base: Path):
        """Define las rutas del entorno a partir de una carpeta base.

        Argumentos:
            base: carpeta raíz donde se crean datos/, .secrets/ y la
                referencia.
        """
        self.base = Path(base)
        self.datos = self.base / 'datos'
        self.secretos = self.base / '.secrets'
        self.entrada = self.datos / 'pedidos.csv'
        self.referencia = self.base / 'referencia.sha256'
        self.clave = self.secretos / 'fernet.key'

    def preparar(self):
        """Genera el entorno completo sin mostrar datos ni clave.

        Lanza:
            FileExistsError: si ya existe la entrada, la referencia o la
                clave; en ese caso no se modifica nada.
        """
        self.datos.mkdir(exist_ok=True)
        self.secretos.mkdir(exist_ok=True)
        # No reemplazar datos, clave o referencia en una repetición.
        if any(p.exists() for p in (self.entrada, self.referencia, self.clave)):
            raise FileExistsError('Entorno existente; revisar antes de recrear')
        self._escribir_dataset()
        # Alta de referencia sobre datos conocidos del instructor.
        self.referencia.write_text(
            hashlib.sha256(self.entrada.read_bytes()).hexdigest(),
            encoding='ascii')
        self._generar_clave()
        print('Dataset, referencia y clave creados sin mostrarlos')

    def _escribir_dataset(self):
        with self.entrada.open('w', encoding='utf-8', newline='') as f:
            escritor = csv.DictWriter(f, fieldnames=CAMPOS)
            escritor.writeheader()
            for n, (cliente, ciudad, importe, estado) in enumerate(
                    PEDIDOS, start=1001):
                escritor.writerow({
                    'pedido_id': f'PED-{n}',
                    'cliente_id': f'CLI-{cliente:03d}',
                    'nombre_cliente': f'Cliente Prueba {cliente:03d}',
                    'correo': f'cliente{cliente:03d}@example.com',
                    'ciudad': ciudad,
                    'importe': importe,
                    'estado': estado,
                })

    def _generar_clave(self):
        with self.clave.open('xb') as f:
            f.write(Fernet.generate_key())
        try:
            self.clave.chmod(0o600)
        except OSError:
            pass  # En Windows se requiere gestionar ACL aparte.


def main():
    """Prepara el entorno en la carpeta del propio script."""
    PreparadorEntorno(BASE).preparar()


if __name__ == '__main__':
    main()
