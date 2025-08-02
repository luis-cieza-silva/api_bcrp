# API BCRP

## Descripción

Este proyecto permite acceder y visualizar información de las series estadísticas del **Banco Central de Reserva del Perú (BCRP)** a través de la API pública de la entidad. Incluye una aplicación web interactiva desarrollada con **Streamlit** para consultar, visualizar y graficar series estadísticas de manera sencilla.

## Características

- Consulta de series estadísticas del BCRP por código, categoría y periodicidad.
- Selección múltiple de series y visualización conjunta.
- Visualización de metadatos relevantes de cada serie.
- Gráficos de líneas automáticos para las series seleccionadas.
- Actualización automática de la metadata desde la web del BCRP.
- Interfaz web amigable y personalizable.

## Instalación

1. Clona el repositorio:
    ```bash
    git clone https://github.com/luis-cieza-silva/api_bcrp.git
    cd api_bcrp
    ```

2. Instala las dependencias:
    ```bash
    pip install -r requirements.txt
    ```

## Uso

1. Ejecuta la aplicación Streamlit:
    ```bash
    streamlit run app.py
    ```

2. En la interfaz web:
    - Selecciona una categoría y una o más series estadísticas.
    - Ajusta los parámetros de consulta (códigos, año inicial, año final).
    - Haz clic en **Crear DataFrame** para ver los datos y el gráfico.
    - Si es la primera vez, presiona **Actualizar metadata** para descargar la metadata desde la web del BCRP.

## Estructura del Proyecto

```
api_bcrp/
│
├── app.py                  # Aplicación principal Streamlit
├── api_bcrp.py             # Función para consultar la API del BCRP
├── metadata.py             # Scraper y gestor de metadata de series
├── requirements.txt        # Dependencias del proyecto
├── master_categorias_urls.csv # URLs de categorías para scraping
├── metadata.csv            # Metadata generada de las series
├── README.md               # Este archivo
└── .gitignore              # Archivos y carpetas a ignorar por git
```

## Ejemplo de Consulta Múltiple

Puedes consultar varias series a la vez ingresando los códigos separados por guiones, por ejemplo:
```
PM04986AA-PM04989AA-PM04990AA
```
Solo asegúrate de que todas las series sean de la misma categoría y periodicidad.

## Recomendaciones

- No mezcles series de diferentes periodicidades en una misma consulta.
- Actualiza la metadata periódicamente para mantener la información al día.

## Licencia

Este proyecto se distribuye bajo la licencia MIT.

## Autor

Luis Cieza Silva  
[GitHub](https://github.com/luis-cieza-silva)
