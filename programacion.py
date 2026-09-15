import streamlit as st
from pathlib import Path
import pandas as pd


# ==========================================================
# RUTAS DE DATOS
# ==========================================================

CARPETA_DATOS = Path("datos")

ARCHIVO_GESTION = (
    CARPETA_DATOS / "gestion_id.pkl"
)


# ==========================================================
# CARGAR GESTIÓN ID
# ==========================================================

def cargar_gestion():

    if not ARCHIVO_GESTION.exists():
        return None

    try:
        return pd.read_pickle(
            ARCHIVO_GESTION
        )

    except Exception as e:

        st.error(
            f"No fue posible cargar Gestión ID: {e}"
        )

        return None


# ==========================================================
# OBTENER IDS PROGRAMADOS PARA HOY
# ==========================================================

def obtener_ids_programados_hoy(
    df_gestion
):

    if (
        df_gestion is None
        or df_gestion.empty
    ):
        return pd.DataFrame()

    if "Programado Para" not in df_gestion.columns:
        return pd.DataFrame()

    fecha_hoy = (
        pd.Timestamp.now()
        .normalize()
    )

    fecha_programada = pd.to_datetime(
        df_gestion["Programado Para"],
        errors="coerce"
    ).dt.normalize()

    return df_gestion[
        fecha_programada.eq(fecha_hoy)
    ].copy()


# ==========================================================
# CONSTRUIR TEXTO COMPLETO DEL ID
# ==========================================================

def construir_texto_completo_id(
    fila
):

    partes = []

    for columna in fila.index:

        valor = fila[columna]

        if pd.isna(valor):
            continue

        texto = str(
            valor
        ).strip()

        if not texto:
            continue

        partes.append(
            f"{columna}: {texto}"
        )

    return "\n".join(
        partes
    )


# ==========================================================
# LIMPIAR CHECKBOXES DE UN ID
# ==========================================================

def limpiar_checkboxes_id(
    id_actual
):

    prefijo = (
        f"check_{id_actual}_"
    )

    claves = [
        clave
        for clave in st.session_state.keys()
        if str(clave).startswith(prefijo)
    ]

    for clave in claves:

        del st.session_state[clave]


# ==========================================================
# PLANEAR ACTIVIDADES DE LOS IDS PROGRAMADOS PARA HOY
# ==========================================================

