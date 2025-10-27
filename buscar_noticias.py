import requests
import os
import datetime
from deep_translator import GoogleTranslator
import re

# --- Configuración ---
API_KEY = os.environ.get('NEWS_API_KEY')
LANGUAGE = 'en'
OUTPUT_DIR_EN = "noticias_en"
OUTPUT_DIR_ES = "noticias_es"

# Consultas MÁS ESPECÍFICAS para IA en odontología
QUERIES = [
    '"AI in dentistry" OR "artificial intelligence in dentistry" OR "machine learning in dentistry"',
    '"dental AI" OR "AI dental" OR "dental artificial intelligence"',
    '("AI" OR "artificial intelligence" OR "machine learning") AND ("dental imaging" OR "dental diagnosis" OR "oral health AI")',
    '("deep learning" OR "computer vision") AND ("dentistry" OR "dental" OR "odontology")'
]

# Términos que DEBEN aparecer para considerar relevante
REQUIRED_KEYWORDS = [
    'ai', 'artificial intelligence', 'machine learning', 'deep learning',
    'computer vision', 'neural network', 'algorithm'
]

# Términos dentales que deben aparecer
DENTAL_KEYWORDS = [
    'dental', 'dentistry', 'dentist', 'odontology', 'oral health',
    'tooth', 'teeth', 'cavity', 'caries', 'periodontal', 'orthodont',
    'endodont', 'prosthodont', 'implant', 'denture'
]

def es_noticia_relevante(titulo, descripcion):
    """Filtra noticias realmente relevantes a IA en odontología"""
    texto = f"{titulo} {descripcion}".lower()
    
    # Debe contener al menos un término de IA Y un término dental
    tiene_ia = any(termino in texto for termino in REQUIRED_KEYWORDS)
    tiene_dental = any(termino in texto for termino in DENTAL_KEYWORDS)
    
    return tiene_ia and tiene_dental

def traducir_texto(texto):
    """Traduce texto con manejo de errores mejorado"""
    if not texto or texto == 'Untitled':
        return texto
    
    try:
        return GoogleTranslator(source='en', target='es').translate(texto)
    except Exception as e:
        print(f"⚠️ Error en traducción: {e}")
        return texto

def fetch_news():
    if not API_KEY:
        print("❌ No se encontró la variable de entorno NEWS_API_KEY.")
        return

    today = datetime.date.today()
    today_str = today.strftime('%Y-%m-%d')
    search_from = today - datetime.timedelta(days=3)  # Reducir a 3 días para más relevancia
    search_from_str = search_from.strftime('%Y-%m-%d')

    # Crear carpetas de forma más robusta
    try:
        os.makedirs(OUTPUT_DIR_EN, exist_ok=True)
        os.makedirs(OUTPUT_DIR_ES, exist_ok=True)
        print(f"✅ Carpetas creadas: {OUTPUT_DIR_EN}, {OUTPUT_DIR_ES}")
    except Exception as e:
        print(f"❌ Error creando carpetas: {e}")
        return

    filename_en = os.path.join(OUTPUT_DIR_EN, f"{today_str}.md")
    filename_es = os.path.join(OUTPUT_DIR_ES, f"{today_str}.md")

    all_articles = []

    # Buscar por bloques
    for i, query in enumerate(QUERIES, start=1):
        print(f"\n🔍 Búsqueda {i}/{len(QUERIES)}: {query}")

        # Codificar query para URL
        encoded_query = requests.utils.quote(query)
        
        url = (
            f'https://newsapi.org/v2/everything?'
            f'q={encoded_query}&'
            f'language={LANGUAGE}&'
            f'from={search_from_str}&'
            f'sortBy=publishedAt&'
            f'pageSize=50&'
            f'apiKey={API_KEY}'
        )

        try:
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            if data.get('status') != 'ok':
                print(f"   ⚠️ Error en API: {data.get('message', 'Unknown error')}")
                continue
                
            articles = data.get('articles', [])
            print(f"   ➜ {len(articles)} artículos encontrados antes de filtrar.")
            
            # FILTRAR noticias relevantes
            relevant_articles = []
            for article in articles:
                title = article.get('title', '')
                description = article.get('description', '')
                
                if es_noticia_relevante(title, description):
                    relevant_articles.append(article)
                else:
                    print(f"   ➜ Descartado: {title[:60]}...")
            
            print(f"   ✅ {len(relevant_articles)} artículos relevantes después de filtrar.")
            all_articles.extend(relevant_articles)
            
        except requests.exceptions.RequestException as e:
            print(f"   ❌ Error en búsqueda {i}: {e}")
        except Exception as e:
            print(f"   ❌ Error inesperado en búsqueda {i}: {e}")

    # Eliminar duplicados por URL
    unique_articles = {a['url']: a for a in all_articles if a.get('url')}.values()
    print(f"\n📊 Resumen final:")
    print(f"   ➜ Total artículos únicos y relevantes: {len(unique_articles)}")

    # Escribir archivos
    try:
        with open(filename_en, 'w', encoding='utf-8') as f_en, \
             open(filename_es, 'w', encoding='utf-8') as f_es:

            # Encabezados
            f_en.write(f"# AI in Dentistry News ({today_str})\n\n")
            f_es.write(f"# Noticias sobre IA en Odontología ({today_str})\n\n")

            if not unique_articles:
                f_en.write("No relevant AI dentistry news found in the last 3 days.\n")
                f_es.write("No se encontraron noticias relevantes sobre IA en odontología en los últimos 3 días.\n")
                print("📝 Archivos creados con mensaje 'no news found'")
            else:
                f_en.write(f"Total relevant articles found: {len(unique_articles)}\n\n")
                f_es.write(f"Total de artículos relevantes encontrados: {len(unique_articles)}\n\n")
                
                f_en.write("---\n\n")
                f_es.write("---\n\n")

                for i, article in enumerate(unique_articles, start=1):
                    title = article.get('title', 'Untitled').strip()
                    desc = article.get('description', '').strip()
                    url = article.get('url', '#')
                    source = article.get('source', {}).get('name', 'Unknown source')
                    published = article.get('publishedAt', '').replace('T', ' ').replace('Z', ' UTC')

                    # Traducir
                    title_es = traducir_texto(title)
                    desc_es = traducir_texto(desc) if desc else ""

                    # Inglés
                    f_en.write(f"## {i}. [{title}]({url})\n")
                    f_en.write(f"- **Source:** {source}\n")
                    f_en.write(f"- **Published:** {published}\n")
                    if desc:
                        f_en.write(f"- **Description:** {desc}\n")
                    f_en.write("\n---\n\n")

                    # Español
                    f_es.write(f"## {i}. [{title_es}]({url})\n")
                    f_es.write(f"- **Fuente:** {source}\n")
                    f_es.write(f"- **Publicado:** {published}\n")
                    if desc_es:
                        f_es.write(f"- **Descripción:** {desc_es}\n")
                    f_es.write("\n---\n\n")

                print(f"📂 Archivos creados exitosamente:")
                print(f"   - {filename_en}")
                print(f"   - {filename_es}")

    except Exception as e:
        print(f"❌ Error escribiendo archivos: {e}")

if __name__ == "__main__":
    fetch_news()
