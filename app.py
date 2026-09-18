import streamlit as st
from pathlib import Path
import pandas as pd
from odoo_api import OdooAPI

from programacion import mostrar_programacion
from actividades import mostrar_actividades_id
from catalogo_actividades import cargar_catalogo, guardar_catalogo, COLUMNAS_CATALOGO


# ==========================================================
# CONFIGURACIÓN
# ==========================================================

st.set_page_config(
    page_title="Programador Inteligente HERCAS",
    page_icon="📋",
    layout="wide"
)

# ==========================================================
# RUTAS DE DATOS
# ==========================================================

CARPETA_DATOS = Path("datos")

ARCHIVO_ODOO = CARPETA_DATOS / "ids_odoo.pkl"

ARCHIVO_GESTION = CARPETA_DATOS / "gestion_id.pkl"

ARCHIVO_PERSONAL = CARPETA_DATOS / "personal.pkl"

ARCHIVO_LISTAS_PERSONAL = CARPETA_DATOS / "listas_personal.pkl"

ARCHIVO_BIBLIOTECA_MRP = (
    CARPETA_DATOS / "biblioteca_mrp.pkl"
)

# ==========================================================
# ARCHIVO DE DISPONIBILIDAD DIARIA DEL PERSONAL
# ==========================================================

ARCHIVO_DISPONIBILIDAD = (
    CARPETA_DATOS / "disponibilidad_personal.pkl"
)


# ==========================================================
# ESTRUCTURA DE DISPONIBILIDAD DIARIA
# ==========================================================

COLUMNAS_DISPONIBILIDAD = [
    "Fecha",
    "Código",
    "Nombre Completo",
    "Cargo Principal",
    "Estado Disponibilidad",
    "Turno",
    "Última Actualización"
]


CARPETA_DATOS.mkdir(
    exist_ok=True
)

# ==========================================================
# ESTRUCTURA DE DATOS DE PERSONAL
# ==========================================================

COLUMNAS_PERSONAL = [
    "Código",
    "Nombre Completo",
    "Tipo Personal",
    "Estado Disponibilidad",
    "Cargo Principal",
    "Especialidad",
    "Nivel",
    "Productividad",
    "Experiencia",
    "Turno",
    "Puede Viajar",
    "Licencia Conducción",
    "Categoría Licencia",
    "Curso Alturas Avanzado",
    "Coordinador de alturas",
    "Espacios Confinados",
    "Restricción Médica",
    "Observaciones"
]


# ==========================================================
# CARGAR PERSONAL
# ==========================================================

def cargar_personal():

    if not ARCHIVO_PERSONAL.exists():

        return None

    try:

        df = pd.read_pickle(
            ARCHIVO_PERSONAL
        )

        # --------------------------------------------------
        # ASEGURAR COLUMNAS DEL MAESTRO DE PERSONAL
        # --------------------------------------------------

        for columna in COLUMNAS_PERSONAL:

            if columna not in df.columns:

                if columna in [
                    "Cargo Principal",
                    "Especialidad",
                    "Nivel",
                    "Productividad",
                    "Experiencia"
                ]:
                    df[columna] = "Ninguno"

                elif columna == "Estado Disponibilidad":
                    df[columna] = "Disponible"

                elif columna == "Turno":
                    df[columna] = "Diurno"

                elif columna in [
                    "Puede Viajar",
                    "Licencia Conducción",
                    "Curso Alturas Avanzado",
                    "Coordinador de alturas",
                    "Espacios Confinados",
                    "Restricción Médica"
                ]:
                    df[columna] = "No"

                else:
                    df[columna] = ""

        # --------------------------------------------------
        # MANTENER ORDEN OFICIAL
        # --------------------------------------------------

        df = df[COLUMNAS_PERSONAL]

        return df

    except Exception:

        return None


# ==========================================================
# CARGAR LISTAS DE PERSONAL
# ==========================================================

def cargar_listas_personal():

    if not ARCHIVO_LISTAS_PERSONAL.exists():

        return None

    try:

        return pd.read_pickle(
            ARCHIVO_LISTAS_PERSONAL
        )

    except Exception:

        return None


# ==========================================================
# GUARDAR LISTAS DE PERSONAL
# ==========================================================

def guardar_listas_personal(
    df_listas
):

    df_listas.to_pickle(
        ARCHIVO_LISTAS_PERSONAL
    )


# ==========================================================
# GUARDAR PERSONAL
# ==========================================================

def guardar_personal(df):

    df.to_pickle(
        ARCHIVO_PERSONAL
    )


# ==========================================================
# ELIMINAR TODOS LOS DATOS DE PERSONAL
# ==========================================================

def eliminar_personal():

    archivos_eliminar = [
        ARCHIVO_PERSONAL,
        ARCHIVO_DISPONIBILIDAD
    ]

    resultado = []

    for archivo in archivos_eliminar:

        if archivo.exists():

            try:

                archivo.unlink()

                resultado.append(
                    f"Eliminado: {archivo.name}"
                )

            except Exception as e:

                resultado.append(
                    f"ERROR {archivo.name}: {e}"
                )

        else:

            resultado.append(
                f"No existe: {archivo.name}"
            )

    return resultado

# ==========================================================
# ELIMINAR UNA PERSONA
# ==========================================================

def eliminar_persona(codigo_persona):

    # CARGAR PERSONAL
    df_personal = cargar_personal()

    if df_personal is None or df_personal.empty:
        return False, "No existe Personal registrado."

    # NORMALIZAR CÓDIGO
    codigo_persona = str(codigo_persona).strip()

    df_personal["Código"] = (
        df_personal["Código"]
        .astype(str)
        .str.strip()
    )

    # VERIFICAR QUE EXISTA
    if codigo_persona not in df_personal["Código"].values:
        return False, "La persona seleccionada no existe."

    # ELIMINAR PERSONA
    df_personal = df_personal[
        df_personal["Código"] != codigo_persona
    ].copy()

    # GUARDAR PERSONAL ACTUALIZADO
    guardar_personal(df_personal)

    # ELIMINAR DISPONIBILIDAD ASOCIADA
    if ARCHIVO_DISPONIBILIDAD.exists():

        try:

            df_disponibilidad = pd.read_pickle(
                ARCHIVO_DISPONIBILIDAD
            )

            if not df_disponibilidad.empty:

                df_disponibilidad["Código"] = (
                    df_disponibilidad["Código"]
                    .astype(str)
                    .str.strip()
                )

                df_disponibilidad = df_disponibilidad[
                    df_disponibilidad["Código"] != codigo_persona
                ].copy()

                df_disponibilidad.to_pickle(
                    ARCHIVO_DISPONIBILIDAD
                )

        except Exception as e:

            return False, (
                "La persona fue eliminada, pero ocurrió un "
                f"error al actualizar la disponibilidad: {e}"
            )

    return True, "Persona eliminada correctamente."    

# ==========================================================
# DISPONIBILIDAD DIARIA DEL PERSONAL
# ==========================================================

def cargar_disponibilidad():

    if not ARCHIVO_DISPONIBILIDAD.exists():

        return None

    try:

        return pd.read_pickle(
            ARCHIVO_DISPONIBILIDAD
        )

    except Exception:

        return None


def guardar_disponibilidad(df):

    df.to_pickle(
        ARCHIVO_DISPONIBILIDAD
    )


# ==========================================================
# CREAR DISPONIBILIDAD DEL DÍA
# ==========================================================

def crear_disponibilidad_del_dia(
    df_personal,
    fecha
):

    registros = []

    for _, persona in df_personal.iterrows():

        registro = {}

        # --------------------------------------------------
        # DATOS BÁSICOS
        # --------------------------------------------------

        registro["Fecha"] = fecha

        registro["Código"] = (
            str(persona.get("Código", "")).strip()
        )

        registro["Nombre Completo"] = (
            str(persona.get("Nombre Completo", "")).strip()
        )

        registro["Cargo Principal"] = (
            str(persona.get("Cargo Principal", "Ninguno")).strip()
        )

        # --------------------------------------------------
        # DISPONIBILIDAD
        # --------------------------------------------------

        disponibilidad = persona.get(
            "Estado Disponibilidad",
            "Disponible"
        )

        if pd.isna(disponibilidad):
            disponibilidad = "Disponible"

        disponibilidad = str(
            disponibilidad
        ).strip()

        if disponibilidad == "":
            disponibilidad = "Disponible"

        registro["Estado Disponibilidad"] = disponibilidad

        # --------------------------------------------------
        # TURNO
        # --------------------------------------------------

        turno = persona.get(
            "Turno",
            "Diurno"
        )

        if pd.isna(turno):
            turno = "Diurno"

        turno = str(
            turno
        ).strip()

        if turno == "":
            turno = "Diurno"

        registro["Turno"] = turno

        # --------------------------------------------------
        # ÚLTIMA ACTUALIZACIÓN
        # --------------------------------------------------

        registro["Última Actualización"] = pd.Timestamp.now()

        registros.append(
            registro
        )

    # ------------------------------------------------------
    # CREAR DATAFRAME
    # ------------------------------------------------------

    return pd.DataFrame(
        registros,
        columns=COLUMNAS_DISPONIBILIDAD
    )

    registros = []

    for _, persona in df_personal.iterrows():

        registros.append({

            "Fecha": fecha,

            "Código": persona["Código"],

            "Nombre Completo": persona["Nombre Completo"],

            "Cargo Principal": persona["Cargo Principal"],

            "Estado Disponibilidad": persona[
                "Estado Disponibilidad"
            ],

            "Turno": persona["Turno"],

            "Última Actualización": datetime.now()

        })

    return pd.DataFrame(
        registros,
        columns=COLUMNAS_DISPONIBILIDAD
    )

# ==========================================================
# ESTRUCTURA DE DATOS DE ODOO
# ==========================================================

COLUMNAS_ODOO = [
    "Cliente",
    "Referencia del pedido",
    "ID",
    "Descripción",
    "Cantidad",
    "Fecha Orden",
    "Fecha Entrega Producción",
    "Subtotal",
    "Estado ID"
]



# ==========================================================
# ESTRUCTURA DE GESTION_ID
# ==========================================================

COLUMNAS_GESTION = [
    "Cliente",
    "Referencia del pedido",
    "ID",
    "Descripción",
    "Cantidad",
    "Fecha Orden",
    "Fecha Entrega Producción",
    "Días Restantes",
    "Situación de Plazo",
    "Prioridad",
    "Fecha Última Sincronización",
    "Estado Registro",
    "Estado Programador",
    "Programar Hoy",
    "Programado Para",
    "Actividad 1",
    "Actividad 2",
    "Actividad 3",
    "Actividad 4",
    "Actividad 5",
    "Actividad 6",
    "Actividad 7",
    "Actividad 8",
    "Actividad 9",
    "Actividad 10",
    "Observaciones"
]


# ==========================================================
# ESTADOS DE GESTION_ID
# ==========================================================

ESTADOS_REGISTRO = [
    "Nuevo",
    "Vigente",
    "Programado",
    "En ejecución",
    "Finalizado",
    "Cancelado",
    "No vigente"
]


# ==========================================================
# FUNCIONES DE DATOS
# ==========================================================

def cargar_odoo():

    if not ARCHIVO_ODOO.exists():
        return None

    try:

        return pd.read_pickle(
            ARCHIVO_ODOO
        )

    except Exception:

        return None


def cargar_gestion():

    if not ARCHIVO_GESTION.exists():
        return None

    try:

        return pd.read_pickle(
            ARCHIVO_GESTION
        )

    except Exception:

        return None

def cargar_biblioteca_mrp():

    if not ARCHIVO_BIBLIOTECA_MRP.exists():
        return None

    try:

        return pd.read_pickle(
            ARCHIVO_BIBLIOTECA_MRP
        )

    except Exception:

        return None 

def guardar_personal(df):

    df.to_pickle(
        ARCHIVO_PERSONAL
    )

def guardar_gestion(df):

    df.to_pickle(
        ARCHIVO_GESTION
    )

# ==========================================================
# CALCULAR DÍAS RESTANTES Y SITUACIÓN DE PLAZO
# ==========================================================

def calcular_situacion_plazo(fecha_entrega):

    if pd.isna(fecha_entrega):

        return "", None


    try:

        fecha_entrega = pd.to_datetime(
            fecha_entrega
        ).normalize()

    except Exception:

        return "", None


    hoy = pd.Timestamp.now().normalize()


    dias_restantes = (
        fecha_entrega - hoy
    ).days


    # ------------------------------------------------------
    # CLASIFICAR SITUACIÓN DE PLAZO
    # ------------------------------------------------------

    if dias_restantes < 0:

        situacion_plazo = "VENCIÓ"

    elif dias_restantes == 0:

        situacion_plazo = "HOY"

    elif dias_restantes <= 5:

        situacion_plazo = "PRÓXIMA"

    else:

        situacion_plazo = "CON HOLGURA"


    return situacion_plazo, dias_restantes

# ==========================================================
# CREAR GESTION_ID DESDE ODOO
# ==========================================================

