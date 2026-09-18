from odoo_api import OdooAPI

odoo = OdooAPI()
ordenes = odoo.leer_ordenes(1)

for orden in ordenes:
    print(orden)