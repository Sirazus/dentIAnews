import requests
import os
import datetime

# --- Configuración ---
# Tu tema de búsqueda
QUERY = '"IA en odontologia" OR "AI in dentistry" OR "inteligencia artificial en odontologia"'
# Idioma de las noticias
LANGUAGE = 'en'
# Clave API (la toma del Secret de GitHub)
API_KEY = os.environ.get('NEWS_API_KEY')
# Carpeta donde se guardarán las noticias
OUTPUT_DIR = "noticias"
# ---------------------

def fetch_news():
    """
    Busca noticias de HOY y las guarda en un archivo .md.
    """
    if not API_KEY:
        print("Error: No se encontró la variable de entorno NEWS_API_KEY.")
        return

    # 1. Obtener la fecha de hoy en formato YYYY-MM-DD
    today = datetime.date.today()
    today_str = today.strftime('%Y-%m-%d')

    # 2. Definir el nombre del archivo de salida
    filename = os.path.join(OUTPUT_DIR, f"{today_str}.md")
    os.makedirs(OUTPUT_DIR, exist_ok=True) # Crea la carpeta 'noticias' si no existe

    # 3. Construir la URL para la API
    # Buscamos en el endpoint 'everything'
    # 'q': la consulta
    # 'from': la fecha de hoy (para obtener solo las de hoy)
    # 'language': 'en'
    # 'sortBy': 'publishedAt' (las más nuevas primero)
    url = (
        f'https://newsapi.org/v2/everything?'
        f'q={QUERY}&'
        f'language={LANGUAGE}&'
        f'from={today_str}&'
        f'sortBy=publishedAt&'
        f'apiKey={API_KEY}'
    )

    # 4. Hacer la petición a la API
    try:
        response = requests.get(url)
        response.raise_for_status() # Lanza un error si la petición falla
    except requests.exceptions.RequestException as e:
        print(f"Error al contactar la API: {e}")
        return

    data = response.json()
    articles = data.get('articles', [])

    if not articles:
        print(f"No se encontraron artículos nuevos para {today_str}.")
        # Creamos un archivo vacío o con un mensaje
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(f"# Noticias sobre IA en Odontología ({today_str})\n\n")
            f.write("No se encontraron noticias hoy.\n")
        return

    print(f"Se encontraron {len(articles)} artículos. Escribiendo en {filename}...")

    # 5. Formatear y escribir las noticias en el archivo Markdown
    # 'w' sobrescribe el archivo cada vez. Esto asegura que el archivo
    # diario esté siempre actualizado con lo último encontrado ESE DÍA.
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(f"# Noticias sobre IA en Odontología ({today_str})\n\n")
        f.write(f"Total de artículos encontrados hoy: {len(articles)}\n\n")

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