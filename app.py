import os
import pandas as pd
import streamlit as st

from api_bcrp import obtener_dataframe_bcrp
from metadata import actualizar_metadata
import requests
import numpy as np

# --- Config de página ---
st.set_page_config(page_title="BCRP - API", page_icon="📊", layout="wide")

# --- Rutas ---
RUTA_CSV_LINKS = "master_categorias_urls.csv"
RUTA_METADATA = "metadata.csv"

# --- Cache lectura metadata ---
@st.cache_data
def cargar_series(ruta: str) -> pd.DataFrame:
    return pd.read_csv(ruta)

# --- Header ---
st.markdown(
    """
<div style='text-align:center;padding:1rem;background:linear-gradient(90deg,#1f77b4,#ff7f0e);border-radius:10px;margin-bottom:1rem;'>
  <h1 style='color:#fff;margin:0;'>📊 BCRP - API</h1>
  <p style='color:#fff;margin:0;font-size:18px;'>Consulta y visualiza series estadísticas del BCRP</p>
</div>
""",
    unsafe_allow_html=True
)

# --- Expander: Sobre el proyecto ---
with st.expander("ℹ️ Sobre el proyecto", expanded=False):
    st.markdown(
        """
**API BCRP** permite acceder y visualizar información de las series estadísticas del **Banco Central de Reserva del Perú (BCRP)** a través de su API pública.

**Características:**
- Selección por categoría
- Múltiples series simultáneas
- Metadatos visibles
- Gráfico de líneas automático
- Exportación visual rápida
"""
    )

# --- Expander: Función principal (solo ejemplo legible, sin incrustar la app dentro) ---
with st.expander("🛠️ Función para extraer datos del BCRP", expanded=False):
    st.code(
        """import pandas as pd
import requests
import numpy as np
        

def obtener_dataframe_bcrp(codigo_serie, periodo_inicial, periodo_final):
    url_base = 'https://estadisticas.bcrp.gob.pe/estadisticas/series/api/'
    formato_salida = 'json'
    url = f"{url_base}{codigo_serie}/{formato_salida}/{periodo_inicial}/{periodo_final}"

    response = requests.get(url)
    if response.status_code == 200:
        try:
            consulta = response.json()
        except ValueError:
            raise Exception('Error: La consulta no devolvió un JSON')
    else:
        raise Exception('Error en la consulta')

    columns = consulta.get('config', {}).get('series', [])
    nombres_columnas = [i.get('name') for i in columns]

    datos = consulta.get('periods', [])
    periodo = [i.get('name') for i in datos]
    valores = [i.get('values') for i in datos]

    dataset = {'Periodo': periodo, 'series': valores}
    df = pd.DataFrame(dataset)
    if nombres_columnas:
        df[nombres_columnas] = df['series'].to_list()
        df.drop(columns=['series'], inplace=True)
        df.replace('n.d.', np.nan, inplace=True)
        columns_to_float = df.columns[1:]
        df[columns_to_float] = df[columns_to_float].astype(float)
        return df
    else:
        raise Exception("No se encontraron nombres de columnas en la respuesta.")
""",
        language="python"
    )

# --- Disponibilidad / actualización de metadata ---
st.markdown("### 🗂️ Disponibilidad de series")
col_upd, col_note = st.columns([1, 4])
with col_upd:
    if st.button("🔄 Actualizar metadata"):
        with st.spinner("Descargando metadata..."):
            try:
                actualizar_metadata(RUTA_CSV_LINKS, RUTA_METADATA)
                st.success("Metadata actualizada.")
                st.cache_data.clear()
            except Exception as e:
                st.error(f"Error actualizando metadata: {e}")
with col_note:
    st.info("Si es tu primera vez, presiona **Actualizar metadata** para cargar la disponibilidad de series.")

# Validaciones de metadata
if not os.path.exists(RUTA_METADATA):
    st.warning("No existe **metadata.csv**. Actualiza para continuar.")
    st.stop()

try:
    df_series = cargar_series(RUTA_METADATA)
except Exception as e:
    st.error(f"No se pudo leer {RUTA_METADATA}: {e}")
    st.stop()

requeridas = {"categoria", "nombre_serie", "codigo", "fecha_inicio", "fecha_fin", "periodicidad"}
faltantes = requeridas - set(df_series.columns)
if faltantes:
    st.error(f"Faltan columnas en metadata: {', '.join(sorted(faltantes))}")
    st.stop()

# --- Selección de series ---
st.markdown("### 🔍 Selección de series")
col_cat, col_series = st.columns([1, 2])

with col_cat:
    categorias = sorted(df_series["categoria"].dropna().unique().tolist())
    if not categorias:
        st.error("No hay categorías disponibles en la metadata.")
        st.stop()
    categoria_sel = st.selectbox("📂 Categorías sugeridas", categorias)

with col_series:
    df_cat = df_series[df_series["categoria"] == categoria_sel].copy()
    opciones_series = df_cat["nombre_serie"].dropna().unique().tolist()
    seleccion_series = st.multiselect(
        "📈 Series (múltiples)",
        opciones_series,
        default=[opciones_series[0]] if opciones_series else [],
    )

