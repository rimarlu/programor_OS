from pathlib import Path
import re
import unicodedata

import pandas as pd
import streamlit as st
import re

from biblioteca_mrp import buscar_contextos_similares


# ==========================================================
# RUTAS DE DATOS
# ==========================================================

CARPETA_DATOS = Path("datos")

ARCHIVO_ACTIVIDADES = (
    CARPETA_DATOS / "actividades_id.pkl"
)

ARCHIVO_HISTORIAL = (
    CARPETA_DATOS / "historial_actividades.pkl"
)

CARPETA_DATOS.mkdir(
    exist_ok=True
)


# ==========================================================
# ESTRUCTURA DE ACTIVIDADES
# ==========================================================

COLUMNAS_ACTIVIDADES = [
    "ID Odoo",
    "Referencia del pedido",
    "Actividad",
    "Orden Propuesta",
    "Origen",
    "Seleccionada",
    "Fecha Programación",
    "Estado",
    "Observación",
]


# ==========================================================
# ESTRUCTURA DEL HISTORIAL
# ==========================================================

COLUMNAS_HISTORIAL = [
    "ID Odoo",
    "Referencia del pedido",
    "Descripción",
    "Acción",
    "Producto",
    "Actividad",
    "Origen Propuesta",
    "Decisión",
    "Fecha",
]


# ==========================================================
# CARGAR ACTIVIDADES
# ==========================================================

def cargar_actividades():

    if not ARCHIVO_ACTIVIDADES.exists():

        return pd.DataFrame(
            columns=COLUMNAS_ACTIVIDADES
        )

    try:

        df = pd.read_pickle(
            ARCHIVO_ACTIVIDADES
        )

    except Exception as error:

        st.error(
            f"No fue posible cargar actividades: {error}"
        )

        return pd.DataFrame(
            columns=COLUMNAS_ACTIVIDADES
        )

    # ------------------------------------------------------
    # COMPATIBILIDAD
    # ------------------------------------------------------

    if (
        "Orden" in df.columns
        and "Orden Propuesta" not in df.columns
    ):

        df = df.rename(
            columns={
                "Orden": "Orden Propuesta"
            }
        )

    if (
        "Observaciones" in df.columns
        and "Observación" not in df.columns
    ):

        df = df.rename(
            columns={
                "Observaciones": "Observación"
            }
        )

    # ------------------------------------------------------
    # ASEGURAR COLUMNAS
    # ------------------------------------------------------

    for columna in COLUMNAS_ACTIVIDADES:

        if columna not in df.columns:

            if columna == "Seleccionada":

                df[columna] = False

            elif columna == "Estado":

                df[columna] = "Propuesta"

            else:

                df[columna] = None

    return df[
        COLUMNAS_ACTIVIDADES
    ].copy()


# ==========================================================
# GUARDAR ACTIVIDADES
# ==========================================================

def guardar_actividades(
    df
):

    if df is None:

        df = pd.DataFrame(
            columns=COLUMNAS_ACTIVIDADES
        )

    for columna in COLUMNAS_ACTIVIDADES:

        if columna not in df.columns:

            if columna == "Seleccionada":

                df[columna] = False

            elif columna == "Estado":

                df[columna] = "Propuesta"

            else:

                df[columna] = None

    df = df[
        COLUMNAS_ACTIVIDADES
    ].copy()

    df.to_pickle(
        ARCHIVO_ACTIVIDADES
    )


# ==========================================================
# CARGAR HISTORIAL
# ==========================================================

def cargar_historial():

    if not ARCHIVO_HISTORIAL.exists():

        return pd.DataFrame(
            columns=COLUMNAS_HISTORIAL
        )

    try:

        df = pd.read_pickle(
            ARCHIVO_HISTORIAL
        )

    except Exception as error:

        st.error(
            f"No fue posible cargar el historial: {error}"
        )

        return pd.DataFrame(
            columns=COLUMNAS_HISTORIAL
        )

    for columna in COLUMNAS_HISTORIAL:

        if columna not in df.columns:

            df[columna] = None

    return df[
        COLUMNAS_HISTORIAL
    ].copy()


# ==========================================================
# GUARDAR HISTORIAL
# ==========================================================

def guardar_historial(
    df
):

    if df is None:

        df = pd.DataFrame(
            columns=COLUMNAS_HISTORIAL
        )

    for columna in COLUMNAS_HISTORIAL:

        if columna not in df.columns:

            df[columna] = None

    df = df[
        COLUMNAS_HISTORIAL
    ].copy()

    df.to_pickle(
        ARCHIVO_HISTORIAL
    )


# ==========================================================
# OBTENER ACTIVIDADES DE UN ID
# ==========================================================

def obtener_actividades_id(
    id_odoo
):

    df = cargar_actividades()

    if df.empty:

        return pd.DataFrame(
            columns=COLUMNAS_ACTIVIDADES
        )

    id_odoo = str(
        id_odoo
    ).strip()

    ids = (
        df["ID Odoo"]
        .fillna("")
        .astype(str)
        .str.strip()
    )

    return df[
        ids.eq(id_odoo)
    ].copy()


# ==========================================================
# NORMALIZAR TEXTO
# ==========================================================

def normalizar_texto(
    valor
):

    if valor is None:

        return ""

    if pd.isna(valor):

        return ""

    texto = str(
        valor
    ).strip().lower()

    if not texto:

        return ""

    texto = unicodedata.normalize(
        "NFKD",
        texto
    )

    texto = texto.encode(
        "ascii",
        "ignore"
    ).decode(
        "ascii"
    )

    texto = re.sub(
        r"[^a-z0-9]+",
        " ",
        texto
    )

    texto = re.sub(
        r"\s+",
        " ",
        texto
    )

    return texto.strip()


# ==========================================================
# CONVERTIR REGISTRO COMPLETO A TEXTO
# ==========================================================

def _texto(
    registro
):

    partes = []

    if isinstance(
        registro,
        dict
    ):

        for campo, valor in registro.items():

            if pd.isna(valor):

                continue

            texto = str(
                valor
            ).strip()

            if not texto:

                continue

            partes.append(
                f"{campo}: {texto}"
            )

    return "\n".join(
        partes
    )


