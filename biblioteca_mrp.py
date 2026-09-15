import re
import unicodedata
from pathlib import Path

import pandas as pd
from rapidfuzz.fuzz import token_set_ratio


# ==========================================================
# RUTAS
# ==========================================================

CARPETA_DATOS = Path("datos")

ARCHIVO_BIBLIOTECA_MRP = (
    CARPETA_DATOS / "biblioteca_mrp.pkl"
)


# ==========================================================
# CAMPOS DE LA BIBLIOTECA
# ==========================================================

COLUMNAS_MRP = [
    "Operación",
    "Lista de materiales",
    "Centro de trabajo",
    "Cálculo de duración",
    "Duración",
    "Instrucciones",
]


# ==========================================================
# CARGAR BIBLIOTECA MRP
# ==========================================================

def cargar_biblioteca_mrp():

    if not ARCHIVO_BIBLIOTECA_MRP.exists():
        return None

    try:

        df = pd.read_pickle(
            ARCHIVO_BIBLIOTECA_MRP
        )

        # ----------------------------------------------
        # Limpiar nombres de campos
        # ----------------------------------------------

        df.columns = [
            str(columna).strip()
            for columna in df.columns
        ]

        # ----------------------------------------------
        # Validar campos
        # ----------------------------------------------

        faltantes = [
            campo
            for campo in COLUMNAS_MRP
            if campo not in df.columns
        ]

        if faltantes:
            return None

        return df[
            COLUMNAS_MRP
        ].copy()

    except Exception:
        return None


# ==========================================================
# NORMALIZAR TEXTO
# ==========================================================

def normalizar_texto(
    valor
):

    if pd.isna(valor):
        return ""

    texto = str(
        valor
    ).strip()

    if not texto:
        return ""

    # ----------------------------------------------
    # Minúsculas
    # ----------------------------------------------

    texto = texto.lower()

    # ----------------------------------------------
    # Eliminar acentos
    # ----------------------------------------------

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

    # ----------------------------------------------
    # Normalizar separadores
    # ----------------------------------------------

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
# PREPARAR BIBLIOTECA PARA BÚSQUEDA
# ==========================================================

def preparar_biblioteca(
    df_mrp
):

    if df_mrp is None or df_mrp.empty:
        return pd.DataFrame()

    df = df_mrp.copy()

    df["Texto búsqueda"] = (
        df["Lista de materiales"]
        .fillna("")
        .map(normalizar_texto)
    )

    df = df[
        df["Texto búsqueda"].ne("")
    ].copy()

    return df


# ==========================================================
# BUSCAR CONTEXTOS SIMILARES
# ==========================================================

def buscar_contextos_similares(
    descripcion,
    top_n=5,
    umbral=60
):

    df_mrp = cargar_biblioteca_mrp()

    if df_mrp is None:
        return pd.DataFrame()

    df = preparar_biblioteca(
        df_mrp
    )

    if df.empty:
        return pd.DataFrame()

    descripcion_normalizada = (
        normalizar_texto(
            descripcion
        )
    )

    if not descripcion_normalizada:
        return pd.DataFrame()

    # ======================================================
    # CALCULAR SIMILITUD
    # ======================================================

    df["Similitud"] = (
        df["Texto búsqueda"]
        .map(
            lambda texto: token_set_ratio(
                descripcion_normalizada,
                texto
            )
        )
    )

    # ======================================================
    # FILTRAR
    # ======================================================

    df = df[
        df["Similitud"] >= umbral
    ].copy()

    if df.empty:
        return pd.DataFrame()

    # ======================================================
    # ORDENAR
    # ======================================================

    df = df.sort_values(
        "Similitud",
        ascending=False
    )

    # ======================================================
    # DEVOLVER CAMPOS ÚTILES
    # ======================================================

    return df[
        [
            "Operación",
            "Lista de materiales",
            "Centro de trabajo",
            "Duración",
            "Similitud",
        ]
    ].head(
        top_n
    ).reset_index(
        drop=True
    )


# ==========================================================
# OBTENER OPERACIONES DE LOS MEJORES CONTEXTOS
# ==========================================================

def obtener_operaciones_contexto(
    descripcion,
    top_n=5,
    umbral=60
):

    resultados = (
        buscar_contextos_similares(
            descripcion,
            top_n=top_n,
            umbral=umbral
        )
    )

    if resultados.empty:
        return resultados

    return resultados


# ==========================================================
# RESUMIR OPERACIONES ENCONTRADAS
# ==========================================================

def resumir_operaciones(
    resultados
):

    if (
        resultados is None
        or resultados.empty
    ):

        return pd.DataFrame(
            columns=[
                "Operación",
                "Veces encontrada",
                "Mejor similitud",
                "Duración mínima",
                "Duración máxima",
            ]
        )

    resumen = (
        resultados
        .groupby(
            "Operación",
            as_index=False
        )
        .agg(
            Veces_encontrada=(
                "Operación",
                "size"
            ),
            Mejor_similitud=(
                "Similitud",
                "max"
            ),
            Duracion_minima=(
                "Duración",
                "min"
            ),
            Duracion_maxima=(
                "Duración",
                "max"
            ),
        )
    )

    resumen = resumen.rename(
        columns={
            "Veces_encontrada": "Veces encontrada",
            "Mejor_similitud": "Mejor similitud",
            "Duracion_minima": "Duración mínima",
            "Duracion_maxima": "Duración máxima",
        }
    )

    return resumen.sort_values(
        [
            "Mejor similitud",
            "Veces encontrada",
        ],
        ascending=[
            False,
            False,
        ]
    ).reset_index(
        drop=True
    )