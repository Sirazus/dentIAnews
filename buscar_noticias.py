import requests
import os
import datetime
from deep_translator import GoogleTranslator
import time

# --- Configuración ---
API_KEY = os.environ.get('NEWS_API_KEY')
OUTPUT_DIR_EN = "noticias_en"
OUTPUT_DIR_ES = "noticias_es"

# Consultas mejoradas para IA en odontología
QUERIES = [
    '("AI" OR "artificial intelligence" OR "machine learning") AND ("dentistry" OR "dental" OR "tooth" OR "teeth" OR "oral health")',
    '"dental AI" OR "AI dentistry" OR "smart dentistry" OR "digital dentistry"',
    '("deep learning" OR "computer vision") AND ("dental imaging" OR "dental diagnosis" OR "dental care")',
    '"dental technology" OR "dental innovation" OR "dental software" AND AI'
]

def es_noticia_relevante(titulo, descripcion):
    """Filtro para noticias realmente relevantes"""
    if not titulo or not descripcion:
        return False
        
    texto = f"{titulo} {descripcion}".lower()
    
    # Términos de IA
    terminos_ia = ['ai', 'artificial intelligence', 'machine learning', 'deep learning', 
                   'computer vision', 'neural network', 'algorithm', 'intelligent']
    
    # Términos dentales
    terminos_dental = ['dental', 'dentistry', 'dentist', 'tooth', 'teeth', 'oral', 
                       'cavity', 'implant', 'orthodont', 'periodontal', 'denture', 'gingival',
                       'endodont', 'prosthodont', 'odontology']
    
    tiene_ia = any(termino in texto for termino in terminos_ia)
    tiene_dental = any(termino in texto for termino in terminos_dental)
    
    if tiene_ia and tiene_dental:
        return True
    
    return False

def traducir_texto(texto):
    """Traduce con manejo mejorado de errores"""
    if not texto or len(texto.strip()) < 5:
        return texto
        
    try:
        texto_limitado = texto[:490]
        traducido = GoogleTranslator(source='en', target='es').translate(texto_limitado)
        return traducido if traducido else texto
    except Exception as e:
        print(f"⚠️ Error traduciendo: {e}")
        return texto

def buscar_noticias_reales():
    """Busca noticias reales usando NewsAPI"""
    if not API_KEY:
        print("❌ No se encontró NEWS_API_KEY")
        return []
    
    today = datetime.date.today()
    search_from = today - datetime.timedelta(days=7)
    search_from_str = search_from.strftime('%Y-%m-%d')
    
    all_articles = []
    
    for i, query in enumerate(QUERIES, 1):
        print(f"🔍 Búsqueda {i}/{len(QUERIES)}: {query[:80]}...")
        
        try:
            encoded_query = requests.utils.quote(query)
            url = f'https://newsapi.org/v2/everything?q={encoded_query}&language=en&from={search_from_str}&sortBy=publishedAt&pageSize=20&apiKey={API_KEY}'
            
            response = requests.get(url, timeout=30)
            data = response.json()
            
            if data.get('status') != 'ok':
                continue
                
            articles = data.get('articles', [])
            print(f"   📰 {len(articles)} artículos encontrados")
            
            relevant_count = 0
            for article in articles:
                title = article.get('title', '')
                desc = article.get('description', '')
                
                if es_noticia_relevante(title, desc):
                    all_articles.append(article)
                    relevant_count += 1
                    print(f"   ✅ {title[:60]}...")
            
            print(f"   ✅ {relevant_count} artículos relevantes")
            
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    # Eliminar duplicados
    unique_articles = []
    seen_urls = set()
    
    for article in all_articles:
        url = article.get('url')
        if url and url not in seen_urls:
            seen_urls.add(url)
            unique_articles.append(article)
    
    return unique_articles