# ==========================================================
# DETECTAR ACCIONES
# ==========================================================

PALABRAS_ACCION = {

    "Desinstalación": [
        "desinstalacion",
        "desinstalar",
        "desmontaje",
        "desmontar",
        "retiro",
        "retirar",
        "desmonte",
    ],

    "Instalación": [
        "instalacion",
        "instalar",
        "montaje",
        "montar",
    ],

    "Transporte": [
        "transporte",
        "transportar",
        "traslado",
        "trasladar",
    ],

    "Entrega": [
        "entrega",
        "entregar",
        "despacho",
        "despachar",
    ],

    "Fabricación": [
        "fabricacion",
        "fabricar",
        "elaboracion",
        "elaborar",
        "construccion",
        "construir",
    ],

    "Producción": [
        "produccion",
        "producir",
        "produccion de",
    ],

    "Venta": [
        "venta",
        "vender",
        "vendido",
    ],

    "Servicio": [
        "servicio",
        "mantenimiento",
        "reparacion",
        "reparar",
        "adecuacion",
        "ajuste",
        "correctivo",
        "preventivo",
    ],
}


# ============================================================
# PRODUCTOS / ELEMENTOS PRINCIPALES
# ============================================================

PALABRAS_ELEMENTO = {
    "mural": "Mural",
    "murales": "Mural",

    "aviso": "Aviso",
    "avisos": "Aviso",

    "valla": "Valla",
    "vallas": "Valla",

    "bastidor": "Bastidor",
    "bastidores": "Bastidor",

    "fototelon": "Fototelón",
    "fototelón": "Fototelón",
    "fototelones": "Fototelón",

    "lona": "Lona",
    "lonas": "Lona",

    "pendon": "Pendón",
    "pendón": "Pendón",
    "pendones": "Pendón",

    "cartel": "Cartel",
    "carteles": "Cartel",

    "fachada": "Fachada",
    "fachadas": "Fachada",

    "letrero": "Letrero",
    "letreros": "Letrero",
}

# ==========================================================
# FAMILIAS DE COMPONENTES
# ==========================================================

PALABRAS_ESTRUCTURALES = {
    "bastidor": "Bastidor",
    "bastidores": "Bastidor",

    "valla": "Valla",
    "vallas": "Valla",

    "aviso": "Aviso",
    "avisos": "Aviso",

    "señal": "Señal",
    "senal": "Señal",
    "señales": "Señal",
    "senales": "Señal",

    "caja": "Caja",
    "cajas": "Caja",

    "lamina": "Lámina",
    "lámina": "Lámina",
    "laminas": "Lámina",
    "láminas": "Lámina",

    "pendon": "Pendón",
    "pendón": "Pendón",
    "pendones": "Pendón",

    "pasacalle": "Pasacalle",
    "pasacalles": "Pasacalle",

    "bandera": "Bandera",
    "banderas": "Bandera",

    "pasavias": "Pasavías",
    "pasavías": "Pasavías",

    "barrera": "Barrera",
    "barreras": "Barrera",

    "troquel": "Troquel",
    "troqueles": "Troquel",

    "backing": "Backing",

    "publiposte": "Publiposte",
    "publipostes": "Publiposte",
}


PALABRAS_IMPRESION = {
    "fototelon": "Fototelón",
    "fototelón": "Fototelón",
    "fototelones": "Fototelón",

    "lona impresa": "Lona impresa",
    "lonas impresas": "Lona impresa",

    "vinilo impreso": "Vinilo impreso",
    "vinilos impresos": "Vinilo impreso",

    "fotovinilo": "Fotovinilo",
    "fotovinilos": "Fotovinilo",
}


PALABRAS_SOPORTE_EXISTENTE = {
    "muro": "Muro",
    "muros": "Muro",

    "pared": "Pared",
    "paredes": "Pared",

    "puerta": "Puerta",
    "puertas": "Puerta",

    "via": "Vía",
    "vía": "Vía",
    "vias": "Vía",
    "vías": "Vía",

    "vidriera": "Vidriera",
    "vidrieras": "Vidriera",

    "vehiculo": "Vehículo",
    "vehículo": "Vehículo",
    "vehiculos": "Vehículo",
    "vehículos": "Vehículo",

    "ascensor": "Ascensor",
    "ascensores": "Ascensor",

    "torniquete": "Torniquete",
    "torniquetes": "Torniquete",

    "mural": "Mural",
    "murales": "Mural",
}

