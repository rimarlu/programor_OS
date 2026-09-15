from pathlib import Path
import pandas as pd

CARPETA_DATOS = Path("datos")
ARCHIVO_CATALOGO = CARPETA_DATOS / "catalogo_actividades.pkl"
CARPETA_DATOS.mkdir(exist_ok=True)

COLUMNAS_CATALOGO = [
    "Código Actividad",
    "Actividad",
    "Familia",
    "Tipo Trabajo",
    "Competencia Requerida",
    "Nivel Requerido",
    "Máquina",
    "Herramienta",
    "Vehículo",
    "Duración Estimada (min)",
    "Predecesora",
    "Observaciones",
]


def cargar_catalogo():
    if not ARCHIVO_CATALOGO.exists():
        return pd.DataFrame(columns=COLUMNAS_CATALOGO)
    try:
        df = pd.read_pickle(ARCHIVO_CATALOGO)
    except Exception:
        return pd.DataFrame(columns=COLUMNAS_CATALOGO)

    for col in COLUMNAS_CATALOGO:
        if col not in df.columns:
            df[col] = ""
    return df[COLUMNAS_CATALOGO].copy()


def guardar_catalogo(df):
    df = df.copy()
    for col in COLUMNAS_CATALOGO:
        if col not in df.columns:
            df[col] = ""
    df[COLUMNAS_CATALOGO].to_pickle(ARCHIVO_CATALOGO)


if not ARCHIVO_CATALOGO.exists():
    catalogo_inicial = pd.DataFrame([
        {
            "Código Actividad": "REV-ESP",
            "Actividad": "Revisar especificaciones",
            "Familia": "General",
            "Tipo Trabajo": "Producto/Servicio",
            "Competencia Requerida": "Interpretación de orden",
            "Nivel Requerido": "Básico",
            "Máquina": "",
            "Herramienta": "",
            "Vehículo": "",
            "Duración Estimada (min)": 15,
            "Predecesora": "",
            "Observaciones": "Validar descripción, medidas, cantidades y condiciones.",
        },
        {
            "Código Actividad": "CMP-INS",
            "Actividad": "Comprar insumos",
            "Familia": "Abastecimiento",
            "Tipo Trabajo": "Producto",
            "Competencia Requerida": "Compras",
            "Nivel Requerido": "Básico",
            "Máquina": "",
            "Herramienta": "",
            "Vehículo": "",
            "Duración Estimada (min)": 30,
            "Predecesora": "",
            "Observaciones": "Aplicar cuando el trabajo requiera insumos no disponibles.",
        },
        {
            "Código Actividad": "PRE-ARC",
            "Actividad": "Preparar archivo",
            "Familia": "Preproducción",
            "Tipo Trabajo": "Producto",
            "Competencia Requerida": "Diseño gráfico",
            "Nivel Requerido": "Intermedio",
            "Máquina": "PC",
            "Herramienta": "Software gráfico",
            "Vehículo": "",
            "Duración Estimada (min)": 30,
            "Predecesora": "",
            "Observaciones": "Preparación o ajuste del archivo para producción.",
        },
        {
            "Código Actividad": "IMP-001",
            "Actividad": "Impresión",
            "Familia": "Producción gráfica",
            "Tipo Trabajo": "Producto",
            "Competencia Requerida": "Impresión",
            "Nivel Requerido": "Intermedio",
            "Máquina": "Impresora",
            "Herramienta": "",
            "Vehículo": "",
            "Duración Estimada (min)": 60,
            "Predecesora": "Preparar archivo",
            "Observaciones": "Producción del material según especificaciones.",
        },
        {
            "Código Actividad": "REF-001",
            "Actividad": "Refilado",
            "Familia": "Acabados",
            "Tipo Trabajo": "Producto",
            "Competencia Requerida": "Acabados gráficos",
            "Nivel Requerido": "Básico",
            "Máquina": "",
            "Herramienta": "Bisturí/mesa de corte",
            "Vehículo": "",
            "Duración Estimada (min)": 30,
            "Predecesora": "Impresión",
            "Observaciones": "Corte o refilado del material.",
        },
        {
            "Código Actividad": "TUN-001",
            "Actividad": "Túneles perimetrales",
            "Familia": "Acabados",
            "Tipo Trabajo": "Producto",
            "Competencia Requerida": "Confección/acabados",
            "Nivel Requerido": "Intermedio",
            "Máquina": "",
            "Herramienta": "Equipo de confección",
            "Vehículo": "",
            "Duración Estimada (min)": 45,
            "Predecesora": "Refilado",
            "Observaciones": "Aplicar según especificación del producto.",
        },
        {
            "Código Actividad": "EMP-001",
            "Actividad": "Empaque",
            "Familia": "Despacho",
            "Tipo Trabajo": "Producto",
            "Competencia Requerida": "Logística",
            "Nivel Requerido": "Básico",
            "Máquina": "",
            "Herramienta": "",
            "Vehículo": "",
            "Duración Estimada (min)": 20,
            "Predecesora": "Control de calidad",
            "Observaciones": "Proteger y preparar para despacho.",
        },
        {
            "Código Actividad": "TRA-001",
            "Actividad": "Transporte",
            "Familia": "Logística",
            "Tipo Trabajo": "Producto/Servicio",
            "Competencia Requerida": "Conducción/logística",
            "Nivel Requerido": "Básico",
            "Máquina": "",
            "Herramienta": "",
            "Vehículo": "Vehículo de transporte",
            "Duración Estimada (min)": 60,
            "Predecesora": "Empaque",
            "Observaciones": "Aplicar cuando el alcance incluya despacho o instalación.",
        },
        {
            "Código Actividad": "INS-001",
            "Actividad": "Instalación",
            "Familia": "Instalación",
            "Tipo Trabajo": "Servicio",
            "Competencia Requerida": "Instalación",
            "Nivel Requerido": "Intermedio",
            "Máquina": "",
            "Herramienta": "Kit de instalación",
            "Vehículo": "Vehículo de transporte",
            "Duración Estimada (min)": 120,
            "Predecesora": "Transporte",
            "Observaciones": "Aplicar cuando el pedido incluya instalación.",
        },
        {
            "Código Actividad": "FOT-001",
            "Actividad": "Reporte fotográfico",
            "Familia": "Cierre",
            "Tipo Trabajo": "Servicio",
            "Competencia Requerida": "Instalación/reportes",
            "Nivel Requerido": "Básico",
            "Máquina": "",
            "Herramienta": "Celular/cámara",
            "Vehículo": "",
            "Duración Estimada (min)": 15,
            "Predecesora": "Instalación",
            "Observaciones": "Registrar evidencia del trabajo realizado.",
        },
    ], columns=COLUMNAS_CATALOGO)
    guardar_catalogo(catalogo_inicial)
