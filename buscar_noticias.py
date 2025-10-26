import requests
import os
import datetime

# --- Configuración ---

# QUERY MEJORADA:
# Busca la frase exacta "AI in dentistry" O
# (la palabra "AI" o "Artificial Intelligence") Y (la palabra "dentistry" o "dental")
QUERY = '"AI in dentistry" OR (("Artificial Intelligence" OR AI) AND (dentistry OR dental))'

# Idioma de las noticias
LANGUAGE = 'en'
# Clave API (la toma del Secret de GitHub)
API_KEY = os.environ.get('NEWS_API_KEY')
# Carpeta donde se guardarán las noticias
OUTPUT_DIR = "noticias"
# ---------------------

def fetch_news():
    """
    Busca noticias de los últimos 2 días y las guarda en un archivo .md con la fecha de HOY.
    """
    if not API_KEY:
        print("Error: No se encontró la variable de entorno NEWS_API_KEY.")
        return

    # 1. Obtener la fecha de hoy (para el nombre del archivo)
    today = datetime.date.today()
    today_str = today.strftime('%Y-%m-%d')

    # 2. MEJORA: Obtener la fecha de hace 2 días (para la búsqueda en la API)
    # Esto da margen a que NewsAPI indexe los artículos.
    search_from_date = today - datetime.timedelta(days=2)
    search_from_str = search_from_date.strftime('%Y-%m-%d')

    # 3. Definir el nombre del archivo de salida (sigue usando la fecha de hoy)
    filename = os.path.join(OUTPUT_DIR, f"{today_str}.md")
    os.makedirs(OUTPUT_DIR, exist_ok=True) # Crea la carpeta 'noticias' si no existe

    # 4. Construir la URL para la API
    # 'from': usa la fecha de hace 2 días
    url = (
        f'https://newsapi.org/v2/everything?'
        f'q={QUERY}&'
        f'language={LANGUAGE}&'
        f'from={search_from_str}&' # <-- CAMBIO IMPORTANTE
        f'sortBy=publishedAt&'
        f'apiKey={API_KEY}'
    )

    print(f"Buscando artículos con consulta: {QUERY}")
    print(f"Buscando artículos desde: {search_from_str}")

    # 5. Hacer la petición a la API
    try:
        response = requests.get(url)
        response.raise_for_status() 
    except requests.exceptions.RequestException as e:
        print(f"Error al contactar la API: {e}")
        return

    data = response.json()
    articles = data.get('articles', [])

    if not articles:
        print(f"No se encontraron artículos nuevos para {today_str}.")
        # Escribimos en el archivo para confirmar que el script corrió
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(f"# Noticias sobre IA en Odontología ({today_str})\n\n")
            f.write("No se encontraron noticias en las últimas 48 horas.\n")
        return

    print(f"Se encontraron {len(articles)} artículos. Escribiendo en {filename}...")

    # 6. Formatear y escribir las noticias en el archivo Markdown
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(f"# Noticias sobre IA en Odontología ({today_str})\n\n")
        f.write(f"Resultados de las últimas 48 horas. Total: {len(articles)}\n\n")
        
        for article in articles:
            title = article.get('title', 'Sin título')
            url = article.get('url', '#')
            source = article.get('source', {}).get('name', 'Fuente desconocida')
            published_at = article.get('publishedAt', 'Fecha desconocida').replace("T", " ").replace("Z", " UTC")
            
            f.write(f"## [{title}]({url})\n")
            f.write(f"- **Fuente:** {source}\n")
            f.write(f"- **Publicado:** {published_at}\n\n")
            f.write("---\n\n")

    print(f"Archivo {filename} creado/actualizado exitosamente.")

if __name__ == "__main__":
    fetch_news()