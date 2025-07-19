import pandas as pd
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