def crear_archivos_noticias():
    """Crea los archivos de noticias"""
    
    # Crear carpetas
    print("🔧 CREANDO CARPETAS...")
    try:
        os.makedirs(OUTPUT_DIR_EN, exist_ok=True)
        os.makedirs(OUTPUT_DIR_ES, exist_ok=True)
        print(f"✅ Carpetas creadas: {OUTPUT_DIR_EN}, {OUTPUT_DIR_ES}")
    except Exception as e:
        print(f"❌ ERROR creando carpetas: {e}")
        return False

    # Fecha actual
    today = datetime.date.today()
    today_str = today.strftime('%Y-%m-%d')
    timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    # Rutas de archivos
    archivo_en = os.path.join(OUTPUT_DIR_EN, f"{today_str}.md")
    archivo_es = os.path.join(OUTPUT_DIR_ES, f"{today_str}.md")
    
    print(f"📄 Archivos a crear:")
    print(f"   - {archivo_en}")
    print(f"   - {archivo_es}")

    # Buscar noticias reales
    print("\n🎯 BUSCANDO NOTICIAS REALES...")
    noticias = buscar_noticias_reales()
    
    print(f"\n📊 RESULTADOS: {len(noticias)} noticias relevantes encontradas")

    # Generar contenido
    timestamp_unique = f"{timestamp} - Build {int(time.time())}"
    
    try:
        print("✍️ ESCRIBIENDO ARCHIVOS...")
        
        with open(archivo_en, 'w', encoding='utf-8') as f_en:
            f_en.write(f"# AI in Dentistry News ({today_str})\n\n")
            f_en.write(f"**Last Update:** {timestamp_unique}\n\n")
            
            if not noticias:
                f_en.write("## No AI Dentistry News Found\n\n")
                f_en.write("No relevant artificial intelligence news in dentistry were found in the last 7 days.\n\n")
                f_en.write("### Search Criteria:\n")
                f_en.write("- AI, Artificial Intelligence, Machine Learning\n")
                f_en.write("- Dentistry, Dental, Oral Health\n")
                f_en.write("- Combined relevance filter applied\n")
            else:
                f_en.write(f"## Found {len(noticias)} Relevant Articles\n\n")
                f_en.write("---\n\n")
                
                for i, article in enumerate(noticias, 1):
                    title = article.get('title', 'No title').strip()
                    desc = article.get('description', '').strip()
                    url = article.get('url', '#')
                    source = article.get('source', {}).get('name', 'Unknown')
                    published = article.get('publishedAt', '').replace('T', ' ').replace('Z', ' UTC')
                    
                    f_en.write(f"### {i}. [{title}]({url})\n")
                    f_en.write(f"- **Source:** {source}\n")
                    f_en.write(f"- **Published:** {published}\n")
                    if desc:
                        f_en.write(f"- **Summary:** {desc}\n")
                    f_en.write("\n---\n\n")
        
        print(f"✅ ARCHIVO INGLÉS ESCRITO: {archivo_en}")
        
        with open(archivo_es, 'w', encoding='utf-8') as f_es:
            f_es.write(f"# Noticias sobre IA en Odontología ({today_str})\n\n")
            f_es.write(f"**Última actualización:** {timestamp_unique}\n\n")
            
            if not noticias:
                f_es.write("## No Se Encontraron Noticias de IA en Odontología\n\n")
                f_es.write("No se encontraron noticias relevantes sobre inteligencia artificial en odontología en los últimos 7 días.\n\n")
                f_es.write("### Criterios de Búsqueda:\n")
                f_es.write("- IA, Inteligencia Artificial, Aprendizaje Automático\n")
                f_es.write("- Odontología, Dental, Salud Oral\n")
                f_es.write("- Filtro de relevancia combinada aplicado\n")
            else:
                f_es.write(f"## Se Encontraron {len(noticias)} Artículos Relevantes\n\n")
                f_es.write("---\n\n")
                
                for i, article in enumerate(noticias, 1):
                    title = article.get('title', 'Sin título').strip()
                    desc = article.get('description', '').strip()
                    url = article.get('url', '#')
                    source = article.get('source', {}).get('name', 'Desconocida')
                    published = article.get('publishedAt', '').replace('T', ' ').replace('Z', ' UTC')
                    
                    # Traducir
                    title_es = traducir_texto(title)
                    desc_es = traducir_texto(desc) if desc else ""
                    
                    f_es.write(f"### {i}. [{title_es}]({url})\n")
                    f_es.write(f"- **Fuente:** {source}\n")
                    f_es.write(f"- **Publicado:** {published}\n")
                    if desc_es:
                        f_es.write(f"- **Resumen:** {desc_es}\n")
                    f_es.write("\n---\n\n")
        
        print(f"✅ ARCHIVO ESPAÑOL ESCRITO: {archivo_es}")
        
        # VERIFICACIÓN FINAL
        if os.path.exists(archivo_en) and os.path.exists(archivo_es):
            tamaño_en = os.path.getsize(archivo_en)
            tamaño_es = os.path.getsize(archivo_es)
            print(f"🎉 VERIFICACIÓN EXITOSA:")
            print(f"   📁 {archivo_en} - {tamaño_en} bytes")
            print(f"   📁 {archivo_es} - {tamaño_es} bytes")
            return True
        else:
            print("❌ ERROR: Los archivos no se crearon correctamente")
            return False
            
    except Exception as e:
        print(f"❌ ERROR escribiendo archivos: {e}")
        return False

if __name__ == "__main__":
    print("🚀 INICIANDO BÚSQUEDA DE NOTICIAS...")
    print(f"📂 Directorio actual: {os.getcwd()}")
    
    success = crear_archivos_noticias()
    
    if success:
        print("\n🎉 ¡BÚSQUEDA COMPLETADA EXITOSAMENTE!")
    else:
        print("\n💥 BÚSQUEDA COMPLETADA CON ERRORES")