def detectar_componentes(descripcion):
    texto = normalizar_texto(descripcion)

    estructurales = []
    estructurales_existentes = []
    impresion = []
    soportes = []

    # -----------------------------------------
    # COMPONENTES ESTRUCTURALES
    # -----------------------------------------

    for palabra, componente in PALABRAS_ESTRUCTURALES.items():

        palabra_normalizada = normalizar_texto(palabra)

        patron = (
            r"(?<!\w)"
            + re.escape(palabra_normalizada)
            + r"(?!\w)"
        )

        coincidencia = re.search(patron, texto)

        if coincidencia:

            if componente not in estructurales:
                estructurales.append(componente)

            # -----------------------------------------
            # DETERMINAR SI EL COMPONENTE ES EXISTENTE
            # -----------------------------------------

            inicio = max(0, coincidencia.start() - 40)
            fin = min(len(texto), coincidencia.end() + 40)

            contexto = texto[inicio:fin]

            palabras_existente = [
                "existente",
                "existentes",
                "ya existe",
                "ya existen",
                "existia",
                "existía",
                "actual",
                "actualmente",
            ]

            es_existente = any(
                palabra_existente in contexto
                for palabra_existente in palabras_existente
            )

            if es_existente:
                if componente not in estructurales_existentes:
                    estructurales_existentes.append(componente)

    # -----------------------------------------
    # COMPONENTES DE IMPRESIÓN
    # -----------------------------------------

    for palabra, componente in PALABRAS_IMPRESION.items():

        palabra_normalizada = normalizar_texto(palabra)

        patron = (
            r"(?<!\w)"
            + re.escape(palabra_normalizada)
            + r"(?!\w)"
        )

        if re.search(patron, texto):

            if componente not in impresion:
                impresion.append(componente)

    # -----------------------------------------
    # SOPORTES / ELEMENTOS EXISTENTES
    # -----------------------------------------

    for palabra, soporte in PALABRAS_SOPORTE_EXISTENTE.items():

        palabra_normalizada = normalizar_texto(palabra)

        patron = (
            r"(?<!\w)"
            + re.escape(palabra_normalizada)
            + r"(?!\w)"
        )

        if re.search(patron, texto):

            if soporte not in soportes:
                soportes.append(soporte)

    return {
        "estructurales": estructurales,
        "estructurales_existentes": estructurales_existentes,
        "impresion": impresion,
        "soportes": soportes,
    }

    # ------------------------------------------------------
    # COMPONENTES DE IMPRESIÓN
    # ------------------------------------------------------

    for palabra, componente in PALABRAS_IMPRESION.items():

        palabra_normalizada = normalizar_texto(palabra)

        patron = (
            r"(?<!\w)"
            + re.escape(palabra_normalizada)
            + r"(?!\w)"
        )

        if re.search(patron, texto):

            if componente not in impresion:
                impresion.append(componente)

    # ------------------------------------------------------
    # SOPORTES EXISTENTES
    # ------------------------------------------------------

    for palabra, soporte in PALABRAS_SOPORTE_EXISTENTE.items():

        palabra_normalizada = normalizar_texto(palabra)

        patron = (
            r"(?<!\w)"
            + re.escape(palabra_normalizada)
            + r"(?!\w)"
        )

        if re.search(patron, texto):

            if soporte not in soportes:
                soportes.append(soporte)

    return {
        "estructurales": estructurales,
        "impresion": impresion,
        "soportes": soportes,
    }


# ============================================================
# MATERIALES / CARACTERÍSTICAS
# ============================================================

PALABRAS_MATERIAL = {
    "vinilo": "Vinilo",
    "vinilo adhesivo": "Vinilo adhesivo",

    
    "aluminio": "Aluminio",
    "acero": "Acero",
    "mdf": "MDF",
    "acrilico": "Acrílico",
    "acrílico": "Acrílico",

    "laminado": "Laminado",
    "laminado mate": "Laminado mate",
    "laminado brillante": "Laminado brillante",
}


# ============================================================
# CARACTERÍSTICAS TÉCNICAS
# ============================================================

PALABRAS_CARACTERISTICA = {
    "1440 dpi": "1440 DPI",
    "1440dpi": "1440 DPI",

    "720 dpi": "720 DPI",
    "720dpi": "720 DPI",

    "refilado": "Refilado",
    "impreso": "Impreso",
    "impresa": "Impresa",

    "en alturas": "En alturas",
    "instalación en alturas": "Instalación en alturas",
}


# ==========================================================
# DETECTAR ACCIONES
# ==========================================================

def detectar_acciones(
    texto
):

    texto_normalizado = normalizar_texto(
        texto
    )

    acciones_encontradas = []

    for accion, palabras in PALABRAS_ACCION.items():

        for palabra in palabras:

            palabra_normalizada = normalizar_texto(
                palabra
            )

            # Buscar la palabra completa y no una parte
            # de otra palabra.
            patron = r"(?<!\w)" + re.escape(
                palabra_normalizada
            ) + r"(?!\w)"

            if re.search(
                patron,
                texto_normalizado
            ):

                acciones_encontradas.append(
                    accion
                )

                break

    # ------------------------------------------------------
    # ELIMINAR DUPLICADOS
    # ------------------------------------------------------

    acciones_unicas = []

    for accion in acciones_encontradas:

        if accion not in acciones_unicas:

            acciones_unicas.append(
                accion
            )

    return acciones_unicas


# ==========================================================
# ELEGIR ACCIÓN PRINCIPAL
# ==========================================================

def determinar_accion_principal(
    texto,
    acciones
):

    if not acciones:

        return "Ambigua"

    # ------------------------------------------------------
    # PRIORIDADES
    # ------------------------------------------------------

    prioridades = [
        "Desinstalación",
        "Instalación",
        "Transporte",
        "Entrega",
        "Fabricación",
        "Producción",
        "Servicio",
        "Venta",
    ]

    for accion in prioridades:

        if accion in acciones:

            return accion

    return acciones[0]


# ==========================================================
# DETECTAR PRODUCTOS / ELEMENTOS
# ==========================================================

def detectar_productos(
    descripcion
):

    texto = normalizar_texto(
        descripcion
    )

    productos_encontrados = []

    for palabra, producto in PALABRAS_ELEMENTO.items():

        palabra_normalizada = normalizar_texto(
            palabra
        )

        patron = (
            r"(?<!\w)"
            + re.escape(palabra_normalizada)
            + r"(?!\w)"
        )

        coincidencia = re.search(
            patron,
            texto
        )

        if coincidencia:

            posicion = coincidencia.start()

            productos_encontrados.append(
                (
                    posicion,
                    producto
                )
            )

    # ------------------------------------------------------
    # ORDENAR SEGÚN APARICIÓN EN LA DESCRIPCIÓN
    # ------------------------------------------------------

    productos_encontrados.sort(
        key=lambda x: x[0]
    )

    # ------------------------------------------------------
    # ELIMINAR DUPLICADOS
    # ------------------------------------------------------

    productos = []

    for _, producto in productos_encontrados:

        if producto not in productos:

            productos.append(
                producto
            )

    return productos


# ==========================================================
# DETERMINAR PRODUCTO PRINCIPAL
# ==========================================================

def determinar_producto_principal(
    productos
):

    if not productos:

        return "No determinado"

    return productos[0]


# ==========================================================
# DETECTAR CARACTERÍSTICAS ESPECIALES
# ==========================================================

