import requests
import json

from config import (
    ODOO_URL,
    ODOO_DATABASE,
    ODOO_API_KEY,
    validar_configuracion_odoo,
)


class OdooAPI:
    def __init__(self):
        validar_configuracion_odoo()

        self.base_url = f"{ODOO_URL}/json/2"
        self.headers = {
            "Authorization": f"bearer {ODOO_API_KEY}",
            "X-Odoo-Database": ODOO_DATABASE,
            "Content-Type": "application/json",
            "User-Agent": "Programador-OS/1.0",
        }


    def ejecutar(self, modelo, metodo, **parametros):
        url = f"{self.base_url}/{modelo}/{metodo}"

        print("URL:", url)
        print("PARAMETROS:", parametros)

        respuesta = requests.post(
            url,
            headers=self.headers,
            json=parametros,
            timeout=30,
        )

        print("STATUS:", respuesta.status_code)

        respuesta.raise_for_status()
        datos = respuesta.json()

        # Imprimir JSON ordenado
        print("RESPUESTA:")
        print(json.dumps(datos, indent=4, ensure_ascii=False))

        return datos

    def leer_ordenes(self, limite=99999999999):
        return self.ejecutar(
            "sale.order.line",
            "search_read",
            domain=[("name", "not ilike", "KIT"),("id_state" , "not ilike", "closed")],
            fields=[
                "id",               
                "order_id",          # Trae [id_orden, "SO001"]
                "order_partner_id",  # Cliente asociado
                "name",              # Descripción del producto / línea
                "product_uom_qty",   # Cantidad
                "price_subtotal",    # Subtotal
                "id_state",   
                "date_order",
                "commitment_date",       # Estado de la línea (nuevo campo)
                
            ],
            limit=limite,
            order="commitment_date asc",
        )
    

    def operaciones_modelo(self, limite =999):
        return self.ejecutar(
            "mrp.routing.workcenter",
            "search_read",
            domain=[],
            fields=[
                "name",           
                "bom_id",              # operacion
                "workcenter_id",       # workcenter
                "time_mode",        # time mode
                "time_cycle",       # time cycle   
                "quality_point_count",       # quality check
                
                
            ],
            limit=limite,
            order="workcenter_id asc",
        ) 