def crear_gestion_desde_odoo(df_odoo):

    ahora = pd.Timestamp.now()

    gestion = pd.DataFrame(
        columns=COLUMNAS_GESTION
    )


    # ------------------------------------------------------
    # CAMPOS PROVENIENTES DE ODOO
    # ------------------------------------------------------

    for columna in COLUMNAS_ODOO:

        if columna in df_odoo.columns:

            gestion[columna] = df_odoo[columna].values

        else:

            gestion[columna] = None


    # ------------------------------------------------------
    # CAMPOS CONTROLADOS POR LA APLICACIÓN
    # ------------------------------------------------------

    gestion[
        "Fecha Última Sincronización"
    ] = ahora


    gestion[
        "Estado Registro"
    ] = "Nuevo"

    gestion[
        "Estado Programador"
    ] = ""

    gestion[
        "Programar Hoy"
    ] = "NO"

    gestion[
        "Programado Para"
    ] = pd.NaT

    gestion[
        "Prioridad"
    ] = ""

    # ------------------------------------------------------
    # CALCULAR SITUACIÓN DE PLAZO Y DÍAS RESTANTES
    # ------------------------------------------------------

    situaciones_plazo = []
    dias_restantes = []

    for fecha in gestion[
        "Fecha Entrega Producción"
    ]:

        situacion_plazo, dias = calcular_situacion_plazo(
            fecha
        )

        situaciones_plazo.append(
            situacion_plazo
        )

        dias_restantes.append(
            dias
        )


    gestion[
        "Situación de Plazo"
    ] = situaciones_plazo

    gestion[
        "Días Restantes"
    ] = dias_restantes


    for numero in range(1, 11):

        gestion[
            f"Actividad {numero}"
        ] = ""

    for numero in range(1, 11):

        gestion[
            f"Actividad {numero}"
        ] = ""


    gestion[
        "Observaciones"
    ] = ""


    # ------------------------------------------------------
    # ORDEN DEFINITIVO
    # ------------------------------------------------------

    gestion = gestion[
        COLUMNAS_GESTION
    ]


    return gestion


# ==========================================================
# SINCRONIZAR GESTION_ID
# ==========================================================

def sincronizar_gestion(
    df_odoo,
    df_gestion
):

    ahora = pd.Timestamp.now()


    # ------------------------------------------------------
    # SI NO EXISTE GESTION
    # ------------------------------------------------------

    if df_gestion is None:

        return crear_gestion_desde_odoo(
            df_odoo
        )


    # ------------------------------------------------------
    # ASEGURAR COLUMNAS
    # ------------------------------------------------------

    for columna in COLUMNAS_GESTION:

        if columna not in df_gestion.columns:

            if columna == "Programar Hoy":

                df_gestion[columna] = "NO"

            elif columna == "Programado Para":

                df_gestion[columna] = pd.NaT    

            elif columna == "Estado Registro":

                df_gestion[columna] = "Nuevo"

            elif columna == "Fecha Última Sincronización":

                df_gestion[columna] = ahora

            elif columna == "Días Restantes":

                df_gestion[columna] = pd.Series(
                    dtype="Int64"
                )

            else:

                df_gestion[columna] = ""


    df_gestion = df_gestion[
        COLUMNAS_GESTION
    ].copy()

    # ------------------------------------------------------
    # ASEGURAR TIPO NUMÉRICO DE DÍAS RESTANTES
    # ------------------------------------------------------

    df_gestion["Días Restantes"] = pd.to_numeric(
        df_gestion["Días Restantes"],
        errors="coerce"
    ).astype("Int64")

    # ------------------------------------------------------
    # ELIMINAR DUPLICADOS POR ID
    # ------------------------------------------------------

    df_gestion["ID"] = (
        df_gestion["ID"]
        .astype(str)
        .str.strip()
    )

    df_gestion = (
        df_gestion
        .drop_duplicates(
            subset=["ID"],
            keep="last"
        )
        .reset_index(drop=True)
    )

    # ------------------------------------------------------
    # NORMALIZAR ID
    # ------------------------------------------------------

    df_gestion["ID"] = (
        df_gestion["ID"]
        .astype(str)
        .str.strip()
    )

    df_odoo = df_odoo.copy()

    df_odoo["ID"] = (
        df_odoo["ID"]
        .astype(str)
        .str.strip()
    )


    # ------------------------------------------------------
    # ÍNDICE POR ID
    # ------------------------------------------------------

    indice_gestion = {
        valor: posicion
        for posicion, valor
        in enumerate(df_gestion["ID"])
    }


    # ------------------------------------------------------
    # ACTUALIZAR / INSERTAR
    # ------------------------------------------------------

    for _, fila in df_odoo.iterrows():

        identificador = str(
            fila["ID"]
        ).strip()


        # --------------------------------------------------
        # ID EXISTENTE
        # --------------------------------------------------

        if identificador in indice_gestion:

            posicion = indice_gestion[
                identificador
            ]


            # ----------------------------------------------
            # ACTUALIZAR SOLAMENTE CAMPOS DE ODOO
            # ----------------------------------------------

            for columna in COLUMNAS_ODOO:

                df_gestion.loc[
                    posicion,
                    columna
                ] = fila.get(
                    columna,
                    None
                )


            # ----------------------------------------------
            # FECHA DE SINCRONIZACIÓN
            # ----------------------------------------------

            df_gestion.loc[
                posicion,
                "Fecha Última Sincronización"
            ] = ahora

            # --------------------------------------------------
            # RECALCULAR SITUACIÓN DE PLAZO Y DÍAS RESTANTES
            # --------------------------------------------------

            situacion_plazo, dias = calcular_situacion_plazo(
                df_gestion.loc[
                    posicion,
                    "Fecha Entrega Producción"
                ]
            )

            df_gestion.loc[
                posicion,
                "Situación de Plazo"
            ] = situacion_plazo

            df_gestion.loc[
                posicion,
                "Días Restantes"
            ] = dias

            # ----------------------------------------------
            # NUEVO → VIGENTE
            # ----------------------------------------------

            estado_actual = df_gestion.loc[
                posicion,
                "Estado Registro"
            ]


            if estado_actual == "Nuevo":

                df_gestion.loc[
                    posicion,
                    "Estado Registro"
                ] = "Vigente"


        # --------------------------------------------------
        # ID NUEVO
        # --------------------------------------------------

        else:

            nuevo = {
                columna: fila.get(
                    columna,
                    None
                )
                for columna in COLUMNAS_ODOO
            }


            nuevo[
                "Fecha Última Sincronización"
            ] = ahora


            nuevo[
                "Estado Registro"
            ] = "Nuevo"

            nuevo[
                "Estado Programador"
            ] = ""
             
                          
            nuevo[
                "Programar Hoy"
            ] = "NO"

            nuevo[
                "Programado Para"
            ] = pd.NaT
            
            nuevo[
                "Prioridad"
            ] = ""


            for numero in range(1, 11):

                nuevo[
                    f"Actividad {numero}"
                ] = ""


            nuevo[
                "Observaciones"
            ] = ""


            df_gestion.loc[
                len(df_gestion)
            ] = nuevo


    # ------------------------------------------------------
    # IDS QUE YA NO VIENEN DE ODOO
    # ------------------------------------------------------

    ids_odoo = set(
        df_odoo["ID"]
    )


    for posicion in range(
        len(df_gestion)
    ):

        identificador = str(
            df_gestion.loc[
                posicion,
                "ID"
            ]
        ).strip()


        if identificador not in ids_odoo:

            estado_actual = df_gestion.loc[
                posicion,
                "Estado Registro"
            ]


            # ----------------------------------------------
            # SOLO MARCAR COMO NO VIGENTE LOS QUE AÚN
            # NO HAN ENTRADO EN PROCESOS POSTERIORES
            # ----------------------------------------------

            if estado_actual in [
                "Nuevo",
                "Vigente"
            ]:

                df_gestion.loc[
                    posicion,
                    "Estado Registro"
                ] = "No vigente"


    # ------------------------------------------------------
    # ORDEN FINAL
    # ------------------------------------------------------

    return df_gestion[
        COLUMNAS_GESTION
    ].copy()


# ==========================================================
# NAVEGACIÓN
# ==========================================================

st.sidebar.title(
    "📋 Programador HERCAS"
)


pagina = st.sidebar.radio(
    "Navegación",
    [
        "🏠 Inicio",
        "📋 Importación Odoo",
        "📚 Biblioteca MRP",
        "📁 Gestión ID",
        "👷 Personal",
        "🧠 Competencias",
        "🔧 Actividades",
        "📚 Maestro de Actividades",
        "📅 Programación",  
        "👥 Programación Personal",
        "📄 Órdenes de Servicio"
    ]
)


# ==========================================================
# ENCABEZADO
# ==========================================================

st.title(
    "📋 PROGRAMADOR INTELIGENTE HERCAS"
)

st.caption(
    "Sistema de programación de equipos de trabajo "
    "y Órdenes de Servicio"
)

# ==========================================================
# DIÁLOGO DE CONFIRMACIÓN - BORRADO TOTAL
# ==========================================================

@st.dialog("🚨 Confirmar borrado total")
def confirmar_borrado_total():

    st.warning(
        "Esta operación eliminará TODOS los datos "
        "almacenados actualmente en la aplicación."
    )

    st.write(
        "Se eliminarán:"
    )

    st.write(
        "• Importación Odoo"
    )

    st.write(
        "• Gestión ID"
    )

    st.error(
        "⚠️ Esta acción no se puede deshacer."
    )

    col1, col2 = st.columns(2)

    with col1:

        if st.button(
            "🚨 Sí, borrar todo",
            type="primary",
            key="dialog_confirmar_borrado_total"
        ):

            if ARCHIVO_ODOO.exists():
                ARCHIVO_ODOO.unlink()

            if ARCHIVO_GESTION.exists():
                ARCHIVO_GESTION.unlink()

            st.success(
                "🟢 Todos los datos fueron eliminados."
            )

            st.rerun()

    with col2:

        if st.button(
            "Cancelar",
            key="dialog_cancelar_borrado_total"
        ):

            st.rerun()

# ==========================================================
# INICIO
# ==========================================================

if pagina == "🏠 Inicio":

    st.header(
        "🏠 Inicio"
    )


    df_odoo = cargar_odoo()

    df_gestion = cargar_gestion()


    # ------------------------------------------------------
    # MÉTRICAS
    # ------------------------------------------------------

    col1, col2, col3, col4 = st.columns(4)


    with col1:

        st.metric(
            "📋 Identificaciones Odoo",
            0 if df_odoo is None
            else len(df_odoo)
        )


    with col2:

        st.metric(
            "📁 Gestión ID",
            0 if df_gestion is None
            else len(df_gestion)
        )


    with col3:

        st.metric(
            "👷 Personal",
            "Pendiente"
        )


    with col4:

        st.metric(
            "🔧 Actividades",
            "Pendiente"
        )


    st.divider()


    if df_gestion is not None:

        st.success(
            "🟢 Gestión ID disponible."
        )

        st.write(
            f"Registros gestionados: "
            f"**{len(df_gestion)}**"
        )

    else:

        st.info(
            "Gestión ID todavía no ha sido creada."
        )

    # ======================================================
    # ADMINISTRACIÓN DE DATOS
    # ======================================================

    st.divider()

    st.subheader(
        "⚠️ Administración de datos"
    )

    st.warning(
        "Esta operación eliminará TODOS los datos "
        "almacenados actualmente en la aplicación."
    )

    if st.button(
        "🗑️ BORRAR TODOS LOS DATOS",
        type="secondary",
        key="abrir_dialogo_borrado_total"
    ):

        confirmar_borrado_total()


    # ======================================================
    # ELIMINAR SOLAMENTE IMPORTACIÓN ODOO
    # ======================================================

    st.divider()

    st.subheader(
        "📋 Datos de importación Odoo"
    )

    if ARCHIVO_ODOO.exists():

        try:

            df_importacion = pd.read_pickle(
                ARCHIVO_ODOO
            )

            cantidad_odoo = len(
                df_importacion
            )

        except Exception:

            cantidad_odoo = 0

    else:

        cantidad_odoo = 0


    st.write(
        f"Registros de Odoo almacenados: "
        f"**{cantidad_odoo}**"
    )


    if cantidad_odoo > 0:

        if st.button(
            "🗑️ Eliminar solamente Importación Odoo",
            key="eliminar_importacion_odoo"
        ):

            ARCHIVO_ODOO.unlink(
                missing_ok=True
            )

            st.success(
                "🟢 Importación Odoo eliminada correctamente."
            )

            st.info(
                "📁 Gestión ID no fue modificada."
            )

            st.rerun()

    else:

        st.info(
            "No existen datos de importación Odoo."
        )   


# ==========================================================
# IMPORTACIÓN ODOO
# ==========================================================

elif pagina == "📋 Importación Odoo":

    st.header(
        "📋 Importación Odoo"
    )

    st.write(
        "Suba aquí el archivo Excel generado desde Odoo."
    )


    archivo = st.file_uploader(
        "Seleccionar archivo Excel",
        type=["xlsx", "xls"]
    )


    df_guardado = cargar_odoo()


    if df_guardado is not None:

        st.success(
            f"🟢 Datos almacenados: "
            f"{len(df_guardado)} registros."
        )


    if archivo is not None:

        try:

            libro_excel = pd.ExcelFile(
                archivo
            )


            st.success(
                f"🟢 Archivo leído correctamente. "
                f"Hoja utilizada: {libro_excel.sheet_names[0]}"
            )

            # --------------------------------------------------
            # UTILIZAR LA PRIMERA HOJA
            # --------------------------------------------------

            nombre_hoja = (
                libro_excel.sheet_names[0]
            )


            df = pd.read_excel(
                archivo,
                sheet_name=nombre_hoja
            )

            # --------------------------------------------------
            # LIMPIAR NOMBRES DE COLUMNAS
            # --------------------------------------------------

            df.columns = [
                str(columna).strip()
                for columna in df.columns
            ]


            st.write(
                f"Registros encontrados: "
                f"**{len(df)}**"
            )


            st.dataframe(
                df,
                width="stretch",
                hide_index=True
            )


            # --------------------------------------------------
            # VALIDAR COLUMNAS PRINCIPALES
            # --------------------------------------------------

            faltantes = [
                columna
                for columna in COLUMNAS_ODOO
                if columna not in df.columns
            ]


            if faltantes:

                st.warning(
                    "El archivo no contiene algunas "
                    "columnas esperadas:"
                )

                for columna in faltantes:

                    st.write(
                        f"- {columna}"
                    )


            else:

                if st.button(
                    "📥 Importar datos a la aplicación",
                    type="primary"
                ):

                    guardar = df.copy()


                    guardar["ID"] = (
                        guardar["ID"]
                        .astype(str)
                        .str.strip()
                    )


                    # ------------------------------------------
                    # GUARDAR SOLAMENTE LOS CAMPOS DE ODOO
                    # ------------------------------------------

                    guardar = guardar[
                        COLUMNAS_ODOO
                    ].copy()


                    guardar.to_pickle(
                        ARCHIVO_ODOO
                    )


                    st.success(
                        "🟢 Datos de Odoo guardados "
                        "correctamente."
                    )


                    st.rerun()


        except Exception as error:

            st.error(
                "Error al leer el archivo."
            )

            st.exception(
                error
            )