def detectar_caracteristicas(descripcion):
    texto = normalizar_texto(descripcion)

    caracteristicas = []

    # ========================================================
    # MATERIALES
    # ========================================================

    # Primero evaluamos las expresiones más largas/específicas.
    materiales_ordenados = sorted(
        PALABRAS_MATERIAL.items(),
        key=lambda x: len(x[0]),
        reverse=True
    )

    texto_trabajo = texto

    for palabra, valor in materiales_ordenados:

        if palabra in texto_trabajo:

            if valor not in caracteristicas:
                caracteristicas.append(valor)

            # Evita que después se detecte también
            # el término contenido dentro de esta expresión.
            texto_trabajo = texto_trabajo.replace(
                palabra,
                " "
            )

    # ========================================================
    # CARACTERÍSTICAS TÉCNICAS
    # ========================================================

    caracteristicas_ordenadas = sorted(
        PALABRAS_CARACTERISTICA.items(),
        key=lambda x: len(x[0]),
        reverse=True
    )

    for palabra, valor in caracteristicas_ordenadas:

        if palabra in texto and valor not in caracteristicas:
            caracteristicas.append(valor)

    return caracteristicas


# ==========================================================
# ANÁLISIS PRINCIPAL DEL ID
# ==========================================================

def analizar_id(
    registro
):

    texto = _texto(
        registro
    )

    acciones = detectar_acciones(
        texto
    )

    accion_principal = determinar_accion_principal(
        texto,
        acciones
    )

    productos = detectar_productos(
        texto
    )

    producto_principal = determinar_producto_principal(
        productos
    )

    caracteristicas = detectar_caracteristicas(
        texto
    )

    ambigua = (
        accion_principal == "Ambigua"
    )

    return {
        "texto": texto,
        "acciones": acciones,
        "accion": accion_principal,
        "productos": productos,
        "producto": producto_principal,
        "caracteristicas": caracteristicas,
        "ambigua": ambigua,
    }


def actividades_base_por_accion(
    accion,
    producto,
    caracteristicas=None,
    productos=None
):

    actividades = []

    if caracteristicas is None:

        caracteristicas = []

    if productos is None:

        productos = []    

    # ======================================================
    # DESINSTALACIÓN
    # ======================================================

    if accion == "Desinstalación":

        actividades = [
            "Preparar materiales y herramientas",
            f"Desinstalar {producto.lower()}"
            if producto != "No determinado"
            else "Desinstalar elemento",
            "Limpiar punto",
            "Retirar material desmontado",
            "Reporte fotográfico",
            "Reporte de servicio",
        ]

    # ======================================================
    # INSTALACIÓN
    # ======================================================

    elif accion == "Instalación":

        actividades = [
            "Preparar materiales y herramientas",
            "Preparar sitio de instalación",
            (
                f"Instalar {producto.lower()}"
                if producto != "No determinado"
                else "Instalar elemento"
            ),
            "Verificar instalación",
            "Reporte fotográfico",
        ]

    # ======================================================
    # TRANSPORTE
    # ======================================================

    elif accion == "Transporte":

        actividades = [
            "Preparar carga",
            "Cargar elementos",
            "Transportar elementos",
            "Descargar elementos",
            "Verificar entrega",
            "Reporte fotográfico",
        ]

    # ======================================================
    # ENTREGA
    # ======================================================

    elif accion == "Entrega":

        actividades = [
            "Preparar entrega",
            "Cargar elementos",
            "Transportar elementos",
            "Entregar elementos",
            "Verificar entrega",
            "Reporte fotográfico",
        ]

    # ======================================================
    # SERVICIO
    # ======================================================

    elif accion == "Servicio":

        actividades = [
            "Preparar materiales y herramientas",
            "Realizar servicio",
            "Verificar resultado",
            "Reporte fotográfico",
            "Reporte de servicio",
        ]

    # ======================================================
    # FABRICACIÓN
    # ======================================================

    elif accion == "Fabricación":

        actividades = [
            "Preparar materiales y herramientas",
            (
                f"Fabricar {producto.lower()}"
                if producto != "No determinado"
                else "Fabricar elemento"
            ),
            "Control de calidad",
            "Empaque",
        ]

    # ======================================================
    # PRODUCCIÓN
    # ======================================================

    elif accion == "Producción":

        actividades = [
            "Preparar materiales y herramientas",
            (
                f"Producir {producto.lower()}"
                if producto != "No determinado"
                else "Producir elemento"
            ),
            "Control de calidad",
            "Empaque",
        ]

    # ======================================================
    # VENTA
    # ======================================================

    elif accion == "Venta":

        actividades = []

        if producto == "No determinado":

            actividades = [
                "Revisar producto requerido",
                "Empacar producto",
            ]

        else:

            # ==================================================
            # COMPONENTES ESTRUCTURALES FABRICABLES
            # ==================================================

            if "Bastidor" in productos:

                actividades.append(
                    "Fabricar bastidor"
                )

            # ==================================================
            # PRODUCTO / ELEMENTO IMPRESO
            # ==================================================

            productos_impresos = [
                "Fototelón",
                "Lona",
                "Mural",
                "Vinilo",
            ]

            producto_impreso = None

            for elemento in productos:

                if elemento in productos_impresos:

                    producto_impreso = elemento

                    break

            es_impreso = (
                producto_impreso is not None
                and any(
                    caracteristica in [
                        "Impreso",
                        "Impresa",
                    ]
                    for caracteristica in caracteristicas
                )
            )

            # ==================================================
            # IMPRESIÓN
            # ==================================================

            if es_impreso:

                actividades.append(
                    "Impresión"
                )

                actividades.append(
                    "Acabados de impresión"
                )

            # ==================================================
            # ENSAMBLE DEL PRODUCTO COMPUESTO
            # ==================================================

            if len(productos) > 1:

                actividades.append(
                    "Ensamblar producto"
                )

            # ==================================================
            # INCORPORACIÓN DEL ELEMENTO IMPRESO
            # ==================================================

            if es_impreso:

                if producto_impreso == "Fototelón":

                    actividades.append(
                        "Templar fototelón"
                    )

                elif producto_impreso == "Lona":

                    actividades.append(
                        "Templar lona"
                    )

                elif producto_impreso in [
                    "Mural",
                    "Vinilo",
                ]:

                    actividades.append(
                        f"Decorar {producto_impreso.lower()}"
                    )

            # ==================================================
            # EMPAQUE
            # ==================================================

            actividades.append(
                "Empacar producto"
            )

    return actividades


