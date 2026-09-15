import sqlite3
from pathlib import Path
from datetime import datetime


# ==========================================================
# BASE DE DATOS
# ==========================================================

RUTA_BASE_DATOS = Path("programador.db")


# ==========================================================
# CONEXIÓN
# ==========================================================

def obtener_conexion():

    conexion = sqlite3.connect(
        RUTA_BASE_DATOS
    )

    conexion.row_factory = sqlite3.Row

    return conexion


# ==========================================================
# INICIALIZAR BASE DE DATOS
# ==========================================================

def inicializar_base_datos():

    conexion = obtener_conexion()

    cursor = conexion.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS importacion_odoo (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            cliente TEXT,

            referencia_pedido TEXT,

            id_odoo TEXT UNIQUE,

            descripcion TEXT,

            cantidad REAL,

            fecha_orden TEXT,

            fecha_entrega_produccion TEXT,

            subtotal REAL,

            estado_id TEXT,

            fecha_importacion TEXT
        )
    """)

    conexion.commit()
    conexion.close()


# ==========================================================
# GUARDAR REGISTRO
# ==========================================================

def guardar_importacion_odoo(registro):

    conexion = obtener_conexion()

    cursor = conexion.cursor()

    cursor.execute("""
        INSERT INTO importacion_odoo (
            cliente,
            referencia_pedido,
            id_odoo,
            descripcion,
            cantidad,
            fecha_orden,
            fecha_entrega_produccion,
            subtotal,
            estado_id,
            fecha_importacion
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)

        ON CONFLICT(id_odoo)
        DO UPDATE SET

            cliente = excluded.cliente,
            referencia_pedido = excluded.referencia_pedido,
            descripcion = excluded.descripcion,
            cantidad = excluded.cantidad,
            fecha_orden = excluded.fecha_orden,
            fecha_entrega_produccion =
                excluded.fecha_entrega_produccion,
            subtotal = excluded.subtotal,
            estado_id = excluded.estado_id,
            fecha_importacion = excluded.fecha_importacion
    """, (

        registro.get("Cliente"),

        registro.get("Referencia del pedido"),

        registro.get("ID"),

        registro.get("Descripción"),

        registro.get("Cantidad"),

        registro.get("Fecha Orden"),

        registro.get("Fecha Entrega Producción"),

        registro.get("Subtotal"),

        registro.get("Estado ID"),

        datetime.now().isoformat(
            timespec="seconds"
        )
    ))

    conexion.commit()
    conexion.close()


# ==========================================================
# GUARDAR MUCHOS REGISTROS
# ==========================================================

def guardar_importaciones_odoo(registros):

    conexion = obtener_conexion()

    cursor = conexion.cursor()

    fecha_importacion = datetime.now().isoformat(
        timespec="seconds"
    )

    for registro in registros:

        cursor.execute("""
            INSERT INTO importacion_odoo (
                cliente,
                referencia_pedido,
                id_odoo,
                descripcion,
                cantidad,
                fecha_orden,
                fecha_entrega_produccion,
                subtotal,
                estado_id,
                fecha_importacion
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)

            ON CONFLICT(id_odoo)
            DO UPDATE SET

                cliente = excluded.cliente,
                referencia_pedido = excluded.referencia_pedido,
                descripcion = excluded.descripcion,
                cantidad = excluded.cantidad,
                fecha_orden = excluded.fecha_orden,
                fecha_entrega_produccion =
                    excluded.fecha_entrega_produccion,
                subtotal = excluded.subtotal,
                estado_id = excluded.estado_id,
                fecha_importacion = excluded.fecha_importacion
        """, (

            registro.get("Cliente"),

            registro.get("Referencia del pedido"),

            registro.get("ID"),

            registro.get("Descripción"),

            registro.get("Cantidad"),

            registro.get("Fecha Orden"),

            registro.get("Fecha Entrega Producción"),

            registro.get("Subtotal"),

            registro.get("Estado ID"),

            fecha_importacion
        ))

    conexion.commit()
    conexion.close()


# ==========================================================
# LEER IMPORTACIONES
# ==========================================================

def obtener_importaciones_odoo():

    conexion = obtener_conexion()

    cursor = conexion.cursor()

    cursor.execute("""
        SELECT
            cliente,
            referencia_pedido,
            id_odoo,
            descripcion,
            cantidad,
            fecha_orden,
            fecha_entrega_produccion,
            subtotal,
            estado_id,
            fecha_importacion

        FROM importacion_odoo

        ORDER BY id DESC
    """)

    registros = cursor.fetchall()

    conexion.close()

    return registros