def planear_actividades_ids_hoy(
    df_gestion
):

    from actividades import (
        analizar_y_guardar_propuesta,
        obtener_actividades_id,
        cargar_actividades,
        guardar_actividades,
    )

    st.divider()

    st.header(
        "🤖 Planear actividades de los IDs de hoy"
    )

    st.caption(
        "La IA analiza cada ID y propone un universo "
        "de actividades. El usuario decide cuáles "
        "se requieren para la programación."
    )

    # ======================================================
    # VALIDAR GESTIÓN ID
    # ======================================================

    if (
        df_gestion is None
        or df_gestion.empty
    ):

        st.info(
            "No existe información en Gestión ID."
        )

        return

    # ======================================================
    # OBTENER IDS DE HOY
    # ======================================================

    df_hoy = (
        obtener_ids_programados_hoy(
            df_gestion
        )
    )

    if df_hoy.empty:

        st.info(
            "No existen IDs programados para hoy."
        )

        return

    # ======================================================
    # RESUMEN
    # ======================================================

    st.metric(
        "📋 IDs programados para hoy",
        len(df_hoy)
    )

    # ==================================================
    # PROCESAR CADA ID
    # ==================================================

    total_ids = len(df_hoy)

    for posicion, (_, fila) in enumerate(
        df_hoy.iterrows(),
        start=1
    ):

        id_actual = str(
            fila.get(
                "ID",
                ""
            )
        ).strip()

        if not id_actual:
            continue

        referencia = str(
            fila.get(
                "Referencia del pedido",
                ""
            )
        ).strip()

        cliente = str(
            fila.get(
                "Cliente",
                ""
            )
        ).strip()

        descripcion = str(
            fila.get(
                "Descripción",
                ""
            )
        ).strip()

        # ==================================================
        # EXPANDER DEL ID
        # ==================================================

        with st.expander(
            f"📋 ID {posicion} de {total_ids} | "
            f"{id_actual} | {referencia}",
            expanded=True
        ):

            # ----------------------------------------------
            # INFORMACIÓN DEL ID
            # ----------------------------------------------

            st.write(
                f"**Cliente:** {cliente}"
            )

            st.write(
                f"**Referencia del pedido:** {referencia}"
            )

            st.write(
                f"**Descripción:** {descripcion}"
            )

            if "Cantidad" in fila.index:

                st.write(
                    f"**Cantidad:** {fila['Cantidad']}"
                )

            if "Fecha Orden" in fila.index:

                st.write(
                    f"**Fecha Orden:** {fila['Fecha Orden']}"
                )

            if "Fecha Entrega Producción" in fila.index:

                st.write(
                    "**Fecha Entrega Producción:** "
                    f"{fila['Fecha Entrega Producción']}"
                )

            if "Prioridad" in fila.index:

                st.write(
                    f"**Prioridad:** {fila['Prioridad']}"
                )

            if "Estado ID" in fila.index:

                st.write(
                    f"**Estado ID:** {fila['Estado ID']}"
                )

            # ----------------------------------------------
            # ANALIZAR ID
            # ----------------------------------------------

            st.markdown(
                "### 🤖 Análisis del ID"
            )

            if st.button(
                "🤖 Analizar actividades",
                key=f"analizar_id_hoy_{id_actual}",
                type="primary"
            ):

                registro_completo = (
                    fila.to_dict()
                )

                nuevas, analisis = (
                    analizar_y_guardar_propuesta(
                        registro_completo
                    )
                )

                st.session_state[
                    f"analisis_id_{id_actual}"
                ] = analisis

                limpiar_checkboxes_id(
                    id_actual
                )

                st.success(
                    f"Análisis realizado. "
                    f"Se generaron {len(nuevas)} "
                    "actividades propuestas."
                )

                st.rerun()

            # ----------------------------------------------
            # RESULTADO DEL ANÁLISIS
            # ----------------------------------------------

            resultado = st.session_state.get(
                f"analisis_id_{id_actual}"
            )

            if resultado:

                col1, col2 = st.columns(2)

                with col1:

                    st.write(
                        "**Tipo:** "
                        f"{resultado.get('tipo', '')}"
                    )

                with col2:

                    st.write(
                        "**Familia:** "
                        f"{resultado.get('familia', '')}"
                    )

                texto_analisis = resultado.get(
                    "texto",
                    ""
                )

                if texto_analisis:

                    with st.expander(
                        "🔎 Ver análisis"
                    ):

                        st.write(
                            texto_analisis
                        )

            # ----------------------------------------------
            # OBTENER ACTIVIDADES DEL ID
            # ----------------------------------------------

            df_actividades = (
                obtener_actividades_id(
                    id_actual
                )
            )

            if (
                df_actividades is None
                or df_actividades.empty
            ):

                st.info(
                    "Este ID todavía no tiene "
                    "actividades propuestas."
                )

                continue

            # ----------------------------------------------
            # VALIDAR COLUMNA ACTIVIDAD
            # ----------------------------------------------

            if "Actividad" not in df_actividades.columns:

                st.error(
                    "La tabla de actividades no contiene "
                    "la columna 'Actividad'."
                )

                continue

            # ----------------------------------------------
            # ORDENAR ACTIVIDADES
            # ----------------------------------------------

            if "Orden Propuesta" in df_actividades.columns:

                df_actividades = (
                    df_actividades
                    .sort_values(
                        "Orden Propuesta",
                        na_position="last"
                    )
                )

            # ----------------------------------------------
            # TITULO
            # ----------------------------------------------

            st.markdown(
                "### 🤖 Actividades propuestas por IA"
            )

            st.caption(
                "Marque solamente las actividades "
                "que necesita ejecutar."
            )

            # ==================================================
            # BOTONES DE SELECCIÓN
            # ==================================================

            col1, col2 = st.columns(2)

            with col1:

                if st.button(
                    "[ Seleccionar todas ]",
                    key=(
                        f"seleccionar_todas_"
                        f"{id_actual}"
                    )
                ):

                    for idx in df_actividades.index:

                        st.session_state[
                            f"check_{id_actual}_{idx}"
                        ] = True

                    st.rerun()

            with col2:

                if st.button(
                    "[ Deseleccionar todas ]",
                    key=(
                        f"deseleccionar_todas_"
                        f"{id_actual}"
                    )
                ):

                    for idx in df_actividades.index:

                        st.session_state[
                            f"check_{id_actual}_{idx}"
                        ] = False

                    st.rerun()

            # ==================================================
            # CHECKBOXES
            # ==================================================

            seleccionadas = []

            for idx, actividad in df_actividades.iterrows():

                nombre_actividad = str(
                    actividad.get(
                        "Actividad",
                        ""
                    )
                ).strip()

                if not nombre_actividad:
                    continue

                clave = (
                    f"check_"
                    f"{id_actual}_"
                    f"{idx}"
                )

                if clave not in st.session_state:

                    estado = str(
                        actividad.get(
                            "Estado",
                            ""
                        )
                    ).strip()

                    seleccionada_bd = (
                        str(
                            actividad.get(
                                "Seleccionada",
                                False
                            )
                        )
                        .strip()
                        .lower()
                        == "true"
                    )

                    st.session_state[
                        clave
                    ] = (
                        estado == "Aprobada"
                        or seleccionada_bd
                    )

                marcada = st.checkbox(
                    nombre_actividad,
                    key=clave
                )

                if marcada:

                    seleccionadas.append(
                        idx
                    )

            # ==================================================
            # CONTADOR
            # ==================================================

            st.write(
                "☑ Actividades seleccionadas: "
                f"**{len(seleccionadas)}**"
            )

            # ==================================================
            # ACEPTAR SELECCIONADAS
            # ==================================================

            if st.button(
                "[ Aceptar seleccionadas ]",
                key=f"aceptar_{id_actual}",
                type="primary"
            ):

                df_guardar = (
                    cargar_actividades()
                )

                if df_guardar is None:

                    st.error(
                        "No fue posible cargar "
                        "las actividades."
                    )

                    continue

                # ------------------------------------------
                # ASEGURAR COLUMNAS
                # ------------------------------------------

                if "Seleccionada" not in df_guardar.columns:

                    df_guardar[
                        "Seleccionada"
                    ] = False

                if "Estado" not in df_guardar.columns:

                    df_guardar[
                        "Estado"
                    ] = "Propuesta"

                if "Fecha Programación" not in df_guardar.columns:

                    df_guardar[
                        "Fecha Programación"
                    ] = pd.NaT

                # ------------------------------------------
                # PROCESAR CADA ACTIVIDAD
                # ------------------------------------------

                for idx in df_actividades.index:

                    if idx not in df_guardar.index:
                        continue

                    clave = (
                        f"check_"
                        f"{id_actual}_"
                        f"{idx}"
                    )

                    seleccionada = bool(
                        st.session_state.get(
                            clave,
                            False
                        )
                    )

                    # ======================================
                    # SELECCIONADA
                    # ======================================

                    if seleccionada:

                        df_guardar.loc[
                            idx,
                            "Seleccionada"
                        ] = True

                        df_guardar.loc[
                            idx,
                            "Estado"
                        ] = "Aprobada"

                        df_guardar.loc[
                            idx,
                            "Fecha Programación"
                        ] = (
                            pd.Timestamp.now()
                            .normalize()
                        )

                    # ======================================
                    # NO SELECCIONADA
                    # ======================================

                    else:

                        estado_actual = str(
                            df_guardar.loc[
                                idx,
                                "Estado"
                            ]
                        ).strip()

                        if estado_actual == "Aprobada":

                            df_guardar.loc[
                                idx,
                                "Seleccionada"
                            ] = False

                            df_guardar.loc[
                                idx,
                                "Estado"
                            ] = "Propuesta"

                            df_guardar.loc[
                                idx,
                                "Fecha Programación"
                            ] = pd.NaT

                # ------------------------------------------
                # GUARDAR
                # ------------------------------------------

                guardar_actividades(
                    df_guardar
                )

                st.success(
                    f"Las actividades seleccionadas "
                    f"del ID {id_actual} quedaron aprobadas."
                )

                st.rerun()


# ==========================================================
# MOSTRAR PROGRAMACIÓN
# ==========================================================

def mostrar_programacion():

    st.header(
        "📅 Programación"
    )

    st.caption(
        "Programación de los IDs y sus actividades "
        "para la jornada."
    )

    # ======================================================
    # CARGAR GESTIÓN ID
    # ======================================================

    df_gestion = cargar_gestion()

    if df_gestion is None:

        st.warning(
            "No existe información en Gestión ID."
        )

        return

    # ======================================================
    # MOSTRAR PROGRAMACIÓN
    # ======================================================

    planear_actividades_ids_hoy(
        df_gestion
    )