# ==========================================================
# APLICAR REGLAS DE IMPRESIÓN
# ==========================================================

def aplicar_reglas_impresion(
    actividades,
    producto,
    caracteristicas,
    accion
):

    actividades = list(
        actividades
    )

    productos_impresos = [
        "Vinilo",
        "Fototelón",
        "Lona",
        "Mural",
    ]

    es_producto_impreso = (
        producto in productos_impresos
        and any(
            caracteristica in [
                "Impreso",
                "Impresa",
            ]
            for caracteristica in caracteristicas
        )
    )

    # ------------------------------------------------------
    # SOLO APLICA A PRODUCCIÓN/FABRICACIÓN/VENTA
    # ------------------------------------------------------

    if (
        es_producto_impreso
        and accion in [
            "Venta",
            "Fabricación",
            "Producción",
        ]
    ):

        if "Impresión" not in actividades:

            actividades.append(
                "Impresión"
            )

        

    # ------------------------------------------------------
    # SIEMPRE DEVOLVER LA LISTA
    # ------------------------------------------------------

    return actividades


# ==========================================================
# CONSULTAR HISTÓRICO DE DECISIONES
# ==========================================================

def consultar_historico(
    accion,
    producto,
    actividad
):

    df = cargar_historial()

    if df.empty:

        return {
            "aceptaciones": 0,
            "eliminaciones": 0,
            "agregaciones": 0,
            "total": 0,
        }

    filtro = (
        df["Acción"]
        .fillna("")
        .astype(str)
        .eq(accion)
        &
        df["Producto"]
        .fillna("")
        .astype(str)
        .eq(producto)
        &
        df["Actividad"]
        .fillna("")
        .astype(str)
        .str.lower()
        .eq(
            str(
                actividad
            ).lower()
        )
    )

    datos = df[
        filtro
    ]

    if datos.empty:

        return {
            "aceptaciones": 0,
            "eliminaciones": 0,
            "agregaciones": 0,
            "total": 0,
        }

    return {
        "aceptaciones": int(
            (
                datos["Decisión"]
                == "Aceptada"
            ).sum()
        ),
        "eliminaciones": int(
            (
                datos["Decisión"]
                == "Eliminada"
            ).sum()
        ),
        "agregaciones": int(
            (
                datos["Decisión"]
                == "Agregada"
            ).sum()
        ),
        "total": len(
            datos
        ),
    }


# ==========================================================
# CONSULTAR HISTÓRICO POR CONTEXTO
# ==========================================================

def actividades_aprendidas(
    accion,
    producto
):

    df = cargar_historial()

    if df.empty:

        return []

    filtro = (
        df["Acción"]
        .fillna("")
        .astype(str)
        .eq(accion)
        &
        df["Producto"]
        .fillna("")
        .astype(str)
        .eq(producto)
    )

    datos = df[
        filtro
    ].copy()

    if datos.empty:

        return []

    resultados = []

    actividades = (
        datos["Actividad"]
        .dropna()
        .astype(str)
        .str.strip()
        .unique()
    )

    for actividad in actividades:

        estadistica = consultar_historico(
            accion,
            producto,
            actividad
        )

        # --------------------------------------------------
        # CRITERIO DE APRENDIZAJE
        # --------------------------------------------------

        aceptaciones = (
            estadistica["aceptaciones"]
        )

        eliminaciones = (
            estadistica["eliminaciones"]
        )

        agregaciones = (
            estadistica["agregaciones"]
        )

        if (
            aceptaciones > eliminaciones
            or agregaciones > 0
        ):

            resultados.append(
                {
                    "actividad": actividad,
                    "aceptaciones": aceptaciones,
                    "eliminaciones": eliminaciones,
                    "agregaciones": agregaciones,
                }
            )

    return resultados


# ==========================================================
# APLICAR APRENDIZAJE HISTÓRICO
# ==========================================================

def aplicar_historico(
    actividades,
    accion,
    producto
):

    actividades_resultado = list(
        actividades
    )

    aprendidas = actividades_aprendidas(
        accion,
        producto
    )

    for registro in aprendidas:

        actividad = registro[
            "actividad"
        ]

        if actividad in actividades_resultado:

            continue

        # --------------------------------------------------
        # UNA SOLA APARICIÓN NO ES SUFICIENTE
        # --------------------------------------------------

        evidencia = (
            registro["aceptaciones"]
            + registro["agregaciones"]
        )

        eliminaciones = (
            registro["eliminaciones"]
        )

        if (
            evidencia >= 2
            and evidencia > eliminaciones
        ):

            actividades_resultado.append(
                actividad
            )

    return actividades_resultado


# ==========================================================
# FILTRAR ACTIVIDADES CONTRADICTORIAS
# ==========================================================

def filtrar_por_accion(
    actividades,
    accion
):

    resultado = []

    prohibidas = []

    # ======================================================
    # DESINSTALACIÓN
    # ======================================================

    if accion == "Desinstalación":

        prohibidas = [
            "impresión",
            "producción",
            "fabricación",
            "refilado",
            "laminado",
            "empaque",
            "instalación",
            "preparación de archivo",
        ]

    # ======================================================
    # INSTALACIÓN
    # ======================================================

    elif accion == "Instalación":

        prohibidas = [
            "desinstalación",
            "desinstalar",
            "fabricación",
            "producción",
            "preparación de archivo",
        ]

    # ======================================================
    # TRANSPORTE
    # ======================================================

    elif accion == "Transporte":

        prohibidas = [
            "fabricación",
            "producción",
            "impresión",
            "laminado",
            "refilado",
        ]

    # ======================================================
    # ENTREGA
    # ======================================================

    elif accion == "Entrega":

        prohibidas = [
            "fabricación",
            "producción",
            "impresión",
            "laminado",
            "refilado",
        ]

    # ======================================================
    # APLICAR FILTRO
    # ======================================================

    for actividad in actividades:

        texto = normalizar_texto(
            actividad
        )

        contradictoria = any(
            palabra in texto
            for palabra in prohibidas
        )

        if contradictoria:

            continue

        if actividad not in resultado:

            resultado.append(
                actividad
            )

    return resultado


