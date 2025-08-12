import requests
from bs4 import BeautifulSoup
import pandas as pd
from urllib.parse import urlparse
from typing import Tuple, Dict, Optional

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0 Safari/537.36"
    )
}

def obtener_periodicidad(codigo: str) -> str:
    c = (codigo or "").strip().upper()
    if c.endswith("A"): return "Anual"
    if c.endswith("Q"): return "Trimestral"
    if c.endswith("M"): return "Mensual"
    if c.endswith("D"): return "Diaria"
    return "Desconocida"

def _extraer_categoria_por_selectores(soup: BeautifulSoup) -> str:
    for sel in ("h2.categoria", "h2.categoria_titulo", ".categoria_titulo", ".categoria"):
        n = soup.select_one(sel)
        if n:
            t = n.get_text(" ", strip=True)
            if t: return t
    return ""

def _texto_heading_categoria(nodo_h2) -> str:
    if not nodo_h2: return ""
    txt = nodo_h2.get_text(" ", strip=True)
    return txt.split(" - (")[0].strip()

def _fallback_categoria(soup: BeautifulSoup, url: str) -> str:
    t = soup.find("title")
    if t and t.get_text(strip=True): return t.get_text(strip=True)
    bc = soup.select_one(".breadcrumb, .miga, nav[aria-label='breadcrumb']")
    if bc:
        txt = bc.get_text(" ", strip=True)
        if txt: return txt
    path = urlparse(url).path.strip("/").split("/")
    if path:
        slug = path[-1].replace("-", " ").strip()
        if slug: return slug.title()
    return ""

def _categoria_cercana_a_tabla(tabla, soup: BeautifulSoup, url: str) -> str:
    # 1) heading más cercano
    h2 = tabla.find_previous("h2")
    cat = _texto_heading_categoria(h2) if h2 else ""
    if cat: return cat
    # 2) selectores globales
    cat = _extraer_categoria_por_selectores(soup)
    if cat: return cat
    # 3) fallbacks
    return _fallback_categoria(soup, url)

def _normaliza(s: Optional[str]) -> str:
    return (s or "").strip().lower()

def _indices_por_encabezado(tabla) -> Dict[str, int]:
    head = tabla.find("tr")
    if not head: return {}
    ths = head.find_all(["th", "td"])
    headers = [_normaliza(th.get_text()) for th in ths]
    mapa: Dict[str, int] = {}
    for i, h in enumerate(headers):
        if "código" in h or "codigo" in h: mapa["codigo"] = i
        elif "serie" in h or "nombre" in h: mapa["nombre"] = i
        elif "fecha inicio" in h or "inicio" in h: mapa["fecha_inicio"] = i
        elif "fecha fin" in h or "fin" in h: mapa["fecha_fin"] = i
        elif "última actualización" in h or "ultima actualizacion" in h: mapa["ultima_actualizacion"] = i
    return mapa

def _get(url: str) -> BeautifulSoup:
    resp = requests.get(url, headers=HEADERS, timeout=20)
    resp.raise_for_status()
    return BeautifulSoup(resp.content, "html.parser")

def obtener_categoria(url: str) -> Tuple[str, Optional[BeautifulSoup]]:
    try:
        soup = _get(url)
        # Por compatibilidad con tu firma original
        categoria = _extraer_categoria_por_selectores(soup) or _fallback_categoria(soup, url)
        return categoria, soup
    except Exception as e:
        print(f"Error en {url}: {e}")
        return "", None

def obtener_series_desde_links(ruta_csv: str) -> pd.DataFrame:
    df_links = pd.read_csv(ruta_csv, delimiter=';')
    todas = []

    for _, row in df_links.iterrows():
        url = row["Link"]
        try:
            soup = _get(url)
        except Exception as e:
            print(f"Error al abrir {url}: {e}")
            continue

        tablas = soup.select("div.tcg-elevator table.series, table.series")
        if not tablas:
            print(f"No se encontró tabla en: {url}")
            continue

        for tabla in tablas:
            categoria = _categoria_cercana_a_tabla(tabla, soup, url)
            mapa_idx = _indices_por_encabezado(tabla)
            filas = tabla.find_all("tr")[1:]

            for fila in filas:
                celdas = fila.find_all("td")
                if not celdas:  # filas vacías o separadores
                    continue
                try:
                    if mapa_idx:
                        codigo = celdas[mapa_idx.get("codigo", 1)].get_text(strip=True)
                        nombre_td = celdas[mapa_idx.get("nombre", 2)]
                        enlace = nombre_td.find("a")
                        nombre = (enlace.get_text(strip=True) if enlace else nombre_td.get_text(strip=True))
                        fecha_inicio = celdas[mapa_idx.get("fecha_inicio", 3)].get_text(strip=True)
                        fecha_fin = celdas[mapa_idx.get("fecha_fin", 4)].get_text(strip=True)
                        ultima_actualizacion = celdas[mapa_idx.get("ultima_actualizacion", 5)].get_text(strip=True)
                    else:
                        if len(celdas) < 6:  # esquema mínimo
                            continue
                        codigo = celdas[1].get_text(strip=True)
                        enlace = celdas[2].find("a")
                        nombre = (enlace.get_text(strip=True) if enlace else celdas[2].get_text(strip=True))
                        fecha_inicio = celdas[3].get_text(strip=True)
                        fecha_fin = celdas[4].get_text(strip=True)
                        ultima_actualizacion = celdas[5].get_text(strip=True)

                    todas.append({
                        "codigo": codigo,
                        "nombre_serie": nombre,
                        "fecha_inicio": fecha_inicio,
                        "fecha_fin": fecha_fin,
                        "ultima_actualizacion": ultima_actualizacion,
                        "categoria": categoria,
                        "categoria_url": url,
                        "periodicidad": obtener_periodicidad(codigo),
                    })
                except Exception as e:
                    print(f"Error procesando fila en {url}: {e}")

    return pd.DataFrame(todas)

def actualizar_metadata(ruta_csv: str, ruta_salida: str) -> pd.DataFrame:
    df = obtener_series_desde_links(ruta_csv)
    df.to_csv(ruta_salida, index=False, encoding="utf-8-sig")
    return df

# Ejemplo de uso:
# df = actualizar_metadata("links_bcrp.csv", "series_bcrp_metadata.csv")
# print(df.head())
