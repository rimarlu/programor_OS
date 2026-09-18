from odoo_api import OdooAPI

odoo = OdooAPI()
ordenes = odoo.operaciones_modelo(1)

for orden in ordenes:
    print(orden)