# ==========================================================
# INCORPORAR CONOCIMIENTO MRP
# ==========================================================

def incorporar_conocimiento_mrp(
    descripcion,
    actividades,
    accion,
    producto
):

    resultado = list(
        actividades
    )

    # ======================================================
    # SOLO CONSULTAMOS MRP CUANDO TIENE SENTIDO
    # ======================================================

    if accion in [
        "Fabricación",
        "Producción",
        "Venta",
    ]:

        try:

            resultados_mrp = (
                buscar_contextos_similares(
                    descripcion,
                    top_n=10,
                    umbral=75
                )
            )

        except Exception:

            resultados_mrp = (
                pd.DataFrame()
            )

        if (
            resultados_mrp is not None
            and not resultados_mrp.empty
        ):

            operaciones = (
                resultados_mrp[
                    "Operación"
                ]
                .dropna()
                .astype(str)
                .str.strip()
                .tolist()
            )

            for operacion in operaciones:

                if not operacion:

                    continue

                # ------------------------------------------
                # No copiar operaciones administrativas
                # ------------------------------------------

                texto = normalizar_texto(
                    operacion
                )

                administrativas = [
                    "factur",
                    "cotizacion",
                    "pedido",
                    "cliente",
                    "administrativ",
                    "comercial",
                ]

                if any(
                    palabra in texto
                    for palabra in administrativas
                ):

                    continue

                # ------------------------------------------
                # Evitar contradicciones
                # ------------------------------------------

                propuesta_temporal = resultado + [
                    operacion
                ]

                propuesta_filtrada = (
                    filtrar_por_accion(
                        propuesta_temporal,
                        accion
                    )
                )

                if operacion not in (
                    resultado
                ) and operacion in (
                    propuesta_filtrada
                ):

                    resultado.append(
                        operacion
                    )

    return resultado


# ==========================================================
# ELIMINAR DUPLICADOS
# ==========================================================

def eliminar_duplicados(
    actividades
):

    resultado = []

    vistos = set()

    for actividad in actividades:

        texto = str(
            actividad
        ).strip()

        if not texto:

            continue

        clave = normalizar_texto(
            texto
        )

        if clave in vistos:

            continue

        vistos.add(
            clave
        )

        resultado.append(
            texto
        )

    return resultado


# ==========================================================
# PROPONER ACTIVIDADES
# ==========================================================

def proponer_actividades(
    registro
):

    analisis = analizar_id(
        registro
    )

    accion = analisis[
        "accion"
    ]

    producto = analisis[
        "producto"
    ]

    caracteristicas = analisis[
        "caracteristicas"
    ]

    descripcion = analisis[
        "texto"
    ]

    # ======================================================
    # PROPUESTA BASE
    # ======================================================

    actividades = (
        actividades_base_por_accion(
            accion,
            producto,
            caracteristicas,
            analisis["productos"]
        )
    )

    # ======================================================
    # PRODUCTOS IMPRESOS
    # ======================================================

    actividades = (
        aplicar_reglas_impresion(
            actividades,
            producto,
            caracteristicas,
            accion
        )
    )

    # ======================================================
    # CONSULTAR MRP
    # ======================================================

    actividades = (
        incorporar_conocimiento_mrp(
            descripcion,
            actividades,
            accion,
            producto
        )
    )

    # ======================================================
    # APLICAR HISTÓRICO
    # ======================================================

    actividades = (
        aplicar_historico(
            actividades,
            accion,
            producto
        )
    )

    # ======================================================
    # CASO AMBIGUO
    # ======================================================

    if accion == "Ambigua":

        actividades = [
            "Preparar materiales y herramientas",
            "Revisar elementos requeridos",
            "Preparar elemento",
            "Realizar trabajo requerido",
            "Verificar resultado",
            "Reporte fotográfico",
        ]

    # ======================================================
    # FILTRAR CONTRADICCIONES
    # ======================================================

    actividades = (
        filtrar_por_accion(
            actividades,
            accion
        )
    )

    # ======================================================
    # ELIMINAR DUPLICADOS
    # ======================================================

    actividades = (
        eliminar_duplicados(
            actividades
        )
    )

    # ======================================================
    # DEVOLVER ANÁLISIS
    # ======================================================

    analisis["actividades_generadas"] = (
        actividades
    )

    analisis["motor"] = (
        "Acción + Producto + "
        "Biblioteca MRP + Histórico"
    )

    return (
        actividades,
        analisis
    )


# ==========================================================
# ANALIZAR Y GUARDAR PROPUESTA
# ==========================================================

def analizar_y_guardar_propuesta(
    registro
):

    id_odoo = str(
        registro.get(
            "ID",
            registro.get(
                "ID Odoo",
                ""
            )
        )
    ).strip()

    referencia = str(
        registro.get(
            "Referencia del pedido",
            ""
        )
    ).strip()

    if not id_odoo:

        return (
            pd.DataFrame(
                columns=COLUMNAS_ACTIVIDADES
            ),
            {
                "tipo": "Por determinar",
                "familia": "General",
                "accion": "Ambigua",
                "producto": "No determinado",
                "texto": "El registro no contiene ID.",
                "actividades_generadas": [],
            },
        )

    # ======================================================
    # ANALIZAR
    # ======================================================

    propuestas, analisis = (
        proponer_actividades(
            registro
        )
    )

    # ======================================================
    # CARGAR ACTIVIDADES
    # ======================================================

    df = cargar_actividades()

    # ======================================================
    # ELIMINAR PROPUESTAS ANTERIORES
    # DEL MISMO ID
    # ======================================================

    if not df.empty:

        ids = (
            df["ID Odoo"]
            .fillna("")
            .astype(str)
            .str.strip()
        )

        estados_protegidos = [
            "Programada",
            "En ejecución",
            "Finalizada",
        ]

        conservar = ~(
            ids.eq(id_odoo)
            &
            ~df["Estado"].isin(
                estados_protegidos
            )
        )

        df = df[
            conservar
        ].copy()

    # ======================================================
    # CREAR NUEVAS PROPUESTAS
    # ======================================================

    nuevas = []

    for orden, actividad in enumerate(
        propuestas,
        start=1
    ):

        nuevas.append(
            {
                "ID Odoo": id_odoo,
                "Referencia del pedido": referencia,
                "Actividad": actividad,
                "Orden Propuesta": orden,
                "Origen": "Motor",
                "Seleccionada": False,
                "Fecha Programación": pd.NaT,
                "Estado": "Propuesta",
                "Observación": "",
            }
        )

    df_nuevas = pd.DataFrame(
        nuevas,
        columns=COLUMNAS_ACTIVIDADES
    )

    df_final = pd.concat(
        [
            df,
            df_nuevas,
        ],
        ignore_index=True
    )

    guardar_actividades(
        df_final
    )

    return (
        df_nuevas,
        analisis
    )


