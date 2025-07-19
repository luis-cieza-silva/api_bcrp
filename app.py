import streamlit as st
import pandas as pd
import numpy as np
from api_bcrp import obtener_dataframe_bcrp

st.title("BCRP Extract App")
cod_serie = st.text_input("Inserte codigo de serie:")
year_inicio = st.text_input("Inserte año inicial:")
year_final = st.text_input("Inserte año final:")

if st.button("Crear DataFrame"):
    if not cod_serie or not year_inicio or not year_final:
        st.error("Por favor, complete todos los campos.")
    else:
        try:
            df = obtener_dataframe_bcrp(cod_serie, year_inicio, year_final)
            st.success("DataFrame creado exitosamente.")
            st.table(df)
        except Exception as e:
            st.error(f"Error: {e}")



