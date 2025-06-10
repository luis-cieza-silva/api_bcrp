import streamlit as st
import pandas as pd
import requests
import numpy as np

st.title("BCRP Extract App")
cod_serie=st.text_input("Inserte codigo de serie:")
year_inicio =st.text_input("Inserte año inicial:")
year_final = st.text_input("Inserte año final:")


url_base = 'https://estadisticas.bcrp.gob.pe/estadisticas/series/api/'
separador = '/'
codigo_serie = 'PM04986AA-PM04989AA-PM04990AA'
formato_salida = 'json'
periodo_inicial = '2010' 
periodo_final = '2024'
url = f"{url_base}{cod_serie}/{formato_salida}/{periodo_inicial}/{periodo_final}"

response = requests.get(url)
if response.status_code == 200:
    try:
        consulta = response.json()
    except ValueError:
        print('Error: La consulta no devolvió un JSON')
        consulta = None
else:
    print('Error en la consulta')
    consulta = None

#Nombres de las series
columns = consulta.get('config').get('series')
nombres_columnas = []
for i in columns:
    valor = i.get('name')
    nombres_columnas.append(valor)


#Periodos y valores
datos = consulta.get('periods')
#Periodos:
periodo = []
for i in datos:
    periodo.append(i.get('name'))

#Valores:
valores = []
for i in datos:
    valor = i['values']
    valores.append(valor)


#Creación del dataframe
dataset = {'Periodo': periodo, 'series': valores}
df = pd.DataFrame(dataset)
df[nombres_columnas] = df['series'].to_list()
df.drop(columns=['series'], inplace=True)
df.replace('n.d.', np.nan, inplace=True)

#Convertir columnas a tipo numérico
columns_to_float = df.columns[1:]
df[columns_to_float] = df[columns_to_float].astype(float)
print(df)
if st.button("Crear DataFrame"):
    st.write("Creando DataFrame...")
    st.table(df)
else:
    st.success("DataFrame creado exitosamente.")
    st.write("DataFrame creado con éxito. Aquí está el resultado:")