# ==========================================================
# AGREGAR ACTIVIDAD MANUAL
# ==========================================================

def agregar_actividad(
    id_odoo,
    referencia,
    actividad,
    observacion=""
):

    actividad = str(
        actividad
    ).strip()

    if not actividad:

        return False

    df = cargar_actividades()

    actividades_id = obtener_actividades_id(
        id_odoo
    )

    if actividades_id.empty:

        siguiente_orden = 1

    else:

        ordenes = pd.to_numeric(
            actividades_id[
                "Orden Propuesta"
            ],
            errors="coerce"
        )

        if ordenes.notna().any():

            siguiente_orden = (
                int(
                    ordenes.max()
                )
                + 1
            )

        else:

            siguiente_orden = 1

    nueva = {
        "ID Odoo": str(
            id_odoo
        ).strip(),

        "Referencia del pedido": str(
            referencia
        ).strip(),

        "Actividad": actividad,

        "Orden Propuesta":
            siguiente_orden,

        "Origen":
            "Usuario",

        "Seleccionada":
            False,

        "Fecha Programación":
            pd.NaT,

        "Estado":
            "Propuesta",

        "Observación":
            str(
                observacion
            ).strip(),
    }

    df = pd.concat(
        [
            df,
            pd.DataFrame(
                [nueva],
                columns=COLUMNAS_ACTIVIDADES
            ),
        ],
        ignore_index=True
    )

    guardar_actividades(
        df
    )

    return True


# ==========================================================
# REGISTRAR DECISIÓN EN HISTORIAL
# ==========================================================

def registrar_decision_actividad(
    registro,
    actividad,
    decision,
    origen_propuesta=""
):

    analisis = analizar_id(
        registro
    )

    fila = {
        "ID Odoo": str(
            registro.get(
                "ID",
                registro.get(
                    "ID Odoo",
                    ""
                )
            )
        ).strip(),

        "Referencia del pedido": str(
            registro.get(
                "Referencia del pedido",
                ""
            )
        ).strip(),

        "Descripción": str(
            registro.get(
                "Descripción",
                ""
            )
        ).strip(),

        "Acción": analisis[
            "accion"
        ],

        "Producto": analisis[
            "producto"
        ],

        "Actividad": str(
            actividad
        ).strip(),

        "Origen Propuesta": str(
            origen_propuesta
        ).strip(),

        "Decisión": str(
            decision
        ).strip(),

        "Fecha": pd.Timestamp.now(),
    }

    df = cargar_historial()

    df = pd.concat(
        [
            df,
            pd.DataFrame(
                [fila],
                columns=COLUMNAS_HISTORIAL
            ),
        ],
        ignore_index=True
    )

    guardar_historial(
        df
    )


# ==========================================================
# REGISTRAR VARIAS DECISIONES
# ==========================================================

def registrar_decisiones_actividades(
    registro,
    actividades_aceptadas,
    actividades_eliminadas,
    actividades_agregadas
):

    # ------------------------------------------------------
    # ACEPTADAS
    # ------------------------------------------------------

    for actividad in actividades_aceptadas:

        registrar_decision_actividad(
            registro,
            actividad,
            "Aceptada",
            "Motor"
        )

    # ------------------------------------------------------
    # ELIMINADAS
    # ------------------------------------------------------

    for actividad in actividades_eliminadas:

        registrar_decision_actividad(
            registro,
            actividad,
            "Eliminada",
            "Motor"
        )

    # ------------------------------------------------------
    # AGREGADAS POR USUARIO
    # ------------------------------------------------------

    for actividad in actividades_agregadas:

        registrar_decision_actividad(
            registro,
            actividad,
            "Agregada",
            "Usuario"
        )


# ==========================================================
# ANÁLISIS COMPATIBLE CON INTERFAZ ANTERIOR
# ==========================================================

def analizar_tipo_trabajo(
    texto
):

    acciones = detectar_acciones(
        texto
    )

    accion = determinar_accion_principal(
        texto,
        acciones
    )

    if accion in [
        "Fabricación",
        "Producción",
        "Venta",
    ]:

        return "Producto"

    if accion == "Ambigua":

        return "Por determinar"

    return "Servicio"


# ==========================================================
# DETECTAR FAMILIA COMPATIBLE
# ==========================================================

def detectar_familia(
    texto
):

    productos = detectar_productos(
        texto
    )

    if productos:

        return productos[0]

    return "General"


# ==========================================================
# MOSTRAR ACTIVIDADES DE UN ID
# ==========================================================

