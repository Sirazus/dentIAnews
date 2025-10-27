import requests
import os
import datetime
from deep_translator import GoogleTranslator

# --- CONFIGURACIÓN ---
API_KEY = os.environ.get('NEWS_API_KEY')
OUTPUT_DIR = "noticias"
LANGUAGE = 'en'

# Búsqueda avanzada con sinónimos y términos relacionados
QUERY = (
    '"AI in dentistry" OR "artificial intelligence in dentistry" OR '
    '"machine learning in dentistry" OR "deep learning in dentistry" OR '
    '"dental AI" OR "AI dental" OR "smart dentistry" OR '
    '("AI" OR "artificial intelligence" OR "machine learning" OR "deep learning") AND '
    '("dentistry" OR "dental" OR "oral health" OR "endodontics" OR '
    '"radiology" OR "orthodontics" OR "periodontics" OR "prosthodontics" OR '
    '"oral surgery" OR "pediatric dentistry" OR "dental imaging" OR '
    '"dental x-ray" OR "caries detection" OR "oral cancer" OR "dental diagnosis" OR '
    '"treatment planning" OR "CAD/CAM dentistry" OR "digital dentistry" OR '
    '"teledentistry" OR "dental technology" OR "denttech") OR '
    '"Dental Monitoring" OR "VideaHealth" OR "Overjet" OR "Pearl" OR '
    '"Denti.AI" OR "DentalXAI" OR "DentalAI" OR "Orca AI" OR "Orisview" OR "Allisone" OR "Diagnocat" OR "DentIA" OR "Llamalitica"'
)

# Dominios especializados (filtra por fuentes de salud, ciencia y tecnología)
DOMAINS = (
    "nature.com,sciencedirect.com,medicalxpress.com,dental-tribune.com,"
    "dentistrytoday.com,dentaleconomics.com,ai.googleblog.com,techxplore.com,"
    "jds.nih.gov,ada.org,dtg-global.com,drbicuspid.com,gacetadental.com,"
    "mobihealthnews.com"
)


def translate_text(text, source='en', target='es'):
    """Traduce texto con deep-translator; si falla, devuelve el original."""
    try:
        return GoogleTranslator(source=source, target=target).translate(text)
    except Exception:
        return text


def fetch_news():
    if not API_KEY:
        print("❌ Error: No se encontró la variable de entorno NEWS_API_KEY.")
        return

    today = datetime.date.today()
    today_str = today.strftime('%Y-%m-%d')
    search_from = today - datetime.timedelta(days=5)
    search_from_str = search_from.strftime('%Y-%m-%d')

    # Carpetas de salida
    output_en = os.path.join(OUTPUT_DIR, f"{today_str}.md")
    output_es = os.path.join(OUTPUT_DIR, "es", f"{today_str}.md")
    os.makedirs(os.path.join(OUTPUT_DIR, "es"), exist_ok=True)

    # --- Construcción de la URL ---
    url = (
        f'https://newsapi.org/v2/everything?'
        f'q={QUERY}&'
        f'qInTitle=dentistry&'
        f'language={LANGUAGE}&'
        f'domains={DOMAINS}&'
        f'from={search_from_str}&'
        f'sortBy=publishedAt&'
        f'pageSize=50&'
        f'apiKey={API_KEY}'
    )

    print(f"🔎 Buscando artículos con consulta:\n{QUERY}\n")
    print(f"🕒 Desde: {search_from_str}")

    try:
        response = requests.get(url)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"❌ Error al contactar la API: {e}")
        return

    data = response.json()
    articles = data.get('articles', [])

    if not articles:
        print(f"⚠️ No se encontraron artículos nuevos para {today_str}.")
        with open(output_en, 'w', encoding='utf-8') as f:
            f.write(f"# Noticias sobre IA en Odontología ({today_str})\n\n")
            f.write("No se encontraron noticias en los últimos 5 días.\n")
        with open(output_es, 'w', encoding='utf-8') as f:
            f.write(f"# Noticias sobre IA en Odontología ({today_str})\n\n")
            f.write("No se encontraron noticias en los últimos 5 días.\n")
        return

    # --- Filtrar duplicados y no relevantes ---
    seen_titles = set()
    filtered = []

    for article in articles:
        title = article.get('title', '').strip()
        if not title or title.lower() in seen_titles:
            continue
        seen_titles.add(title.lower())

        if 'AI' not in title and 'artificial' not in title.lower():
            continue

        filtered.append(article)

    print(f"✅ Se encontraron {len(filtered)} artículos relevantes.")
    print(f"📁 Guardando resultados en inglés y traducidos al español...")

    # --- Escribir versión en inglés ---
    with open(output_en, 'w', encoding='utf-8') as f:
        f.write(f"# 🦷 AI in Dentistry News ({today_str})\n\n")
        f.write(f"Results from the last 5 days. Total: {len(filtered)}\n\n")

        for article in filtered:
            title = article.get('title', 'Untitled')
            url = article.get('url', '#')
            source = article.get('source', {}).get('name', 'Unknown source')
            published_at = article.get('publishedAt', 'Unknown date').replace("T", " ").replace("Z", " UTC")

            f.write(f"## [{title}]({url})\n")
            f.write(f"- **Source:** {source}\n")
            f.write(f"- **Published:** {published_at}\n\n")
            f.write("---\n\n")

    # --- Escribir versión traducida ---
    with open(output_es, 'w', encoding='utf-8') as f:
        f.write(f"# 🦷 Noticias sobre IA en Odontología ({today_str})\n\n")
        f.write(f"Resultados de los últimos 5 días (traducción automática). Total: {len(filtered)}\n\n")

        for article in filtered:
            title = article.get('title', 'Sin título')
            title_es = translate_text(title)
            url = article.get('url', '#')
            source = article.get('source', {}).get('name', 'Fuente desconocida')
            published_at = article.get('publishedAt', 'Fecha desconocida').replace("T", " ").replace("Z", " UTC")

            f.write(f"## [{title_es}]({url})\n")
            f.write(f"- **Fuente:** {source}\n")
            f.write(f"- **Publicado:** {published_at}\n\n")
            f.write("---\n\n")

    print(f"✅ Archivos generados correctamente:\n- 🇬🇧 {output_en}\n- 🇪🇸 {output_es}")


if __name__ == "__main__":
    fetch_news()