# ==========================================================
# GESTIÓN ID
# ==========================================================

elif pagina == "📁 Gestión ID":

    st.header(
        "📁 Gestión ID"
    )


    df_odoo = cargar_odoo()

    df_gestion = cargar_gestion()


    # ======================================================
    # ESTADO DE IMPORTACIÓN ODOO
    # ======================================================

    if df_odoo is None:

        st.info(
            "ℹ️ No existe una importación Odoo activa. "
            "La Gestión ID almacenada se puede consultar "
            "y editar, pero no se puede sincronizar con Odoo."
        )


    # ======================================================
    # SINCRONIZAR GESTIÓN ID
    # ======================================================

    if df_odoo is not None:

        if st.button(
            "🔄 Sincronizar Gestión ID",
            type="primary"
        ):

            df_gestion = sincronizar_gestion(
                df_odoo.copy(),
                df_gestion
            )

            guardar_gestion(
                df_gestion
            )

            st.success(
                f"🟢 Gestión ID sincronizada: "
                f"{len(df_gestion)} registros."
            )

            st.rerun()

    else:

        st.button(
            "🔄 Sincronizar Gestión ID",
            disabled=True
        )


    # ======================================================
    # CARGAR INFORMACIÓN ACTUAL
    # ======================================================

    df_gestion = cargar_gestion()


    if df_gestion is None:

        st.info(
            "Gestión ID todavía no ha sido creada."
        )

        st.stop()


    # ======================================================
    # ASEGURAR ESTADOS DE GESTIÓN ID
    # ======================================================

    if "Estado Registro" not in df_gestion.columns:

        df_gestion["Estado Registro"] = ""


    # ------------------------------------------------------
    # LIMPIAR VALORES VACÍOS
    # ------------------------------------------------------

    df_gestion["Estado Registro"] = (
        df_gestion["Estado Registro"]
        .fillna("")
        .astype(str)
        .str.strip()
    )


    # ------------------------------------------------------
    # NORMALIZAR IDs DE GESTIÓN
    # ------------------------------------------------------

    ids_gestion = (
        df_gestion["ID"]
        .astype(str)
        .str.strip()
    )


    # ------------------------------------------------------
    # ACTUALIZAR ESTADOS CON ODOO
    # ------------------------------------------------------

    if df_odoo is not None:

        ids_odoo = (
            df_odoo["ID"]
            .astype(str)
            .str.strip()
        )


        # --------------------------------------------------
        # REGISTROS SIN ESTADO
        # --------------------------------------------------

        condicion_sin_estado = (
            (df_gestion["Estado Registro"] == "")
            &
            (ids_gestion.isin(ids_odoo))
        )


        df_gestion.loc[
            condicion_sin_estado,
            "Estado Registro"
        ] = "Vigente"


        # --------------------------------------------------
        # GUARDAR CORRECCIÓN
        # --------------------------------------------------

        guardar_gestion(
            df_gestion
        )


    # ======================================================
    # INFORMACIÓN GENERAL
    # ======================================================

    st.write(
        f"Registros: **{len(df_gestion)}**"
    )


    # ======================================================
    # RESUMEN POR ESTADO
    # ======================================================

    resumen = (
        df_gestion[
            "Estado Registro"
        ]
        .value_counts()
        .reindex(
            ESTADOS_REGISTRO,
            fill_value=0
        )
        .reset_index()
    )


    resumen.columns = [
        "Estado",
        "Cantidad"
    ]


    st.subheader(
        "Resumen por estado"
    )


    st.dataframe(
        resumen,
        width="stretch",
        hide_index=True
    )

    # ======================================================
    # FILTROS DE GESTIÓN
    # ======================================================

    st.subheader(
        "🔎 Filtros"
    )


    col1, col2, col3, col4, col5, col6 = st.columns(6)


    # ------------------------------------------------------
    # FILTRO ESTADO REGISTRO
    # ------------------------------------------------------

    with col1:

        filtro_estado = st.multiselect(
            "Estado Registro",
            options=[
                estado
                for estado in ESTADOS_REGISTRO
                if estado in df_gestion[
                    "Estado Registro"
                ].unique()
            ],
            default=[]
        )


    # ------------------------------------------------------
    # FILTRO PROGRAMAR HOY
    # ------------------------------------------------------

    with col2:

        filtro_programar = st.multiselect(
            "Programar Hoy",
            options=[
                "SI",
                "NO"
            ],
            default=[]
        )


    # ------------------------------------------------------
    # FILTRO ESTADO PROGRAMADOR
    # ------------------------------------------------------

    with col3:

        filtro_programador = st.multiselect(
            "Estado Programador",
            options=[
                "",
                "Programado",
                "En ejecución",
                "Finalizado",
                "Cancelado"
            ],
            default=[]
        )


    # ------------------------------------------------------
    # FILTRO CLIENTE
    # ------------------------------------------------------

    with col4:

        clientes_disponibles = sorted(
            df_gestion[
                "Cliente"
            ]
            .fillna("")
            .astype(str)
            .unique()
            .tolist()
        )

        filtro_cliente = st.multiselect(
            "Cliente",
            options=clientes_disponibles,
            default=[]
        )

    # ------------------------------------------------------
    # FILTRO SITUACIÓN DE PLAZO
    # ------------------------------------------------------

    with col5:

        filtro_situacion_plazo = st.multiselect(
            "Situación de Plazo",
            options=[
                "VENCIÓ",
                "HOY",
                "PRÓXIMA",
                "CON HOLGURA"
            ],
            default=[]
        )

    # ------------------------------------------------------
    # FILTRO PRIORIDAD
    # ------------------------------------------------------

    with col6:

        filtro_prioridad = st.multiselect(
            "Prioridad",
            options=[
                "Prioridad Alta",
                "Prioridad Media",
                "Prioridad Baja",
                "Prioridad Nula"
            ],
            default=[]
        )

    # ======================================================
    # APLICAR FILTROS
    # ======================================================

    df_mostrar = df_gestion.copy()


    # ------------------------------------------------------
    # FILTRO ESTADO
    # ------------------------------------------------------

    if filtro_estado:

        df_mostrar = df_mostrar[
            df_mostrar[
                "Estado Registro"
            ].isin(
                filtro_estado
            )
        ]


    # ------------------------------------------------------
    # FILTRO PROGRAMAR HOY
    # ------------------------------------------------------

    if filtro_programar:

        df_mostrar = df_mostrar[
            df_mostrar[
                "Programar Hoy"
            ].isin(
                filtro_programar
            )
        ]


    # ------------------------------------------------------
    # FILTRO ESTADO PROGRAMADOR
    # ------------------------------------------------------

    if filtro_programador:

        df_mostrar = df_mostrar[
            df_mostrar[
                "Estado Programador"
            ].isin(
                filtro_programador
            )
        ]


    # ------------------------------------------------------
    # FILTRO CLIENTE
    # ------------------------------------------------------

    if filtro_cliente:

        df_mostrar = df_mostrar[
            df_mostrar[
                "Cliente"
            ]
            .fillna("")
            .astype(str)
            .isin(
                filtro_cliente
            )
        ]


    # ------------------------------------------------------
    # FILTRO SITUACIÓN DE PLAZO
    # ------------------------------------------------------

    if filtro_situacion_plazo:

        df_mostrar = df_mostrar[
            df_mostrar[
                "Situación de Plazo"
            ]
            .fillna("")
            .astype(str)
            .str.strip()
            .isin(
                filtro_situacion_plazo
            )
        ]


    # ------------------------------------------------------
    # FILTRO PRIORIDAD
    # ------------------------------------------------------

    if filtro_prioridad:

        df_mostrar = df_mostrar[
            df_mostrar[
                "Prioridad"
            ]
            .fillna("")
            .astype(str)
            .str.strip()
            .isin(
                filtro_prioridad
            )
        ]

    # ======================================================
    # RESULTADO DEL FILTRO
    # ======================================================

    st.write(
        f"Registros mostrados: "
        f"**{len(df_mostrar)}** "
        f"de **{len(df_gestion)}**"
    )

    

    # ======================================================
    # TABLA DE GESTIÓN
    # ======================================================

    st.subheader(
        "Registros"
    )


    df_editado = st.data_editor(

        df_mostrar,

        width="stretch",

        hide_index=True,

        disabled=[
            "Cliente",
            "Referencia del pedido",
            "ID",
            "Descripción",
            "Cantidad",
            "Fecha Orden",
            "Fecha Entrega Producción",
            "Subtotal",
            "Estado ID",
            "Fecha Última Sincronización",
            "Estado Registro",
            "Actividad 1",
            "Actividad 2",
            "Actividad 3",
            "Actividad 4",
            "Actividad 5",
            "Actividad 6",
            "Actividad 7",
            "Actividad 8",
            "Actividad 9",
            "Actividad 10",
            "Observaciones"
        ],

        column_config={
            
            "Programado Para":
                st.column_config.DateColumn(
                    "Programado Para",
                    format="DD/MM/YYYY"
                ),

            "Prioridad":
                st.column_config.SelectboxColumn(
                    "Prioridad",
                    options=[
                        "Prioridad Alta",
                        "Prioridad Media",
                        "Prioridad Baja",
                        "Prioridad Nula"
                    ],
                    required=True
                ),  

            "Estado Programador":
                st.column_config.SelectboxColumn(
                    "Estado Programador",
                    options=[
                        "Programado",
                        "En ejecución",
                        "Finalizado",
                        "Cancelado"
                    ],
                    required=False
                )
        },

        key="editor_gestion_id_v2"
    )

    # ======================================================
    # ACTIVIDADES DEL ID
    # ======================================================

    mostrar_actividades_id(df_gestion)


    # ======================================================
    # LIMPIEZA DE GESTIÓN ID
    # ======================================================

    st.divider()

    st.subheader(
        "🗑️ Limpieza de Gestión ID"
    )

    st.caption(
        "La limpieza solamente afecta la base temporal "
        "de Gestión ID. No elimina información de Odoo."
    )


    col1, col2 = st.columns(2)


    # ======================================================
    # ELIMINAR FINALIZADOS Y CANCELADOS
    # ======================================================

    with col1:

        st.write(
            "### 🗑️ Finalizados y Cancelados"
        )

        cantidad_eliminar = df_gestion[
            df_gestion[
                "Estado Registro"
            ].isin([
                "Finalizado",
                "Cancelado"
            ])
        ].shape[0]

        st.write(
            f"Registros que se eliminarían: "
            f"**{cantidad_eliminar}**"
        )


        if st.button(
            "🗑️ Eliminar Finalizados y Cancelados",
            type="secondary"
        ):

            if cantidad_eliminar == 0:

                st.info(
                    "No existen registros Finalizados "
                    "o Cancelados para eliminar."
                )

            else:

                st.session_state[
                    "confirmar_eliminacion"
                ] = True


        # --------------------------------------------------
        # CONFIRMACIÓN
        # --------------------------------------------------

        if st.session_state.get(
            "confirmar_eliminacion",
            False
        ):

            st.warning(
                f"⚠️ Está a punto de eliminar "
                f"**{cantidad_eliminar} registros** "
                "Finalizados o Cancelados."
            )

            confirmar = st.checkbox(
                "Sí, deseo eliminar estos registros.",
                key="confirmar_finalizados_cancelados"
            )


            if confirmar:

                if st.button(
                    "✅ Confirmar eliminación",
                    key="confirmar_eliminacion_finalizados"
                ):

                    df_gestion = df_gestion[
                        ~df_gestion[
                            "Estado Registro"
                        ].isin([
                            "Finalizado",
                            "Cancelado"
                        ])
                    ].copy()


                    guardar_gestion(
                        df_gestion
                    )


                    st.session_state[
                        "confirmar_eliminacion"
                    ] = False


                    st.success(
                        f"🟢 Se eliminaron "
                        f"{cantidad_eliminar} registros."
                    )


                    st.rerun()


    # ======================================================
    # VACIAR TODA LA GESTIÓN ID
    # ======================================================

    with col2:

        st.write(
            "### ⚠️ Vaciar Gestión ID"
        )

        cantidad_total = len(
            df_gestion
        )

        st.write(
            f"Registros actuales: "
            f"**{cantidad_total}**"
        )


        if st.button(
            "⚠️ Vaciar toda Gestión ID",
            type="secondary"
        ):

            st.session_state[
                "confirmar_vaciado"
            ] = True


        # --------------------------------------------------
        # CONFIRMACIÓN
        # --------------------------------------------------

        if st.session_state.get(
            "confirmar_vaciado",
            False
        ):

            st.error(
                f"⚠️ ATENCIÓN: se eliminarán "
                f"**{cantidad_total} registros** "
                "de Gestión ID."
            )

            st.write(
                "Esta acción NO elimina los datos "
                "almacenados en Odoo."
            )


            confirmar_vaciado = st.checkbox(
                "Sí, deseo vaciar completamente Gestión ID.",
                key="confirmar_vaciado_total"
            )


            if confirmar_vaciado:

                if st.button(
                    "🚨 CONFIRMAR VACIADO TOTAL",
                    key="confirmar_vaciado_total_boton"
                ):

                    df_vacio = pd.DataFrame(
                        columns=COLUMNAS_GESTION
                    )


                    guardar_gestion(
                        df_vacio
                    )


                    st.session_state[
                        "confirmar_vaciado"
                    ] = False


                    st.success(
                        "🟢 Gestión ID ha sido vaciada."
                    )


                    st.rerun()


    # ======================================================
    # GUARDAR PROGRAMACIÓN
    # ======================================================

    if st.button(
        "💾 Guardar cambios de programación",
        type="primary"
    ):

        # --------------------------------------------------
        # COPIAR VALORES EDITADOS
        # --------------------------------------------------
        
        estado_programador = (
            df_editado["Estado Programador"]
            .fillna("")
            .astype(str)
            .str.strip()
        )

        prioridad = (
            df_editado["Prioridad"]
            .fillna("")
            .astype(str)
            .str.strip()
        )


        # --------------------------------------------------
        # GUARDAR PROGRAMAR HOY
        # --------------------------------------------------

        

        df_gestion["Prioridad"] = prioridad

        # --------------------------------------------------
        # CALCULAR PROGRAMAR HOY AUTOMÁTICAMENTE
        #
        # Programado Para = HOY  → SI
        # Programado Para ≠ HOY  → NO
        # Programado Para vacío   → NO
        # --------------------------------------------------

        hoy = pd.Timestamp.now().normalize()

        programado_para = pd.to_datetime(
            df_editado["Programado Para"],
            errors="coerce"
        ).dt.normalize()

        df_gestion["Programado Para"] = programado_para

        df_gestion["Programar Hoy"] = (
            programado_para == hoy
        ).map(
            {
                True: "SI",
                False: "NO"
            }
        )

        # --------------------------------------------------
        # REGLA 1
        #
        # PROGRAMAR HOY = SI
        #
        # El ID queda PROGRAMADO.
        # --------------------------------------------------

        condicion_programar = (
            df_gestion["Programar Hoy"] == "SI"
        )

        df_gestion.loc[
            condicion_programar,
            "Estado Registro"
        ] = "Programado"

        df_gestion.loc[
            condicion_programar,
            "Estado Programador"
        ] = "Programado"


        # --------------------------------------------------
        # REGLA 2
        #
        # ESTADO DEFINIDO MANUALMENTE POR EL PROGRAMADOR
        # --------------------------------------------------

        condicion_en_ejecucion = (
            estado_programador == "En ejecución"
        )

        df_gestion.loc[
            condicion_en_ejecucion,
            "Estado Registro"
        ] = "En ejecución"

        df_gestion.loc[
            condicion_en_ejecucion,
            "Estado Programador"
        ] = "En ejecución"


        # --------------------------------------------------
        # REGLA 3
        #
        # FINALIZADO
        #
        # El programador decide que terminó.
        # --------------------------------------------------

        condicion_finalizado = (
            estado_programador == "Finalizado"
        )

        df_gestion.loc[
            condicion_finalizado,
            "Estado Registro"
        ] = "Finalizado"

        df_gestion.loc[
            condicion_finalizado,
            "Estado Programador"
        ] = "Finalizado"

        df_gestion.loc[
            condicion_finalizado,
            "Programar Hoy"
        ] = "NO"


        # --------------------------------------------------
        # REGLA 4
        #
        # CANCELADO
        #
        # El programador decide cancelar.
        # --------------------------------------------------

        condicion_cancelado = (
            estado_programador == "Cancelado"
        )

        df_gestion.loc[
            condicion_cancelado,
            "Estado Registro"
        ] = "Cancelado"

        df_gestion.loc[
            condicion_cancelado,
            "Estado Programador"
        ] = "Cancelado"

        df_gestion.loc[
            condicion_cancelado,
            "Programar Hoy"
        ] = "NO"


        # --------------------------------------------------
        # GUARDAR
        # --------------------------------------------------

        guardar_gestion(
            df_gestion
        )


        st.success(
            "🟢 Cambios de programación guardados correctamente."
        )


        st.rerun()