def mostrar_actividades_id(
    df_gestion
):

    st.divider()

    st.subheader(
        "🤖 Actividades propuestas por el motor"
    )

    st.caption(
        "El sistema analiza acción, producto, conocimiento "
        "histórico de Odoo y experiencias anteriores. "
        "El usuario conserva la decisión final."
    )

    if (
        df_gestion is None
        or df_gestion.empty
    ):

        st.info(
            "No hay IDs disponibles en Gestión ID."
        )

        return

    # ======================================================
    # SELECCIONAR ID
    # ======================================================

    opciones = df_gestion[
        [
            "ID",
            "Referencia del pedido",
            "Descripción",
        ]
    ].copy()

    opciones["Etiqueta"] = opciones.apply(
        lambda fila:
        f"{fila['ID']} | "
        f"{fila['Referencia del pedido']} | "
        f"{str(fila['Descripción'])[:100]}",
        axis=1
    )

    seleccion = st.selectbox(
        "Seleccione el ID que desea analizar",
        opciones["Etiqueta"].tolist(),
        key="selector_id_actividades"
    )

    indice = (
        opciones["Etiqueta"]
        .tolist()
        .index(seleccion)
    )

    id_seleccionado = str(
        opciones.iloc[indice]["ID"]
    ).strip()

    registro_completo = (
        df_gestion[
            df_gestion["ID"]
            .astype(str)
            .str.strip()
            .eq(id_seleccionado)
        ]
        .iloc[0]
        .to_dict()
    )

    # ======================================================
    # INFORMACIÓN DEL ID
    # ======================================================

    st.write(
        f"**ID:** {id_seleccionado}"
    )

    st.write(
        f"**Referencia:** "
        f"{registro_completo.get('Referencia del pedido', '')}"
    )

    st.write(
        f"**Descripción:** "
        f"{registro_completo.get('Descripción', '')}"
    )

    # ======================================================
    # ANALIZAR
    # ======================================================

    if st.button(
        "🤖 Analizar ID y proponer actividades",
        type="primary",
        key="analizar_id_actividades"
    ):

        nuevas, analisis = (
            analizar_y_guardar_propuesta(
                registro_completo
            )
        )

        st.session_state[
            "id_actividades_actual"
        ] = id_seleccionado

        st.session_state[
            "analisis_id_actual"
        ] = analisis

        st.success(
            f"Se generaron {len(nuevas)} "
            "actividades propuestas."
        )

        st.rerun()

    # ======================================================
    # MOSTRAR ANÁLISIS
    # ======================================================

    resultado = st.session_state.get(
        "analisis_id_actual"
    )

    if resultado:

        col1, col2, col3 = st.columns(3)

        with col1:

            st.write(
                f"**Acción:** "
                f"{resultado.get('accion', '')}"
            )

        with col2:

            st.write(
                f"**Producto:** "
                f"{resultado.get('producto', '')}"
            )

        with col3:

            if resultado.get("ambigua"):

                st.warning(
                    "⚠️ ID ambiguo"
                )

            else:

                st.success(
                    "✅ Acción identificada"
                )

    # ======================================================
    # ACTIVIDADES
    # ======================================================

    df_actividades = (
        obtener_actividades_id(
            id_seleccionado
        )
    )

    if df_actividades.empty:

        st.info(
            "No existen actividades para este ID."
        )

        return

    st.markdown(
        "### Actividades propuestas"
    )

    if "Orden Propuesta" in (
        df_actividades.columns
    ):

        df_actividades = (
            df_actividades
            .sort_values(
                "Orden Propuesta",
                na_position="last"
            )
        )

    st.dataframe(
        df_actividades[
            [
                "Actividad",
                "Orden Propuesta",
                "Origen",
                "Estado",
                "Seleccionada",
                "Observación",
            ]
        ],
        use_container_width=True,
        hide_index=True
    )

    # ======================================================
    # AGREGAR ACTIVIDAD MANUAL
    # ======================================================

    st.markdown(
        "### ➕ Agregar actividad manual"
    )

    nueva_actividad = st.text_input(
        "Actividad",
        key="nueva_actividad_manual"
    )

    nueva_observacion = st.text_input(
        "Observación",
        key="nueva_observacion_manual"
    )

    if st.button(
        "[ Agregar actividad ]",
        key="agregar_actividad_manual"
    ):

        resultado_agregar = agregar_actividad(
            id_seleccionado,
            str(
                registro_completo.get(
                    "Referencia del pedido",
                    ""
                )
            ),
            nueva_actividad,
            nueva_observacion
        )

        if resultado_agregar:

            st.success(
                "La actividad fue agregada."
            )

            st.rerun()

        else:

            st.warning(
                "Debe escribir una actividad."
            )

# ============================================================
# PRUEBA TEMPORAL
# ============================================================

if __name__ == "__main__":

    pruebas = [
        "Venta de MURALES con Vinilo adhesivo Avery 3822 laminado mate",
        "Venta de Mural con Bastidor en aluminio",
        "Venta de Bastidor con Fototelon en aluminio",
        "Desinstalacion de Valla con Vinilo adhesivo",
        "Instalacion de Bastidor con Fototelon",
        "Venta de Lona impresa con Bastidor en aluminio",
    ]

    for descripcion in pruebas:

        print("\n----------------------------------------")
        print("DESCRIPCION:")
        print(descripcion)

        acciones = detectar_acciones(descripcion)

        print("ACCIONES:")
        print(acciones)

        print("ACCION PRINCIPAL:")
        print(determinar_accion_principal(descripcion, acciones))

        print("PRODUCTOS:")
        print(detectar_productos(descripcion))

        print("CARACTERISTICAS:")
        print(detectar_caracteristicas(descripcion))

        print("ACTIVIDADES PROPUESTAS:")

        actividades, analisis = proponer_actividades(
            {
                "ID": "PRUEBA",
                "Referencia del pedido": "PRUEBA",
                "Descripción": descripcion,
            }
        )

        for actividad in actividades:
            print(
                f"  - {actividad}"
            )

print("\n========================================")
print("PRUEBA DE COMPONENTES")
print("========================================")

pruebas_componentes = [
    "Venta de Bastidor con Fototelon en aluminio",
    "Venta de Lona impresa con Bastidor en aluminio",
    "Venta de Vinilo impreso para muro",
    "Venta de Valla existente con Vinilo impreso",
    "Instalacion de Aviso en fachada",
    "Venta de Fotovinilo para puerta",
]

for descripcion_prueba in pruebas_componentes:

    componentes = detectar_componentes(
        descripcion_prueba
    )

    print("\nDESCRIPCION:")
    print(descripcion_prueba)

    print("ESTRUCTURALES:")
    print(componentes["estructurales"])

    print("ESTRUCTURALES EXISTENTES:")
    print(componentes["estructurales_existentes"])

    print("IMPRESION:")
    print(componentes["impresion"])

    print("SOPORTES:")
    print(componentes["soportes"])            