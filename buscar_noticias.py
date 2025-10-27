import requests
import os
import datetime
from deep_translator import GoogleTranslator

# --- Configuración ---
API_KEY = os.environ.get('NEWS_API_KEY')
LANGUAGE = 'en'
OUTPUT_DIR_EN = "noticias_en"
OUTPUT_DIR_ES = "noticias_es"

# Grupos de búsqueda (más manejables)
QUERIES = [
    '"AI in dentistry" OR "artificial intelligence in dentistry" OR "machine learning in dentistry"',
    '"deep learning in dentistry" OR "dental AI" OR "AI dental" OR "smart dentistry"',
    '("AI" OR "artificial intelligence") AND ("dentistry" OR "dental" OR "oral health")',
    '"Allisone" OR "Overjet" OR "Pearl" OR "VideaHealth" OR "Diagnocat" OR "Dental Monitoring"',
    '("digital dentistry" OR "dental imaging" OR "radiology" OR "endodontics" OR "orthodontics")'
]

DOMAINS = ",".join([
    "nature.com", "sciencedirect.com", "medicalxpress.com", "dental-tribune.com",
    "dentistrytoday.com", "dentaleconomics.com", "ai.googleblog.com",
    "techxplore.com", "ada.org", "drbicuspid.com", "mobihealthnews.com"
])

def traducir_texto(texto):
    try:
        return GoogleTranslator(source='en', target='es').translate(texto)
    except Exception:
        return texto

def fetch_news():
    if not API_KEY:
        print("❌ No se encontró la variable de entorno NEWS_API_KEY.")
        return

    today = datetime.date.today()
    today_str = today.strftime('%Y-%m-%d')
    search_from = today - datetime.timedelta(days=7)
    search_from_str = search_from.strftime('%Y-%m-%d')

    os.makedirs(OUTPUT_DIR_EN, exist_ok=True)
    os.makedirs(OUTPUT_DIR_ES, exist_ok=True)

    filename_en = os.path.join(OUTPUT_DIR_EN, f"{today_str}.md")
    filename_es = os.path.join(OUTPUT_DIR_ES, f"{today_str}.md")

    all_articles = []

    # Buscar por bloques
    for i, query in enumerate(QUERIES, start=1):
        print(f"\n🔍 Búsqueda {i}/{len(QUERIES)}: {query}")

        url = (
            f'https://newsapi.org/v2/everything?'
            f'q={query}&'
            f'language={LANGUAGE}&'
            f'from={search_from_str}&'
            f'sortBy=publishedAt&'
            f'domains={DOMAINS}&'
            f'pageSize=50&'
            f'apiKey={API_KEY}'
        )

        try:
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()
            articles = data.get('articles', [])
            print(f"   ➜ {len(articles)} artículos encontrados.")
            all_articles.extend(articles)
        except requests.exceptions.RequestException as e:
            print(f"   ⚠️ Error en búsqueda {i}: {e}")

    # Eliminar duplicados por URL
    unique_articles = {a['url']: a for a in all_articles}.values()
    print(f"\n✅ Total artículos únicos: {len(unique_articles)}")

    if not unique_articles:
        print("⚠️ No se encontraron artículos nuevos.")
        with open(filename_en, 'w', encoding='utf-8') as f_en, \
             open(filename_es, 'w', encoding='utf-8') as f_es:
            f_en.write(f"# AI in Dentistry News ({today_str})\n\nNo news found.\n")
            f_es.write(f"# Noticias sobre IA en Odontología ({today_str})\n\nNo se encontraron noticias.\n")
        return

    # Guardar en inglés y traducido
    with open(filename_en, 'w', encoding='utf-8') as f_en, \
         open(filename_es, 'w', encoding='utf-8') as f_es:

        f_en.write(f"# AI in Dentistry News ({today_str})\n\n")
        f_es.write(f"# Noticias sobre IA en Odontología ({today_str})\n\n")

        for i, article in enumerate(unique_articles, start=1):
            title = article.get('title', 'Untitled')
            desc = article.get('description', '')
            url = article.get('url', '#')
            source = article.get('source', {}).get('name', 'Unknown source')
            published = article.get('publishedAt', '').replace("T", " ").replace("Z", " UTC")

            title_es = traducir_texto(title)
            desc_es = traducir_texto(desc)

            # Inglés
            f_en.write(f"## {i}. [{title}]({url})\n")
            f_en.write(f"- **Source:** {source}\n")
            f_en.write(f"- **Published:** {published}\n\n{desc}\n\n---\n\n")

            # Español
            f_es.write(f"## {i}. [{title_es}]({url})\n")
            f_es.write(f"- **Fuente:** {source}\n")
            f_es.write(f"- **Publicado:** {published}\n\n{desc_es}\n\n---\n\n")

    print(f"\n📂 Archivos creados:\n- {filename_en}\n- {filename_es}")

if __name__ == "__main__":
    fetch_news()