# ==========================================================
# BIBLIOTECA MRP
# ==========================================================

elif pagina == "📚 Biblioteca MRP":

    from biblioteca_mrp import (
        cargar_biblioteca_mrp,
        buscar_contextos_similares,
        resumir_operaciones,
    )

    st.header(
        "📚 Biblioteca MRP"
    )

    st.caption(
        "Biblioteca de conocimiento operativo obtenida "
        "desde Odoo MRP. Esta información sirve como "
        "contexto histórico para el generador de actividades."
    )

    # ======================================================
    # ESTADO DE LA BIBLIOTECA
    # ======================================================

    df_mrp_actual = cargar_biblioteca_mrp()

    if df_mrp_actual is not None:

        st.success(
            "🟢 Biblioteca MRP disponible."
        )

        col1, col2 = st.columns(2)

        with col1:

            st.metric(
                "Registros almacenados",
                len(df_mrp_actual)
            )

        with col2:

            st.metric(
                "Campos disponibles",
                len(df_mrp_actual.columns)
            )

    else:

        st.warning(
            "⚠️ Todavía no existe una Biblioteca MRP."
        )

    # ======================================================
    # ACTUALIZAR BIBLIOTECA
    # ======================================================

    st.divider()

    st.subheader(
        "📥 Actualizar Biblioteca MRP"
    )

    st.write(
        "Seleccione el archivo Excel exportado desde "
        "Odoo: Utilización del centro de producción "
        "(mrp.routing.workcenter)."
    )

    archivo_mrp = st.file_uploader(
        "Seleccionar archivo Excel de Odoo MRP",
        type=["xlsx", "xls"],
        key="importar_biblioteca_mrp"
    )

    if archivo_mrp is not None:

        try:

            # --------------------------------------------------
            # LEER LIBRO
            # --------------------------------------------------

            libro_excel = pd.ExcelFile(
                archivo_mrp
            )

            nombre_hoja = (
                libro_excel.sheet_names[0]
            )

            df_mrp = pd.read_excel(
                archivo_mrp,
                sheet_name=nombre_hoja
            )

            # --------------------------------------------------
            # LIMPIAR NOMBRES DE CAMPOS
            # --------------------------------------------------

            df_mrp.columns = [
                str(columna).strip()
                for columna in df_mrp.columns
            ]

            st.success(
                f"Archivo leído correctamente. "
                f"Hoja: {nombre_hoja}"
            )

            st.write(
                f"Registros encontrados: "
                f"**{len(df_mrp)}**"
            )

            # --------------------------------------------------
            # CAMPOS OBLIGATORIOS
            # --------------------------------------------------

            campos_obligatorios = [
                "Operación",
                "Lista de materiales",
                "Centro de trabajo",
                "Cálculo de duración",
                "Duración",
                "Instrucciones",
            ]

            faltantes = [
                campo
                for campo in campos_obligatorios
                if campo not in df_mrp.columns
            ]

            if faltantes:

                st.error(
                    "❌ Faltan campos obligatorios."
                )

                st.write(
                    "Campos faltantes:"
                )

                for campo in faltantes:

                    st.write(
                        f"- {campo}"
                    )

            else:

                st.success(
                    "✅ Todos los campos requeridos "
                    "fueron encontrados."
                )

                st.dataframe(
                    df_mrp.head(100),
                    use_container_width=True,
                    hide_index=True
                )

                # --------------------------------------------------
                # BOTÓN ACTUALIZAR
                # --------------------------------------------------

                if st.button(
                    "🔄 Actualizar Biblioteca MRP",
                    type="primary",
                    key="actualizar_biblioteca_mrp"
                ):

                    df_guardar = df_mrp[
                        campos_obligatorios
                    ].copy()

                    df_guardar.to_pickle(
                        ARCHIVO_BIBLIOTECA_MRP
                    )

                    st.success(
                        "🟢 Biblioteca MRP actualizada "
                        "correctamente."
                    )

                    st.info(
                        "El histórico de decisiones del "
                        "Programador no fue modificado."
                    )

                    st.rerun()

        except Exception as error:

            st.error(
                "❌ Error al leer el archivo MRP."
            )

            st.exception(
                error
            )

    # ======================================================
    # PRUEBA DE BÚSQUEDA DE CONOCIMIENTO
    # ======================================================

    st.divider()

    st.subheader(
        "🔎 Probar conocimiento de Odoo"
    )

    st.caption(
        "Esta prueba NO genera actividades. "
        "Solamente busca contextos históricos similares "
        "en la Biblioteca MRP."
    )

    descripcion_prueba = st.text_area(
        "Descripción del ID",
        height=150,
        placeholder=(
            "Ejemplo: Venta de MURALES con Vinilo "
            "adhesivo Avery 3822..."
        ),
        key="descripcion_prueba_mrp"
    )

    col1, col2 = st.columns(2)

    with col1:

        top_n = st.number_input(
            "Cantidad de contextos a mostrar",
            min_value=1,
            max_value=20,
            value=5,
            step=1,
            key="top_n_mrp"
        )

    with col2:

        umbral = st.slider(
            "Similitud mínima",
            min_value=40,
            max_value=100,
            value=70,
            step=5,
            key="umbral_mrp"
        )

    if st.button(
        "🔎 Buscar en Biblioteca MRP",
        type="primary",
        key="buscar_conocimiento_mrp"
    ):

        if not descripcion_prueba.strip():

            st.warning(
                "Ingrese una descripción para realizar "
                "la búsqueda."
            )

        else:

            resultados = (
                buscar_contextos_similares(
                    descripcion_prueba,
                    top_n=int(top_n),
                    umbral=int(umbral)
                )
            )

            if resultados.empty:

                st.warning(
                    "No se encontraron contextos con "
                    f"una similitud mínima de {umbral}%."
                )

            else:

                st.success(
                    f"Se encontraron "
                    f"{len(resultados)} contextos similares."
                )

                # ----------------------------------------------
                # CONTEXTOS ENCONTRADOS
                # ----------------------------------------------

                st.markdown(
                    "### Contextos encontrados"
                )

                st.dataframe(
                    resultados,
                    use_container_width=True,
                    hide_index=True
                )

                # ----------------------------------------------
                # RESUMEN DE OPERACIONES
                # ----------------------------------------------

                resumen = (
                    resumir_operaciones(
                        resultados
                    )
                )

                if not resumen.empty:

                    st.markdown(
                        "### Operaciones históricas encontradas"
                    )

                    st.dataframe(
                        resumen,
                        use_container_width=True,
                        hide_index=True
                    )

                # ----------------------------------------------
                # DETALLE
                # ----------------------------------------------

                st.markdown(
                    "### Detalle de los contextos"
                )

                for numero, (_, registro) in enumerate(
                    resultados.iterrows(),
                    start=1
                ):

                    operacion = str(
                        registro.get(
                            "Operación",
                            ""
                        )
                    )

                    lista_materiales = str(
                        registro.get(
                            "Lista de materiales",
                            ""
                        )
                    )

                    centro_trabajo = str(
                        registro.get(
                            "Centro de trabajo",
                            ""
                        )
                    )

                    duracion = registro.get(
                        "Duración",
                        ""
                    )

                    similitud = registro.get(
                        "Similitud",
                        0
                    )

                    with st.expander(
                        f"{numero}. "
                        f"{operacion} | "
                        f"Similitud: {similitud}%"
                    ):

                        st.write(
                            f"**Operación:** "
                            f"{operacion}"
                        )

                        st.write(
                            f"**Centro de trabajo:** "
                            f"{centro_trabajo}"
                        )

                        st.write(
                            f"**Duración:** "
                            f"{duracion}"
                        )

                        st.write(
                            "**Lista de materiales / "
                            "contexto encontrado:**"
                        )

                        st.write(
                            lista_materiales
                        )

  
# ==========================================================
# PERSONAL
# ==========================================================

