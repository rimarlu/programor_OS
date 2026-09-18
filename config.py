import os
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

ODOO_URL = os.getenv("ODOO_URL", "").rstrip("/")
ODOO_DATABASE = os.getenv("ODOO_DATABASE", "")
ODOO_API_KEY = os.getenv("ODOO_API_KEY", "")



def validar_configuracion_odoo():
    requeridas = {
        "ODOO_URL": ODOO_URL,
        "ODOO_DATABASE": ODOO_DATABASE,
        "ODOO_API_KEY": ODOO_API_KEY,
    }

    faltantes = [nombre for nombre, valor in requeridas.items() if not valor]

    if faltantes:
        raise RuntimeError(
            "Faltan variables de Odoo: " + ", ".join(faltantes)
        )