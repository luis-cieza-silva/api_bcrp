import requests
from bs4 import BeautifulSoup
import pandas as pd

def obtener_periodicidad(codigo):
    if codigo.endswith("A"):
        return "Anual"
    elif codigo.endswith("Q"):
        return "Trimestral"
    else:
        return "Desconocida"

def obtener_categoria(url):
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.content, "html.parser")
        h2 = soup.find("h2", class_="categoria")
        categoria = h2.contents[0].strip() if h2 else ""
        return categoria, soup
    except Exception as e:
        print(f"Error en {url}: {e}")
        return "", None

def obtener_series_desde_links(ruta_csv):
    df_links = pd.read_csv(ruta_csv, delimiter=';')
    todas_las_series = []
    for i, row in df_links.iterrows():
        url = row["Link"]
        categoria, soup = obtener_categoria(url)
        if not soup:
            continue
        tabla = soup.find("table", class_="series")
        if not tabla:
            print(f"No se encontró tabla en: {url}")
            continue
        filas = tabla.find_all("tr")[1:]
        for fila in filas:
            try:
                celdas = fila.find_all("td")
                if len(celdas) >= 6:
                    codigo = celdas[1].text.strip()
                    nombre = celdas[2].text.strip()
                    fecha_inicio = celdas[3].text.strip()
                    fecha_fin = celdas[4].text.strip()
                    ultima_actualizacion = celdas[5].text.strip()
                    periodicidad = obtener_periodicidad(codigo)
                    todas_las_series.append({
                        "codigo": codigo,
                        "nombre_serie": nombre,
                        "fecha_inicio": fecha_inicio,
                        "fecha_fin": fecha_fin,
                        "ultima_actualizacion": ultima_actualizacion,
                        "categoria": categoria,
                        "categoria_url": url,
                        "periodicidad": periodicidad
                    })
            except Exception as e:
                print(f"Error procesando fila en {url}: {e}")
    return pd.DataFrame(todas_las_series)

def actualizar_metadata(ruta_csv, ruta_salida):
    df = obtener_series_desde_links(ruta_csv)
    df.to_csv(ruta_salida, index=False)
    return df