elif pagina == "👷 Personal":

    st.header(
        "👷 Personal"
    )

    st.write(
        "Gestión del maestro de personal de HERCAS."
    )

    st.divider()


    # ======================================================
    # ESTADO DEL ARCHIVO DE PERSONAL
    # ======================================================

    if ARCHIVO_PERSONAL.exists():

        st.subheader(
            "📁 Archivo de Personal"
        )

        st.success(
            "Existe un archivo de Personal cargado."
        )

        if st.button(
            "🗑️ Eliminar archivo de Personal",
            type="secondary",
            key="boton_eliminar_personal"
        ):

            st.session_state[
                "mostrar_confirmacion_eliminar_personal"
            ] = True


        # ==================================================
        # CONFIRMACIÓN DE ELIMINACIÓN
        # ==================================================

        if st.session_state.get(
            "mostrar_confirmacion_eliminar_personal",
            False
        ):

            st.warning(
                "⚠️ Esta acción eliminará TODOS los datos "
                "actualmente almacenados del maestro de Personal."
            )

            st.warning(
                "También se eliminará la disponibilidad diaria "
                "asociada al Personal."
            )

            st.error(
                "Esta acción no se puede deshacer."
            )


            confirmar = st.checkbox(
                "Sí, quiero eliminar definitivamente "
                "todo el Personal.",
                key="check_confirmar_eliminacion_personal"
            )


            col_confirmar, col_cancelar = st.columns(2)


            with col_confirmar:

                if st.button(
                    "🗑️ CONFIRMAR ELIMINACIÓN",
                    type="primary",
                    
                ):

                    if not confirmar:

                        st.error(
                            "Debe marcar la casilla de confirmación "
                            "antes de eliminar."
                        )

                    else:

                        resultado = eliminar_personal()

                        # ----------------------------------
                        # LIMPIAR ESTADO DE CONFIRMACIÓN
                        # ----------------------------------

                        st.session_state[
                            "mostrar_confirmacion_eliminar_personal"
                        ] = False

                        st.session_state.pop(
                            "check_confirmar_eliminacion_personal",
                            None
                        )

                        # ----------------------------------
                        # MOSTRAR RESULTADO
                        # ----------------------------------

                        for mensaje in resultado:

                            if mensaje.startswith(
                                "ERROR"
                            ):

                                st.error(
                                    mensaje
                                )

                            else:

                                st.success(
                                    mensaje
                                )

                        st.success(
                            "✅ El maestro de Personal y su "
                            "disponibilidad fueron eliminados."
                        )

                        st.rerun()


            with col_cancelar:

                if st.button(
                    "↩️ CANCELAR",
                    key="cancelar_eliminacion_personal"
                ):

                    st.session_state[
                        "confirmar_eliminacion_personal"
                    ] = False

                    st.rerun()


    else:

        st.info(
            "📭 No existe un archivo de Personal. "
            "El módulo está actualmente virgen."
        )

    # ======================================================
    # CARGAR PERSONAL ACTUAL
    # ======================================================

    df_personal = cargar_personal()

    if df_personal is not None:

        st.success(
            f"🟢 Personal almacenado: "
            f"{len(df_personal)} registros."
        )

    else:

        st.info(
            "ℹ️ Todavía no existe una tabla de Personal "
            "almacenada en la aplicación."
        )

    st.divider()

    # ======================================================
    # IMPORTAR EXCEL
    # ======================================================

    st.subheader(
        "📥 Importar Personal desde Excel"
    )

    st.write(
        "Seleccione el archivo Excel que contiene "
        "la hoja 'Personal'."
    )

    archivo_personal = st.file_uploader(
        "Seleccionar archivo Tabla Empleados",
        type=["xlsx", "xls"],
        key="importar_personal"
    )

    if archivo_personal is not None:

        try:

            libro_excel = pd.ExcelFile(
                archivo_personal
            )

            # --------------------------------------------------
            # VALIDAR HOJA PERSONAL
            # --------------------------------------------------

            if "Personal" not in libro_excel.sheet_names:

                st.error(
                    "❌ El archivo no contiene una hoja llamada "
                    "'Personal'."
                )

            else:

                st.success(
                    "🟢 Hoja 'Personal' encontrada."
                )


                # --------------------------------------------------
                # VALIDAR HOJA LISTAS
                # --------------------------------------------------

                if "Listas" not in libro_excel.sheet_names:

                    st.warning(
                        "⚠️ El archivo no contiene una hoja llamada "
                        "'Listas'."
                    )

                    df_listas = None

                else:

                    st.success(
                        "🟢 Hoja 'Listas' encontrada."
                    )

                    # --------------------------------------------------
                    # LEER HOJA LISTAS
                    # --------------------------------------------------

                    df_listas = pd.read_excel(
                        archivo_personal,
                        sheet_name="Listas"
                    )

                    # --------------------------------------------------
                    # LIMPIAR NOMBRES DE COLUMNAS
                    # --------------------------------------------------

                    df_listas.columns = [
                        str(columna).strip()
                        for columna in df_listas.columns
                    ]

                    # --------------------------------------------------
                    # NORMALIZAR VALORES VACÍOS COMO "Ninguno"
                    # --------------------------------------------------

                    COLUMNAS_LISTAS = [
                        "Cargo Principal",
                        "Especialidad",
                        "Nivel",
                        "Productividad",
                        "Experiencia"
                    ]

                    for campo in COLUMNAS_LISTAS:

                        if campo in df_listas.columns:

                            df_listas[campo] = (
                                df_listas[campo]
                                .fillna("Ninguno")
                                .astype(str)
                                .str.strip()
                            )

                            df_listas.loc[
                                df_listas[campo] == "",
                                campo
                            ] = "Ninguno"


                # --------------------------------------------------
                # LEER HOJA PERSONAL
                # --------------------------------------------------

                df = pd.read_excel(
                    archivo_personal,
                    sheet_name="Personal"
                )


                # --------------------------------------------------
                # LIMPIAR NOMBRES DE COLUMNAS
                # --------------------------------------------------

                df.columns = [
                    str(columna).strip()
                    for columna in df.columns
                ]


                # ==================================================
                # NORMALIZAR CAMPOS VACÍOS COMO "Ninguno"
                # ==================================================

                CAMPOS_NINGUNO = [
                    "Cargo Principal",
                    "Especialidad",
                    "Nivel",
                    "Productividad",
                    "Experiencia"
                ]


                for campo in CAMPOS_NINGUNO:

                    if campo in df.columns:

                        df[campo] = (
                            df[campo]
                            .fillna("Ninguno")
                            .astype(str)
                            .str.strip()
                        )

                        df.loc[
                            df[campo] == "",
                            campo
                        ] = "Ninguno"


                # --------------------------------------------------
                # REGISTROS ENCONTRADOS
                # --------------------------------------------------

                st.write(
                    f"Registros encontrados: "
                    f"**{len(df)}**"
                )

                # --------------------------------------------------
                # VALIDAR COLUMNAS
                # --------------------------------------------------

                faltantes = [
                    columna
                    for columna in COLUMNAS_PERSONAL
                    if columna not in df.columns
                ]

                if faltantes:

                    st.error(
                        "❌ Faltan columnas requeridas "
                        "en la hoja Personal:"
                    )

                    for columna in faltantes:

                        st.write(
                            f"- {columna}"
                        )

                else:

                    st.success(
                        "🟢 Todas las columnas requeridas "
                        "fueron encontradas."
                    )

                    # --------------------------------------------------
                    # VISTA PREVIA
                    # --------------------------------------------------

                    st.subheader(
                        "👀 Vista previa"
                    )

                    st.dataframe(
                        df[
                            COLUMNAS_PERSONAL
                        ],
                        width="stretch",
                        hide_index=True
                    )

                    # --------------------------------------------------
                    # IMPORTAR
                    # --------------------------------------------------

                    if st.button(
                        "💾 Guardar Personal",
                        type="primary",
                        key="guardar_personal_excel"
                    ):

                        guardar = df[
                            COLUMNAS_PERSONAL
                        ].copy()

                        # --------------------------------------------------
                        # LIMPIAR CÓDIGOS
                        # --------------------------------------------------

                        guardar["Código"] = (
                            guardar["Código"]
                            .fillna("")
                            .astype(str)
                            .str.strip()
                        )

                        # --------------------------------------------------
                        # ELIMINAR FILAS SIN CÓDIGO
                        # --------------------------------------------------

                        guardar = guardar[
                            guardar["Código"] != ""
                        ].copy()

                        # --------------------------------------------------
                        # ELIMINAR DUPLICADOS POR CÓDIGO
                        # --------------------------------------------------

                        guardar = (
                            guardar
                            .drop_duplicates(
                                subset=["Código"],
                                keep="last"
                            )
                            .reset_index(drop=True)
                        )

                        # --------------------------------------------------
                        # GUARDAR PERSONAL
                        # --------------------------------------------------

                        guardar_personal(
                            guardar
                        )


                        # --------------------------------------------------
                        # GUARDAR LISTAS
                        # --------------------------------------------------

                        if df_listas is not None:

                            guardar_listas_personal(
                                df_listas
                            )


                        st.success(
                            f"🟢 Personal guardado correctamente: "
                            f"{len(guardar)} registros."
                        )

                        st.rerun()

        except Exception as error:

            st.error(
                "❌ Error al leer el archivo de Personal."
            )

            st.exception(
                error
            )

    st.divider()

    # ======================================================
    # NUEVO PERSONAL
    # ======================================================

    st.subheader(
        "➕ Agregar Personal"
    )

    if st.button(
        "➕ Nuevo Personal",
        type="primary",
        key="boton_nuevo_personal"
    ):

        @st.dialog("➕ Nuevo Personal")
        def formulario_nuevo_personal():

            st.write(
                "Ingrese la información del nuevo integrante "
                "del personal."
            )

            # ==================================================
            # CARGAR LISTAS MAESTRAS
            # ==================================================

            df_listas_formulario = cargar_listas_personal()

            if df_listas_formulario is None:

                df_listas_formulario = pd.DataFrame(
                    columns=[
                        "Cargo Principal",
                        "Especialidad",
                        "Nivel",
                        "Productividad",
                        "Experiencia"
                    ]
                )

            # ==================================================
            # DATOS BÁSICOS
            # ==================================================

            codigo = st.text_input(
                "Código *",
                placeholder="Ejemplo: P024"
            )

            nombre = st.text_input(
                "Nombre Completo *"
            )

            tipo_personal = st.selectbox(
                "Tipo Personal *",
                [
                    "Empleado",
                    "Contratista"
                ]
            )

            estado_disponibilidad = st.selectbox(
                "Estado Disponibilidad *",
                [
                    "Disponible",
                    "No Disponible"
                ],
                key="nuevo_estado_disponibilidad"
            )            

            # ==================================================
            # CARGO PRINCIPAL
            # ==================================================

            if "Cargo Principal" in df_listas_formulario.columns:

                opciones_cargo = (
                    df_listas_formulario["Cargo Principal"]
                    .dropna()
                    .astype(str)
                    .str.strip()
                )

                opciones_cargo = [
                    valor
                    for valor in opciones_cargo
                    if valor
                ]

                opciones_cargo = list(
                    dict.fromkeys(opciones_cargo)
                )

            else:

                opciones_cargo = ["Ninguno"]


            cargo_principal = st.selectbox(
                "Cargo Principal",
                opciones_cargo,
                key="nuevo_personal_cargo"
            )

            # ==================================================
            # PERFIL
            # ==================================================

            # ==================================================
            # ESPECIALIDAD
            # ==================================================

            opciones_especialidad = (
                df_listas_formulario["Especialidad"]
                .dropna()
                .astype(str)
                .str.strip()
            )

            opciones_especialidad = [
                valor
                for valor in opciones_especialidad
                if valor
            ]

            opciones_especialidad = list(
                dict.fromkeys(opciones_especialidad)
            )


            especialidad = st.selectbox(
                "Especialidad",
                opciones_especialidad,
                key="nuevo_personal_especialidad"
            )


            # ==================================================
            # NIVEL
            # ==================================================

            opciones_nivel = (
                df_listas_formulario["Nivel"]
                .dropna()
                .astype(str)
                .str.strip()
            )

            opciones_nivel = [
                valor
                for valor in opciones_nivel
                if valor
            ]

            opciones_nivel = list(
                dict.fromkeys(opciones_nivel)
            )


            nivel = st.selectbox(
                "Nivel",
                opciones_nivel,
                key="nuevo_personal_nivel"
            )


            # ==================================================
            # PRODUCTIVIDAD
            # ==================================================

            opciones_productividad = (
                df_listas_formulario["Productividad"]
                .dropna()
                .astype(str)
                .str.strip()
            )

            opciones_productividad = [
                valor
                for valor in opciones_productividad
                if valor
            ]

            opciones_productividad = list(
                dict.fromkeys(opciones_productividad)
            )


            productividad = st.selectbox(
                "Productividad",
                opciones_productividad,
                key="nuevo_personal_productividad"
            )


            # ==================================================
            # EXPERIENCIA
            # ==================================================

            opciones_experiencia = (
                df_listas_formulario["Experiencia"]
                .dropna()
                .astype(str)
                .str.strip()
            )

            opciones_experiencia = [
                valor
                for valor in opciones_experiencia
                if valor
            ]

            opciones_experiencia = list(
                dict.fromkeys(opciones_experiencia)
            )


            experiencia = st.selectbox(
                "Experiencia",
                opciones_experiencia,
                key="nuevo_personal_experiencia"
            )

            # ==================================================
            # CONDICIONES DE TRABAJO
            # ==================================================

            turno = st.selectbox(
                "Turno *",
                [
                    "Diurno",
                    "Nocturno"
                ]
            )

            puede_viajar = st.selectbox(
                "Puede Viajar *",
                [
                    "Si",
                    "No"
                ]
            )

            licencia_conduccion = st.selectbox(
                "Licencia Conducción *",
                [
                    "Si",
                    "No"
                ]
            )

            categoria_licencia = st.selectbox(
                "Categoría Licencia",
                [
                    "Ninguna",
                    "A1",
                    "A2",
                    "B1",
                    "B2",
                    "B3",
                    "C1",
                    "C2"
                ]
            )

            # ==================================================
            # CERTIFICACIONES
            # ==================================================

            curso_alturas = st.selectbox(
                "Curso Alturas Avanzado *",
                [
                    "Si",
                    "No"
                ]
            )

            coordinador_alturas = st.selectbox(
                "Coordinador de alturas *",
                [
                    "Si",
                    "No"
                ]
            )

            espacios_confinados = st.selectbox(
                "Espacios Confinados *",
                [
                    "Si",
                    "No"
                ]
            )

            restriccion_medica = st.selectbox(
                "Restricción Médica *",
                [
                    "Si",
                    "No"
                ]
            )

            observaciones = st.text_area(
                "Observaciones"
            )

            st.divider()

            # ==================================================
            # GUARDAR
            # ==================================================

            if st.button(
                "💾 Guardar Personal",
                type="primary",
                key="guardar_nuevo_personal"
            ):

                # ----------------------------------------------
                # LIMPIAR DATOS
                # ----------------------------------------------

                codigo_limpio = (
                    codigo
                    .strip()
                    .upper()
                )

                nombre_limpio = (
                    nombre
                    .strip()
                )

                cargo_limpio = (
                    cargo_principal
                    .strip()
                    if cargo_principal.strip()
                    else "Ninguno"
                )

                especialidad_limpia = (
                    especialidad
                    .strip()
                    if especialidad.strip()
                    else "Ninguno"
                )

                nivel_limpio = (
                    nivel
                    .strip()
                    if nivel.strip()
                    else "Ninguno"
                )

                productividad_limpia = (
                    productividad
                    .strip()
                    if productividad.strip()
                    else "Ninguno"
                )

                experiencia_limpia = (
                    experiencia
                    .strip()
                    if experiencia.strip()
                    else "Ninguno"
                )

                observaciones_limpias = (
                    observaciones
                    .strip()
                )

                # ----------------------------------------------
                # VALIDAR CÓDIGO
                # ----------------------------------------------

                if not codigo_limpio:

                    st.error(
                        "❌ El Código es obligatorio."
                    )

                    return

                # ----------------------------------------------
                # VALIDAR NOMBRE
                # ----------------------------------------------

                if not nombre_limpio:

                    st.error(
                        "❌ El Nombre Completo es obligatorio."
                    )

                    return

                # ----------------------------------------------
                # CARGAR PERSONAL ACTUAL
                # ----------------------------------------------

                df_actual = cargar_personal()

                if df_actual is None:

                    df_actual = pd.DataFrame(
                        columns=COLUMNAS_PERSONAL
                    )

                # ----------------------------------------------
                # VALIDAR CÓDIGO DUPLICADO
                # ----------------------------------------------

                if not df_actual.empty:

                    codigos_existentes = (
                        df_actual["Código"]
                        .astype(str)
                        .str.strip()
                        .str.upper()
                        .tolist()
                    )

                    if codigo_limpio in codigos_existentes:

                        st.error(
                            f"❌ El código "
                            f"**{codigo_limpio}** "
                            f"ya existe en el Personal."
                        )

                        return

                # ----------------------------------------------
                # CREAR NUEVO REGISTRO
                # ----------------------------------------------

                nuevo_personal = {

                    "Código":
                        codigo_limpio,

                    "Nombre Completo":
                        nombre_limpio,

                    "Tipo Personal":
                        tipo_personal,

                    "Estado Disponibilidad":
                        estado_disponibilidad,

                    "Cargo Principal":
                        cargo_limpio,

                    "Especialidad":
                        especialidad_limpia,

                    "Nivel":
                        nivel_limpio,

                    "Productividad":
                        productividad_limpia,

                    "Experiencia":
                        experiencia_limpia,

                    "Turno":
                        turno,

                    "Puede Viajar":
                        puede_viajar,

                    "Licencia Conducción":
                        licencia_conduccion,

                    "Categoría Licencia":
                        categoria_licencia,

                    "Curso Alturas Avanzado":
                        curso_alturas,

                    "Coordinador de alturas":
                        coordinador_alturas,

                    "Espacios Confinados":
                        espacios_confinados,

                    "Restricción Médica":
                        restriccion_medica,

                    "Observaciones":
                        observaciones_limpias
                }

                # ----------------------------------------------
                # AGREGAR REGISTRO
                # ----------------------------------------------

                df_nuevo = pd.DataFrame(
                    [nuevo_personal],
                    columns=COLUMNAS_PERSONAL
                )

                df_actualizado = pd.concat(
                    [
                        df_actual,
                        df_nuevo
                    ],
                    ignore_index=True
                )

                # ----------------------------------------------
                # GUARDAR
                # ----------------------------------------------

                guardar_personal(
                    df_actualizado
                )

                st.success(
                    f"🟢 Personal **{nombre_limpio}** "
                    f"agregado correctamente."
                )

                st.rerun()

        formulario_nuevo_personal()

    # ======================================================
    # MODIFICAR PERSONAL
    # ======================================================

    st.subheader(
        "✏️ Modificar Personal"
    )

    df_personal_modificar = cargar_personal()

    if (
        df_personal_modificar is not None
        and not df_personal_modificar.empty
    ):

        opciones_personal = (
            df_personal_modificar[
                ["Código", "Nombre Completo"]
            ]
            .fillna("")
            .astype(str)
            .apply(
                lambda fila:
                    f"{fila['Código']} - "
                    f"{fila['Nombre Completo']}",
                axis=1
            )
            .tolist()
        )

        persona_seleccionada = st.selectbox(
            "Seleccione la persona que desea modificar",
            opciones_personal,
            key="seleccionar_personal_modificar"
        )

        codigo_seleccionado = (
            persona_seleccionada
            .split(" - ", 1)[0]
            .strip()
        )

        persona = df_personal_modificar[
            df_personal_modificar["Código"].astype(str).str.strip()
            == codigo_seleccionado
        ]

        if not persona.empty:

            registro = persona.iloc[0]

            # ----------------------------------------------
            # CARGAR LISTAS
            # ----------------------------------------------

            df_listas_modificar = cargar_listas_personal()

            if df_listas_modificar is None:

                df_listas_modificar = pd.DataFrame(
                    columns=[
                        "Cargo Principal",
                        "Especialidad",
                        "Nivel",
                        "Productividad",
                        "Experiencia"
                    ]
                )

            # ----------------------------------------------
            # FUNCIÓN PARA OPCIONES
            # ----------------------------------------------

            def opciones_lista(
                df_listas,
                columna
            ):

                if columna not in df_listas.columns:

                    return ["Ninguno"]

                opciones = (
                    df_listas[columna]
                    .fillna("Ninguno")
                    .astype(str)
                    .str.strip()
                )

                opciones = [
                    valor
                    for valor in opciones
                    if valor
                ]

                opciones = list(
                    dict.fromkeys(opciones)
                )

                if not opciones:

                    opciones = ["Ninguno"]

                return opciones

            # ----------------------------------------------
            # FORMULARIO
            # ----------------------------------------------

            @st.dialog("✏️ Modificar Personal")

            def formulario_modificar_personal():

                st.write(
                    f"Modificando: "
                    f"**{registro['Nombre Completo']}**"
                )

                # ==================================================
                # DATOS BÁSICOS
                # ==================================================

                codigo = st.text_input(
                    "Código *",
                    value=str(
                        registro["Código"]
                    ),
                    disabled=True,
                    key="modificar_codigo"
                )

                nombre = st.text_input(
                    "Nombre Completo *",
                    value=str(
                        registro["Nombre Completo"]
                    ),
                    key="modificar_nombre"
                )

                tipo_personal = st.selectbox(
                    "Tipo Personal *",
                    [
                        "Empleado",
                        "Contratista"
                    ],
                    index=(
                        0
                        if str(
                            registro["Tipo Personal"]
                        ) == "Empleado"
                        else 1
                    ),
                    key="modificar_tipo_personal"
                )


                # ==================================================
                # CARGAR OPCIONES DESDE HOJA LISTAS
                # ==================================================

                opciones_cargo = opciones_lista(
                    df_listas_modificar,
                    "Cargo Principal"
                )

                opciones_especialidad = opciones_lista(
                    df_listas_modificar,
                    "Especialidad"
                )

                opciones_nivel = opciones_lista(
                    df_listas_modificar,
                    "Nivel"
                )

                opciones_productividad = opciones_lista(
                    df_listas_modificar,
                    "Productividad"
                )

                opciones_experiencia = opciones_lista(
                    df_listas_modificar,
                    "Experiencia"
                )


                # ==================================================
                # FUNCIÓN PARA ENCONTRAR ÍNDICE
                # ==================================================

                def indice_opcion(
                    opciones,
                    valor
                ):

                    valor = str(
                        valor
                    ).strip()

                    if valor in opciones:

                        return opciones.index(
                            valor
                        )

                    return 0


                # ==================================================
                # PERFIL PROFESIONAL
                # ==================================================

                cargo_principal = st.selectbox(
                    "Cargo Principal",
                    opciones_cargo,
                    index=indice_opcion(
                        opciones_cargo,
                        registro["Cargo Principal"]
                    ),
                    key="modificar_cargo"
                )

                especialidad = st.selectbox(
                    "Especialidad",
                    opciones_especialidad,
                    index=indice_opcion(
                        opciones_especialidad,
                        registro["Especialidad"]
                    ),
                    key="modificar_especialidad"
                )

                nivel = st.selectbox(
                    "Nivel",
                    opciones_nivel,
                    index=indice_opcion(
                        opciones_nivel,
                        registro["Nivel"]
                    ),
                    key="modificar_nivel"
                )

                productividad = st.selectbox(
                    "Productividad",
                    opciones_productividad,
                    index=indice_opcion(
                        opciones_productividad,
                        registro["Productividad"]
                    ),
                    key="modificar_productividad"
                )

                experiencia = st.selectbox(
                    "Experiencia",
                    opciones_experiencia,
                    index=indice_opcion(
                        opciones_experiencia,
                        registro["Experiencia"]
                    ),
                    key="modificar_experiencia"
                )

                # ==================================================
                # DISPONIBILIDAD BASE
                # ==================================================

                estado_disponibilidad = st.selectbox(
                    "Estado Disponibilidad *",
                    [
                        "Disponible",
                        "No Disponible"
                    ],
                    index=(
                        0
                        if str(
                            registro["Estado Disponibilidad"]
                        ).strip() == "Disponible"
                        else 1
                    ),
                    key="modificar_estado_disponibilidad"
                )


                # ==================================================
                # TURNO BASE
                # ==================================================

                turno = st.selectbox(
                    "Turno *",
                    [
                        "Diurno",
                        "Nocturno"
                    ],
                    index=(
                        0
                        if str(
                            registro["Turno"]
                        ).strip() == "Diurno"
                        else 1
                    ),
                    key="modificar_turno"
                )


                # ==================================================
                # PUEDE VIAJAR
                # ==================================================

                puede_viajar = st.selectbox(
                    "Puede Viajar *",
                    [
                        "Si",
                        "No"
                    ],
                    index=(
                        0
                        if str(
                            registro["Puede Viajar"]
                        ).strip() == "Si"
                        else 1
                    ),
                    key="modificar_puede_viajar"
                )


                # ==================================================
                # LICENCIA DE CONDUCCIÓN
                # ==================================================

                licencia_conduccion = st.selectbox(
                    "Licencia Conducción *",
                    [
                        "Si",
                        "No"
                    ],
                    index=(
                        0
                        if str(
                            registro["Licencia Conducción"]
                        ).strip() == "Si"
                        else 1
                    ),
                    key="modificar_licencia"
                )


                # ==================================================
                # CATEGORÍA LICENCIA
                # ==================================================

                categorias_licencia = [
                    "Ninguna",
                    "A1",
                    "A2",
                    "B1",
                    "B2",
                    "B3",
                    "C1",
                    "C2"
                ]

                categoria_actual = str(
                    registro["Categoría Licencia"]
                ).strip()

                if categoria_actual not in categorias_licencia:

                    categoria_actual = "Ninguna"

                categoria_licencia = st.selectbox(
                    "Categoría Licencia",
                    categorias_licencia,
                    index=categorias_licencia.index(
                        categoria_actual
                    ),
                    key="modificar_categoria_licencia"
                )


                # ==================================================
                # CURSO ALTURAS AVANZADO
                # ==================================================

                curso_alturas = st.selectbox(
                    "Curso Alturas Avanzado *",
                    [
                        "Si",
                        "No"
                    ],
                    index=(
                        0
                        if str(
                            registro["Curso Alturas Avanzado"]
                        ).strip() == "Si"
                        else 1
                    ),
                    key="modificar_curso_alturas"
                )


                # ==================================================
                # COORDINADOR DE ALTURAS
                # ==================================================

                coordinador_alturas = st.selectbox(
                    "Coordinador de alturas *",
                    [
                        "Si",
                        "No"
                    ],
                    index=(
                        0
                        if str(
                            registro["Coordinador de alturas"]
                        ).strip() == "Si"
                        else 1
                    ),
                    key="modificar_coordinador_alturas"
                )


                # ==================================================
                # ESPACIOS CONFINADOS
                # ==================================================

                espacios_confinados = st.selectbox(
                    "Espacios Confinados *",
                    [
                        "Si",
                        "No"
                    ],
                    index=(
                        0
                        if str(
                            registro["Espacios Confinados"]
                        ).strip() == "Si"
                        else 1
                    ),
                    key="modificar_espacios_confinados"
                )


                # ==================================================
                # RESTRICCIÓN MÉDICA
                # ==================================================

                restriccion_medica = st.selectbox(
                    "Restricción Médica *",
                    [
                        "Si",
                        "No"
                    ],
                    index=(
                        0
                        if str(
                            registro["Restricción Médica"]
                        ).strip() == "Si"
                        else 1
                    ),
                    key="modificar_restriccion_medica"
                )


                # ==================================================
                # OBSERVACIONES
                # ==================================================

                observacion_actual = registro.get(
                    "Observaciones",
                    ""
                )

                if pd.isna(
                    observacion_actual
                ):

                    observacion_actual = ""

                observaciones = st.text_area(
                    "Observaciones",
                    value=str(
                        observacion_actual
                    ),
                    key="modificar_observaciones"
                )

                # ==================================================
                # GUARDAR CAMBIOS
                # ==================================================

                st.divider()

                if st.button(
                    "💾 Guardar cambios",
                    type="primary",
                    key="guardar_cambios_personal"
                ):

                    # ----------------------------------------------
                    # LIMPIAR DATOS
                    # ----------------------------------------------

                    nombre_limpio = (
                        nombre
                        .strip()
                    )

                    # ----------------------------------------------
                    # VALIDAR NOMBRE
                    # ----------------------------------------------

                    if not nombre_limpio:

                        st.error(
                            "❌ El Nombre Completo es obligatorio."
                        )

                    else:

                        # ------------------------------------------
                        # BUSCAR REGISTRO POR CÓDIGO
                        # ------------------------------------------

                        indice = df_personal_modificar[
                            df_personal_modificar["Código"]
                            .astype(str)
                            .str.strip()
                            .str.upper()
                            == codigo.strip().upper()
                        ].index

                        if len(indice) == 0:

                            st.error(
                                "❌ No se encontró el personal "
                                "seleccionado."
                            )

                        else:

                            indice = indice[0]

                            # --------------------------------------
                            # ACTUALIZAR DATOS
                            # --------------------------------------

                            df_personal_modificar.loc[
                                indice,
                                "Nombre Completo"
                            ] = nombre_limpio

                            df_personal_modificar.loc[
                                indice,
                                "Tipo Personal"
                            ] = tipo_personal

                            df_personal_modificar.loc[
                                indice,
                                "Cargo Principal"
                            ] = cargo_principal

                            df_personal_modificar.loc[
                                indice,
                                "Especialidad"
                            ] = especialidad

                            df_personal_modificar.loc[
                                indice,
                                "Nivel"
                            ] = nivel

                            df_personal_modificar.loc[
                                indice,
                                "Productividad"
                            ] = productividad

                            df_personal_modificar.loc[
                                indice,
                                "Experiencia"
                            ] = experiencia

                            df_personal_modificar.loc[
                                indice,
                                "Estado Disponibilidad"
                            ] = estado_disponibilidad


                            df_personal_modificar.loc[
                                indice,
                                "Turno"
                            ] = turno


                            df_personal_modificar.loc[
                                indice,
                                "Puede Viajar"
                            ] = puede_viajar


                            df_personal_modificar.loc[
                                indice,
                                "Licencia Conducción"
                            ] = licencia_conduccion


                            df_personal_modificar.loc[
                                indice,
                                "Categoría Licencia"
                            ] = categoria_licencia


                            df_personal_modificar.loc[
                                indice,
                                "Curso Alturas Avanzado"
                            ] = curso_alturas


                            df_personal_modificar.loc[
                                indice,
                                "Coordinador de alturas"
                            ] = coordinador_alturas


                            df_personal_modificar.loc[
                                indice,
                                "Espacios Confinados"
                            ] = espacios_confinados


                            df_personal_modificar.loc[
                                indice,
                                "Restricción Médica"
                            ] = restriccion_medica


                            df_personal_modificar.loc[
                                indice,
                                "Observaciones"
                            ] = (
                                observaciones.strip()
                                if observaciones.strip()
                                else "Ninguno"
                            )

                            # --------------------------------------
                            # ASEGURAR CAMPOS VACÍOS
                            # --------------------------------------

                            CAMPOS_NINGUNO_MODIFICAR = [
                                "Cargo Principal",
                                "Especialidad",
                                "Nivel",
                                "Productividad",
                                "Experiencia"
                            ]

                            for campo in CAMPOS_NINGUNO_MODIFICAR:

                                valor = (
                                    str(
                                        df_personal_modificar.loc[
                                            indice,
                                            campo
                                        ]
                                    )
                                    .strip()
                                )

                                if not valor or valor.lower() == "nan":

                                    df_personal_modificar.loc[
                                        indice,
                                        campo
                                    ] = "Ninguno"

                            # --------------------------------------
                            # GUARDAR EN PKL
                            # --------------------------------------

                            guardar_personal(
                                df_personal_modificar
                            )

                            st.success(
                                f"🟢 Datos de "
                                f"**{nombre_limpio}** "
                                f"actualizados correctamente."
                            )

                            st.rerun()

                

            # ----------------------------------------------
            # BOTÓN
            # ----------------------------------------------

            if st.button(
                "✏️ Modificar persona seleccionada",
                key="boton_modificar_personal",
            ):

                formulario_modificar_personal()

    else:

        st.info(
            "No hay personal registrado para modificar."
        )

    # ======================================================
    # MOSTRAR PERSONAL ACTUAL
    # ======================================================

    df_personal = cargar_personal()

    if df_personal is not None:

        st.subheader(
            "👥 Personal registrado"
        )

        st.write(
            f"Total de personas: "
            f"**{len(df_personal)}**"
        )

        st.dataframe(
            df_personal,
            width="stretch",
            hide_index=True
        )

        # ======================================================
        # ELIMINAR UNA PERSONA
        # ======================================================

        st.divider()

        st.subheader(
            "🗑️ Eliminar una persona"
        )

        st.caption(
            "Seleccione una persona para eliminarla del maestro "
            "de Personal y de su disponibilidad diaria."
        )

        if not df_personal.empty:

            opciones_personal = (
                df_personal["Código"].astype(str)
                + " | "
                + df_personal["Nombre Completo"].astype(str)
            ).tolist()

            persona_seleccionada = st.selectbox(
                "Seleccione la persona",
                opciones_personal,
                key="persona_seleccionada_eliminar"
            )

            st.warning(
                "⚠️ La eliminación será permanente y también "
                "eliminará la disponibilidad asociada."
            )

            if st.button(
                "🗑️ Eliminar persona seleccionada",
                type="secondary",
                key="boton_eliminar_persona"
            ):

                codigo_seleccionado = (
                    persona_seleccionada
                    .split(" | ")[0]
                    .strip()
                )

                st.session_state[
                    "mostrar_confirmacion_eliminar_persona"
                ] = True

                st.session_state[
                    "codigo_persona_eliminar"
                ] = codigo_seleccionado


        # ======================================================
        # CONFIRMACIÓN DE ELIMINACIÓN INDIVIDUAL
        # ======================================================

        if st.session_state.get(
            "mostrar_confirmacion_eliminar_persona",
            False
        ):

            codigo_confirmacion = st.session_state.get(
                "codigo_persona_eliminar",
                ""
            )

            st.error(
                f"⚠️ Está a punto de eliminar la persona "
                f"con código **{codigo_confirmacion}**."
            )

            confirmar_persona = st.checkbox(
                "Sí, quiero eliminar definitivamente esta persona.",
                key="check_confirmar_eliminar_persona"
            )

            col_confirmar, col_cancelar = st.columns(2)

            with col_confirmar:

                if st.button(
                    "🗑️ CONFIRMAR ELIMINACIÓN",
                    type="primary",
                    key="confirmar_eliminar_persona"
                ):

                    if not confirmar_persona:

                        st.error(
                            "Debe marcar la casilla de confirmación "
                            "antes de eliminar."
                        )

                    else:

                        resultado, mensaje = eliminar_persona(
                            codigo_confirmacion
                        )

                        if resultado:

                            st.success(
                                f"✅ {mensaje}"
                            )

                            st.session_state[
                                "mostrar_confirmacion_eliminar_persona"
                            ] = False

                            st.session_state.pop(
                                "codigo_persona_eliminar",
                                None
                            )

                            st.session_state.pop(
                                "check_confirmar_eliminar_persona",
                                None
                            )

                            st.rerun()

                        else:

                            st.error(mensaje)

            with col_cancelar:

                if st.button(
                    "↩️ Cancelar",
                    key="cancelar_eliminar_persona"
                ):

                    st.session_state[
                        "mostrar_confirmacion_eliminar_persona"
                    ] = False

                    st.session_state.pop(
                        "codigo_persona_eliminar",
                        None
                    )

                    st.session_state.pop(
                        "check_confirmar_eliminar_persona",
                        None
                    )

                    st.rerun()

        # ==================================================
        # DESCARGAR PERSONAL ACTUALIZADO
        # ==================================================

        # AQUÍ DEBE ESTAR EL CÓDIGO QUE YA TIENES
        # PARA DESCARGAR EL ARCHIVO EXCEL


        # ==================================================
        # DISPONIBILIDAD DEL DÍA
        # ==================================================

        st.divider()

        st.subheader(
            "📅 Disponibilidad del día"
        )

        st.caption(
            "Antes de formar los equipos, revise y ajuste "
            "la disponibilidad y el turno del personal."
        )

        # ==================================================
        # FECHA DE PROGRAMACIÓN
        # ==================================================

        fecha_disponibilidad = st.date_input(
            "Fecha de programación",
            value=pd.Timestamp.now().date(),
            key="fecha_disponibilidad_personal"
        )

        fecha_disponibilidad = pd.Timestamp(
            fecha_disponibilidad
        ).normalize()


        # ==================================================
        # CARGAR DISPONIBILIDAD EXISTENTE
        # ==================================================

        df_disponibilidad = cargar_disponibilidad()


        if df_disponibilidad is None:

            df_disponibilidad = pd.DataFrame(
                columns=COLUMNAS_DISPONIBILIDAD
            )


        # ==================================================
        # NORMALIZAR FECHAS
        # ==================================================

        if not df_disponibilidad.empty:

            df_disponibilidad["Fecha"] = pd.to_datetime(
                df_disponibilidad["Fecha"],
                errors="coerce"
            ).dt.normalize()


        # ==================================================
        # BUSCAR LA FECHA SELECCIONADA
        # ==================================================

        if not df_disponibilidad.empty:

            df_dia = df_disponibilidad[
                df_disponibilidad["Fecha"] == fecha_disponibilidad
            ].copy()

        else:

            df_dia = pd.DataFrame()


        # ==================================================
        # SI NO EXISTE LA FECHA, CREARLA DESDE PERSONAL
        # ==================================================

        if df_dia.empty:

            if df_personal is not None and not df_personal.empty:

                df_dia = crear_disponibilidad_del_dia(
                    df_personal,
                    fecha_disponibilidad
                )

                st.info(
                    "ℹ️ Se cargó la información base del maestro "
                    "de Personal para esta fecha."
                )

            else:

                df_dia = pd.DataFrame(
                    columns=COLUMNAS_DISPONIBILIDAD
                )

                st.info(
                    "📭 No existe Personal registrado. "
                    "La disponibilidad del día está vacía."
                )


        # ==================================================
        # EDITAR DISPONIBILIDAD Y TURNO
        # ==================================================

        columnas_editor = [
            "Código",
            "Nombre Completo",
            "Cargo Principal",
            "Estado Disponibilidad",
            "Turno"
        ]


        df_dia_editado = st.data_editor(

            df_dia[columnas_editor].copy(),

            width="stretch",

            hide_index=True,

            disabled=[
                "Código",
                "Nombre Completo",
                "Cargo Principal"
            ],

            column_config={

                "Estado Disponibilidad":
                    st.column_config.SelectboxColumn(
                        "Estado Disponibilidad",
                        options=[
                            "Disponible",
                            "No Disponible"
                        ],
                        required=True
                    ),

                "Turno":
                    st.column_config.SelectboxColumn(
                        "Turno",
                        options=[
                            "Diurno",
                            "Nocturno"
                        ],
                        required=True
                    )
            },

            key=(
                "editor_disponibilidad_"
                f"{fecha_disponibilidad.strftime('%Y%m%d')}"
            )
        )


        # ==================================================
        # GUARDAR DISPONIBILIDAD
        # ==================================================

        if st.button(
            "💾 Guardar disponibilidad del día",
            type="primary",
            key="guardar_disponibilidad_dia"
        ):

            df_dia_guardar = df_dia.copy()

            df_dia_guardar[
                "Estado Disponibilidad"
            ] = (
                df_dia_editado[
                    "Estado Disponibilidad"
                ]
                .fillna("No Disponible")
                .astype(str)
                .str.strip()
            )

            df_dia_guardar[
                "Turno"
            ] = (
                df_dia_editado[
                    "Turno"
                ]
                .fillna("Diurno")
                .astype(str)
                .str.strip()
            )

            df_dia_guardar[
                "Fecha"
            ] = fecha_disponibilidad

            df_dia_guardar[
                "Última Actualización"
            ] = pd.Timestamp.now()


            # ----------------------------------------------
            # ELIMINAR INFORMACIÓN ANTERIOR DE ESA FECHA
            # ----------------------------------------------

            if not df_disponibilidad.empty:

                df_disponibilidad = df_disponibilidad[
                    df_disponibilidad["Fecha"]
                    != fecha_disponibilidad
                ].copy()


            # ----------------------------------------------
            # AGREGAR INFORMACIÓN ACTUALIZADA
            # ----------------------------------------------

            df_disponibilidad = pd.concat(
                [
                    df_disponibilidad,
                    df_dia_guardar[
                        COLUMNAS_DISPONIBILIDAD
                    ]
                ],
                ignore_index=True
            )


            # ----------------------------------------------
            # GUARDAR
            # ----------------------------------------------

            guardar_disponibilidad(
                df_disponibilidad
            )


            st.success(
                "🟢 Disponibilidad del día guardada correctamente."
            )

            st.rerun()


        # ==================================================
        # DESCARGAR PERSONAL ACTUALIZADO
        # ==================================================

        st.subheader(
            "📤 Descargar Personal actualizado"
        )

        st.write(
            "Descargue la tabla de Personal con los datos "
            "actualmente almacenados en el sistema."
        )

        # --------------------------------------------------
        # CREAR ARCHIVO EXCEL EN MEMORIA
        # --------------------------------------------------

        import io

        archivo_descarga = io.BytesIO()

        with pd.ExcelWriter(
            archivo_descarga,
            engine="openpyxl"
        ) as writer:

            df_personal.to_excel(
                writer,
                sheet_name="Personal",
                index=False
            )

        archivo_descarga.seek(0)

        # --------------------------------------------------
        # BOTÓN DE DESCARGA
        # --------------------------------------------------

        st.download_button(
            label="📤 Descargar Personal actualizado",
            data=archivo_descarga,
            file_name="Tabla Empleados_Actualizada.xlsx",
            mime=(
                "application/vnd.openxmlformats-officedocument."
                "spreadsheetml.sheet"
            ),
            key="descargar_personal_actualizado"
        )

    else:

        st.info(
            "No hay personal registrado todavía."
        )


