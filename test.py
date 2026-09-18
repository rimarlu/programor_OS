from odoo_api import OdooAPI

odoo = OdooAPI()
ordenes = odoo.leer_ordenes(999)

for orden in ordenes:
    print(orden)