if not seleccion_series:
    st.info("Selecciona al menos una serie para continuar.")
    st.stop()

# --- Metadatos de las series seleccionadas (contraste sobre fondo blanco) ---
st.markdown("### 📋 Metadatos de las series seleccionadas")
PALETA = ["#2563eb", "#059669", "#ea580c", "#7c3aed", "#dc2626", "#0d9488", "#d97706"]

meta_cols = st.columns(len(seleccion_series))
for i, nombre in enumerate(seleccion_series):
    fila = df_cat[df_cat["nombre_serie"] == nombre]
    if fila.empty:
        continue
    info = fila.iloc[0]
    color = PALETA[i % len(PALETA)]
    codigo = str(info.get("codigo", ""))
    f_ini = str(info.get("fecha_inicio", ""))
    f_fin = str(info.get("fecha_fin", ""))
    peri  = str(info.get("periodicidad", ""))
    titulo = str(info.get("nombre_serie", ""))

    card_html = f"""
    <div style="
        background:#ffffff;
        border:1px solid #e5e7eb;
        border-top:6px solid {color};
        border-radius:10px;
        padding:12px 14px;
        box-shadow:0 1px 2px rgba(0,0,0,0.04);
        ">
        <div style="font-weight:700;color:#111827;margin-bottom:4px;">
            {titulo[:80]}{'…' if len(titulo) > 80 else ''}
        </div>
        <div style="font-family:ui-monospace, SFMono-Regular, Menlo, monospace;
                    display:inline-block;
                    padding:2px 6px;
                    border-radius:6px;
                    background:rgba(0,0,0,0.04);
                    color:#111827;
                    border:1px dashed {color};
                    margin-bottom:6px;">
            {codigo}
        </div>
        <div style="color:#374151;line-height:1.4;">
            <strong>Inicio:</strong> {f_ini}<br>
            <strong>Fin:</strong> {f_fin}<br>
            <strong>Periodicidad:</strong> {peri}
        </div>
    </div>
    """
    with meta_cols[i]:
        st.markdown(card_html, unsafe_allow_html=True)

# --- Parámetros de consulta ---
st.markdown("### ⚙️ Parámetros de consulta")
p_cod, p_ini, p_fin, p_btn = st.columns([3, 1, 1, 1])

codigos_defecto = (
    df_cat[df_cat["nombre_serie"].isin(seleccion_series)]["codigo"]
    .dropna().astype(str).tolist()
)
entrada_codigos = "-".join(codigos_defecto)

with p_cod:
    codigos_input = st.text_input(
        "Código(s) de serie",
        value=entrada_codigos,
        help="Separa múltiples códigos con guiones (-). Requiere misma periodicidad.",
    )

fila_ref = df_cat[df_cat["nombre_serie"] == seleccion_series[0]].iloc[0]
with p_ini:
    anio_ini = st.text_input("Año inicial", value=str(fila_ref.get("fecha_inicio", "")))
with p_fin:
    anio_fin = st.text_input("Año final", value=str(fila_ref.get("fecha_fin", "")))
with p_btn:
    st.markdown("<br>", unsafe_allow_html=True)
    disparar = st.button("🚀 Crear DataFrame")

# --- Ejecución de consulta ---
if disparar:
    if not codigos_input or not anio_ini or not anio_fin:
        st.error("Completa todos los campos antes de consultar.")
        st.stop()

    try:
        df = obtener_dataframe_bcrp(codigos_input, anio_ini, anio_fin)
    except Exception as e:
        st.error(f"Error al consultar la API del BCRP: {e}")
        st.stop()

    if df is None or df.empty:
        st.warning("La consulta no devolvió datos.")
        st.stop()

    if "Periodo" not in df.columns:
        st.error("El DataFrame no contiene la columna 'Periodo'.")
        st.stop()

    st.success("Datos descargados correctamente.")

    c_tabla, c_graf = st.columns([1, 1])
    with c_tabla:
        st.markdown("### 📊 Datos")
        st.dataframe(df, use_container_width=True, height=420)
    with c_graf:
        st.markdown("### 📈 Gráfico")
        series_cols = [c for c in df.columns if c != "Periodo"]
        if series_cols:
            try:
                st.line_chart(
                    df.set_index("Periodo")[series_cols],
                    use_container_width=True,
                    height=420,
                )
            except Exception:
                st.info("No fue posible graficar. Verifica que las columnas de series sean numéricas.")
        else:
            st.info("No hay columnas de series para graficar.")

# --- Footer ---
st.markdown("---")
st.markdown(
    """
<div style='text-align:center;color:#666;padding:1rem;'>
  Desarrollado por <strong>Luis Cieza Silva</strong> ·
  <a href='https://github.com/luis-cieza-silva/api_bcrp' target='_blank'>Repo GitHub</a> ·
  Datos: BCRP
</div>
""",
    unsafe_allow_html=True
)