# ==========================================================
# COMPETENCIAS
# ==========================================================

elif pagina == "🧠 Competencias":

    st.header(
        "🧠 Competencias"
    )

    st.info(
        "Módulo pendiente de construcción."
    )


# ==========================================================
# ACTIVIDADES
# ==========================================================

elif pagina == "🔧 Actividades":

    st.header(
        "🔧 Actividades"
    )

    st.info(
        "Las actividades se gestionan desde Gestión ID. "
        "Este módulo será el detalle y consulta de las actividades por ID."
    )


# ==========================================================
# CATÁLOGO DE ACTIVIDADES
# ==========================================================

elif pagina == "📚 Maestro de Actividades":

    st.header(
        "📚 Maestro de Actividades"
    )

    st.caption(
        "Maestro de atributos de cada actividad. La IA puede proponer actividades "
        "fuera del catálogo; el catálogo sirve para enriquecerlas y estandarizarlas."
    )

    df_catalogo = cargar_catalogo()
    st.dataframe(df_catalogo, width="stretch", hide_index=True)


    # ======================================================
    # CARGAR GESTIÓN ID
    # ======================================================

    df_gestion = cargar_gestion()


    if df_gestion is None:

        st.warning(
            "No existe información en Gestión ID."
        )

        st.stop()


    # ======================================================
    # BUSCADOR DE ID
    # ======================================================

    st.subheader(
        "🔎 Consultar ID"
    )


    col_busqueda, col_boton = st.columns(
        [4, 1]
    )


    with col_busqueda:

        id_buscado = st.text_input(
            "Ingrese el ID que desea consultar",
            placeholder="Ejemplo: 8627",
            key="buscador_id_programacion"
        )


    with col_boton:

        st.write("")

        consultar_id = st.button(
            "🔎 Consultar ID",
            type="primary",
            key="consultar_id_programacion"
        )


    # ======================================================
    # CONSULTAR ID
    # ======================================================

    if consultar_id:

        id_consulta = (
            str(id_buscado)
            .strip()
        )


        if not id_consulta:

            st.warning(
                "Ingrese un ID para realizar la consulta."
            )

            st.session_state[
                "id_programacion_consultado"
            ] = None


        else:

            ids_gestion = (
                df_gestion["ID"]
                .astype(str)
                .str.strip()
            )


            # --------------------------------------------------
            # BUSCAR ID OPERATIVO
            # --------------------------------------------------

            resultado_id = df_gestion[
                ids_gestion.str.contains(
                    f"_{id_consulta}_",
                    regex=False,
                    na=False
                )
            ]


            # --------------------------------------------------
            # ID NO ENCONTRADO
            # --------------------------------------------------

            if resultado_id.empty:

                st.session_state[
                    "id_programacion_consultado"
                ] = None

                st.error(
                    f"No se encontró el ID **{id_consulta}** "
                    "en Gestión ID."
                )


            # --------------------------------------------------
            # ID ENCONTRADO
            # --------------------------------------------------

            else:

                st.session_state[
                    "id_programacion_consultado"
                ] = id_consulta

                st.success(
                    f"ID **{id_consulta}** encontrado."
                )

                st.rerun()


    # ======================================================
    # RECUPERAR ID CONSULTADO
    # ======================================================

    id_consultado = st.session_state.get(
        "id_programacion_consultado",
        None
    )


    # ======================================================
    # MOSTRAR FICHA DEL ID CONSULTADO
    # ======================================================

    if id_consultado:

        # --------------------------------------------------
        # RECARGAR GESTIÓN ID
        # --------------------------------------------------

        df_gestion = cargar_gestion()


        ids_gestion = (
            df_gestion["ID"]
            .astype(str)
            .str.strip()
        )


        resultado_id = df_gestion[
            ids_gestion.str.contains(
                f"_{id_consultado}_",
                regex=False,
                na=False
            )
        ]


        # --------------------------------------------------
        # VALIDAR QUE SIGA EXISTIENDO
        # --------------------------------------------------

        if resultado_id.empty:

            st.error(
                f"El ID **{id_consultado}** "
                "ya no existe en Gestión ID."
            )

            st.session_state[
                "id_programacion_consultado"
            ] = None

            st.stop()


        # --------------------------------------------------
        # OBTENER REGISTRO
        # --------------------------------------------------

        indice_id = resultado_id.index[0]

        registro = df_gestion.loc[
            indice_id
        ]


        # ==================================================
        # FICHA DEL ID
        # ==================================================

        st.divider()

        st.subheader(
            f"📋 Información del ID {id_consultado}"
        )


        col1, col2 = st.columns(2)


        # ==================================================
        # INFORMACIÓN GENERAL
        # ==================================================

        with col1:

            st.write(
                f"**ID:** "
                f"{id_consultado}"
            )

            st.write(
                f"**Cliente:** "
                f"{registro.get('Cliente', '')}"
            )

            st.write(
                f"**Referencia del pedido:** "
                f"{registro.get('Referencia del pedido', '')}"
            )

            st.write(
                f"**Descripción:** "
                f"{registro.get('Descripción', '')}"
            )

            st.write(
                f"**Cantidad total:** "
                f"{registro.get('Cantidad', '')}"
            )


        # ==================================================
        # INFORMACIÓN DE PLAZO
        # ==================================================

        with col2:

            st.write(
                f"**Fecha Entrega Producción:** "
                f"{registro.get('Fecha Entrega Producción', '')}"
            )

            st.write(
                f"**Situación de Plazo:** "
                f"{registro.get('Situación de Plazo', '')}"
            )

            st.write(
                f"**Días Restantes:** "
                f"{registro.get('Días Restantes', '')}"
            )

            st.write(
                f"**Prioridad:** "
                f"{registro.get('Prioridad', '')}"
            )

            st.write(
                f"**Estado Registro:** "
                f"{registro.get('Estado Registro', '')}"
            )


        # ==================================================
        # ESTADO DE PROGRAMACIÓN
        # ==================================================

        st.divider()

        st.subheader(
            "📅 Estado de Programación"
        )


        col_prog1, col_prog2, col_prog3 = st.columns(3)


        with col_prog1:

            st.write(
                f"**Programar Hoy:** "
                f"{registro.get('Programar Hoy', 'NO')}"
            )


        with col_prog2:

            programado_para = registro.get(
                "Programado Para",
                ""
            )

            if pd.notna(programado_para):

                try:

                    programado_para = pd.to_datetime(
                        programado_para
                    ).strftime(
                        "%d/%m/%Y"
                    )

                except Exception:

                    pass

            else:

                programado_para = ""


            st.write(
                f"**Programado Para:** "
                f"{programado_para}"
            )


        with col_prog3:

            st.write(
                f"**Estado Programador:** "
                f"{registro.get('Estado Programador', '')}"
            )


        # ==================================================
        # INCORPORAR ID
        # ==================================================

        st.divider()

        st.subheader(
            "📋 Acción de Programación"
        )


        # --------------------------------------------------
        # DETERMINAR SI YA ESTÁ PROGRAMADO PARA HOY
        # --------------------------------------------------

        fecha_hoy = pd.Timestamp.now().normalize()


        fecha_actual_programada = pd.to_datetime(
            registro.get(
                "Programado Para",
                pd.NaT
            ),
            errors="coerce"
        )


        ya_programado_hoy = (
            pd.notna(fecha_actual_programada)
            and
            fecha_actual_programada.normalize()
            == fecha_hoy
        )


        # --------------------------------------------------
        # BOTÓN INCORPORAR
        # --------------------------------------------------

        if ya_programado_hoy:

            st.success(
                f"🟢 El ID **{id_consultado}** "
                "ya está incorporado a la programación de hoy."
            )


        else:

            incorporar_id = st.button(
                "📋 Incorporar ID a programación de hoy",
                type="primary",
                key=f"incorporar_id_{id_consultado}"
            )


            # ==================================================
            # PROCESAR INCORPORACIÓN
            # ==================================================

            if incorporar_id:

                # --------------------------------------------------
                # RECARGAR EL ARCHIVO ANTES DE MODIFICAR
                # --------------------------------------------------

                df_gestion = cargar_gestion()


                if df_gestion is None:

                    st.error(
                        "No se pudo cargar Gestión ID."
                    )

                    st.stop()


                # --------------------------------------------------
                # VOLVER A BUSCAR EL ID EN EL DATAFRAME ACTUAL
                # --------------------------------------------------

                ids_gestion = (
                    df_gestion["ID"]
                    .astype(str)
                    .str.strip()
                )


                resultado_id_actual = df_gestion[
                    ids_gestion.str.contains(
                        f"_{id_consultado}_",
                        regex=False,
                        na=False
                    )
                ]


                if resultado_id_actual.empty:

                    st.error(
                        f"No se encontró nuevamente "
                        f"el ID **{id_consultado}** "
                        "en Gestión ID."
                    )

                    st.stop()


                # --------------------------------------------------
                # ÍNDICE REAL DEL REGISTRO
                # --------------------------------------------------

                indice_id_actual = (
                    resultado_id_actual.index[0]
                )


                # --------------------------------------------------
                # FECHA DE HOY
                # --------------------------------------------------

                fecha_hoy = (
                    pd.Timestamp.now()
                    .normalize()
                )


                # --------------------------------------------------
                # MODIFICAR PROGRAMACIÓN
                # --------------------------------------------------

                df_gestion.loc[
                    indice_id_actual,
                    "Programar Hoy"
                ] = "SI"


                df_gestion.loc[
                    indice_id_actual,
                    "Programado Para"
                ] = fecha_hoy


                # --------------------------------------------------
                # ESTADO DEL PROGRAMADOR
                # --------------------------------------------------

                if (
                    pd.isna(
                        df_gestion.loc[
                            indice_id_actual,
                            "Estado Programador"
                        ]
                    )
                ):

                    df_gestion.loc[
                        indice_id_actual,
                        "Estado Programador"
                    ] = ""


                # --------------------------------------------------
                # ESTADO REGISTRO
                # --------------------------------------------------

                if (
                    str(
                        df_gestion.loc[
                            indice_id_actual,
                            "Estado Registro"
                        ]
                    ).strip()
                    in [
                        "Nuevo",
                        "Vigente"
                    ]
                ):

                    df_gestion.loc[
                        indice_id_actual,
                        "Estado Registro"
                    ] = "Programado"


                # --------------------------------------------------
                # GUARDAR
                # --------------------------------------------------

                guardar_gestion(
                    df_gestion
                )


                # --------------------------------------------------
                # VERIFICACIÓN REAL DESDE DISCO
                # --------------------------------------------------

                df_verificacion = cargar_gestion()


                ids_verificacion = (
                    df_verificacion["ID"]
                    .astype(str)
                    .str.strip()
                )


                resultado_verificacion = (
                    df_verificacion[
                        ids_verificacion.str.contains(
                            f"_{id_consultado}_",
                            regex=False,
                            na=False
                        )
                    ]
                )


                if resultado_verificacion.empty:

                    st.error(
                        f"❌ El ID **{id_consultado}** "
                        "no fue encontrado después de guardar."
                    )

                    st.stop()


                registro_verificado = (
                    resultado_verificacion.iloc[0]
                )


                programar_verificado = str(
                    registro_verificado.get(
                        "Programar Hoy",
                        ""
                    )
                ).strip()


                fecha_verificada = pd.to_datetime(
                    registro_verificado.get(
                        "Programado Para",
                        pd.NaT
                    ),
                    errors="coerce"
                )


                # --------------------------------------------------
                # CONFIRMAR GUARDADO
                # --------------------------------------------------

                if (
                    programar_verificado == "SI"
                    and
                    pd.notna(fecha_verificada)
                    and
                    fecha_verificada.normalize()
                    == fecha_hoy
                ):

                    st.success(
                        f"🟢 ID **{id_consultado}** "
                        "incorporado correctamente "
                        "a la programación de hoy."
                    )


                    # --------------------------------------------------
                    # RECARGAR
                    # --------------------------------------------------

                    st.rerun()


                else:

                    st.error(
                        f"❌ No se pudo confirmar la "
                        f"incorporación del ID **{id_consultado}**."
                    )


        # ==================================================
        # BANDEJA DE PROGRAMACIÓN
        # ==================================================

    st.divider()

    st.subheader(
        "📋 Bandeja de Programación"
    )

    st.caption(
        "IDs programados para la fecha de hoy."
    )


    # ======================================================
    # RECARGAR DATOS DESDE DISCO
    # ======================================================

    df_gestion = cargar_gestion()


    if df_gestion is None:

        st.warning(
            "No existe información en Gestión ID."
        )

        st.stop()


    # ======================================================
    # FECHA DE HOY
    # ======================================================

    fecha_hoy = (
        pd.Timestamp.now()
        .normalize()
    )


    # ======================================================
    # CONVERTIR FECHA PROGRAMADA
    # ======================================================

    fecha_programado = pd.to_datetime(
        df_gestion["Programado Para"],
        errors="coerce"
    ).dt.normalize()


    # ======================================================
    # FILTRAR PROGRAMADOS PARA HOY
    # ======================================================

    df_bandeja = df_gestion[
        fecha_programado.eq(
            fecha_hoy
        )
    ].copy()


    # ======================================================
    # CONTADOR
    # ======================================================

    st.metric(
        "📋 IDs programados para hoy",
        len(df_bandeja)
    )


    # ======================================================
    # MOSTRAR BANDEJA
    # ======================================================

    if df_bandeja.empty:

        st.info(
            "No hay IDs programados para hoy."
        )

    else:

        columnas_bandeja = [
            "ID",
            "Cliente",
            "Referencia del pedido",
            "Descripción",
            "Cantidad",
            "Fecha Entrega Producción",
            "Situación de Plazo",
            "Días Restantes",
            "Prioridad",
            "Programar Hoy",
            "Programado Para",
            "Estado Programador"
        ]


        columnas_disponibles = [
            columna
            for columna in columnas_bandeja
            if columna in df_bandeja.columns
        ]


        st.dataframe(
            df_bandeja[
                columnas_disponibles
            ],
            width="stretch",
            hide_index=True
        )          

# ==========================================================
# PROGRAMACIÓN
# ==========================================================

elif pagina == "📅 Programación":

    mostrar_programacion()

# ==========================================================
# PROGRAMACIÓN PERSONAL
# ==========================================================

elif pagina == "👥 Programación Personal":

    st.header(
        "👥 Programación Personal"
    )

    st.info(
        "Módulo pendiente de construcción."
    )


# ==========================================================
# ÓRDENES DE SERVICIO
# ==========================================================

elif pagina == "📄 Órdenes de Servicio":

    st.header(
        "📄 Órdenes de Servicio"
    )

    st.info(
        "Módulo pendiente de construcción."
    )

