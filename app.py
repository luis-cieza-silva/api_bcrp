import streamlit as st
import pandas as pd
import os
from api_bcrp import obtener_dataframe_bcrp
from metadata import actualizar_metadata

RUTA_CSV_LINKS = "master_categorias_urls.csv"
RUTA_METADATA = "metadata.csv"

@st.cache_data
def cargar_series():
    return pd.read_csv(RUTA_METADATA)

st.title("BCRP Extract App")

if not os.path.exists(RUTA_METADATA):
    st.warning("No existe metadata.csv. Presiona el botón para generar la metadata.")
    if st.button("Actualizar metadata"):
        with st.spinner("Actualizando metadata, esto puede tardar unos minutos..."):
            df_actualizada = actualizar_metadata(RUTA_CSV_LINKS, RUTA_METADATA)
            st.success("Metadata actualizada y guardada correctamente.")
    st.stop()

if st.button("Actualizar metadata"):
    with st.spinner("Actualizando metadata, esto puede tardar unos minutos..."):
        df_actualizada = actualizar_metadata(RUTA_CSV_LINKS, RUTA_METADATA)
        st.success("Metadata actualizada y guardada correctamente.")

df_series = cargar_series()

# Agrupar por categoría y mostrar sugerencias
st.sidebar.header("Sugerencias de series estadísticas")

# Mostrar solo categorías únicas y no nulas
categorias = sorted(df_series["categoria"].dropna().unique())
categoria_seleccionada = st.sidebar.selectbox("Seleccione una categoría", categorias)

# Filtrar series por la categoría seleccionada y mostrar solo nombres únicos
series_categoria = df_series[df_series["categoria"] == categoria_seleccionada]
series_unicas = series_categoria["nombre_serie"].dropna().unique()
series_seleccionadas = st.sidebar.multiselect(
    "Seleccione una o más series",
    options=series_unicas,
    default=[series_unicas[0]] if len(series_unicas) > 0 else []
)

# Mostrar metadatos de todas las series seleccionadas con formato y color
if series_seleccionadas:
    st.sidebar.markdown("<hr>", unsafe_allow_html=True)
    st.sidebar.markdown(
        "<span style='color:#1f77b4; font-size:18px; font-weight:bold;'>Metadatos de las series seleccionadas:</span>",
        unsafe_allow_html=True
    )
    for serie_nombre in series_seleccionadas:
        serie_info = series_categoria[series_categoria["nombre_serie"] == serie_nombre].iloc[0]
        st.sidebar.markdown(
            f"""
            <div style="background-color:#f0f8ff; border-radius:8px; padding:8px; margin-bottom:8px;">
            <span style="color:#2c3e50; font-weight:bold;">{serie_info['nombre_serie']}</span><br>
            <span style="color:#7f8c8d;">Código:</span> <span style="color:#e74c3c; font-weight:bold;">{serie_info['codigo']}</span><br>
            <span style="color:#7f8c8d;">Fecha inicio:</span> <span style="color:#16a085;">{serie_info['fecha_inicio']}</span><br>
            <span style="color:#7f8c8d;">Fecha fin:</span> <span style="color:#16a085;">{serie_info['fecha_fin']}</span><br>
            <span style="color:#7f8c8d;">Última actualización:</span> <span style="color:#2980b9;">{serie_info['ultima_actualizacion']}</span><br>
            <span style="color:#7f8c8d;">Periodicidad:</span> <span style="color:#8e44ad;">{serie_info['periodicidad']}</span>
            </div>
            """,
            unsafe_allow_html=True
        )

# Obtener los códigos de las series seleccionadas
codigos_seleccionados = series_categoria[series_categoria["nombre_serie"].isin(series_seleccionadas)]["codigo"].tolist()
codigos_default = "-".join(codigos_seleccionados)

# Inputs distribuidos horizontalmente
col1, col2, col3 = st.columns([2, 1, 1])
with col1:
    cod_serie = st.text_input(
        "Código(s) de serie",
        value=codigos_default,
        help="Para consultar varias series, sepáralas por guiones. Ejemplo: COD1-COD2-COD3"
    )
with col2:
    year_inicio = st.text_input(
        "Año inicial",
        value=str(series_categoria[series_categoria["nombre_serie"] == series_seleccionadas[0]]["fecha_inicio"].iloc[0]) if series_seleccionadas else ""
    )
with col3:
    year_final = st.text_input(
        "Año final",
        value=str(series_categoria[series_categoria["nombre_serie"] == series_seleccionadas[0]]["fecha_fin"].iloc[0]) if series_seleccionadas else ""
    )

if st.button("Crear DataFrame"):
    if not cod_serie or not year_inicio or not year_final:
        st.error("Por favor, complete todos los campos.")
    else:
        try:
            df = obtener_dataframe_bcrp(cod_serie, year_inicio, year_final)
            st.success("DataFrame creado exitosamente.")
            st.dataframe(df)
            
            # Mostrar gráfico de líneas si hay más de una columna de serie
            series_cols = df.columns[1:]  # Excluye 'Periodo'
            if len(series_cols) > 0:
                st.markdown("### Gráfico de líneas de las series seleccionadas")
                st.line_chart(df.set_index("Periodo")[series_cols])
        except Exception as e:
            st.error(f"Error: {e}")
