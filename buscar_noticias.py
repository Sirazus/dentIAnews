import requests
import os
import datetime
from deep_translator import GoogleTranslator
import time

# --- Configuración ---
API_KEY = os.environ.get('NEWS_API_KEY')
OUTPUT_DIR_EN = "noticias_en"
OUTPUT_DIR_ES = "noticias_es"

def crear_archivos_de_ejemplo():
    """Crea archivos de ejemplo para forzar que se suban al repositorio"""
    
    # Crear carpetas de forma ABSOLUTAMENTE robusta
    print("🔧 CREANDO CARPETAS...")
    try:
        os.makedirs(OUTPUT_DIR_EN, exist_ok=True)
        os.makedirs(OUTPUT_DIR_ES, exist_ok=True)
        print(f"✅ Carpetas creadas: {OUTPUT_DIR_EN}, {OUTPUT_DIR_ES}")
        
        # Verificar que existen
        if not os.path.exists(OUTPUT_DIR_EN):
            print(f"❌ ERROR: {OUTPUT_DIR_EN} no se pudo crear")
            return False
        if not os.path.exists(OUTPUT_DIR_ES):
            print(f"❌ ERROR: {OUTPUT_DIR_ES} no se pudo crear") 
            return False
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

    # CONTENIDO DE EJEMPLO (siempre único)
    contenido_en = f"""# AI in Dentistry News ({today_str})

**Last Update:** {timestamp}
**Build ID:** {int(time.time())}

## Currently Testing File Creation

This is a test file to verify that the GitHub Actions workflow is correctly creating and committing files.

### Next Steps:
1. Verify this file appears in the repository
2. Check if noticias_es/ folder is created
3. Ensure both files are committed

---
*This is an automated test message*
"""

    contenido_es = f"""# Noticias sobre IA en Odontología ({today_str})

**Última actualización:** {timestamp}
**ID de ejecución:** {int(time.time())}

## Actualmente probando creación de archivos

Este es un archivo de prueba para verificar que el workflow de GitHub Actions está creando y confirmando archivos correctamente.

### Próximos pasos:
1. Verificar que este archivo aparezca en el repositorio
2. Comprobar si la carpeta noticias_es/ se creó
3. Asegurar que ambos archivos se confirmen

---
*Este es un mensaje automatizado de prueba*
"""

    # ESCRIBIR ARCHIVOS
    try:
        print("✍️ ESCRIBIENDO ARCHIVOS...")
        
        with open(archivo_en, 'w', encoding='utf-8') as f:
            f.write(contenido_en)
        print(f"✅ ARCHIVO INGLÉS ESCRITO: {archivo_en}")
        
        with open(archivo_es, 'w', encoding='utf-8') as f:
            f.write(contenido_es)
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
    print("🚀 INICIANDO SCRIPT DE PRUEBA...")
    print(f"📂 Directorio actual: {os.getcwd()}")
    print(f"📁 Contenido actual: {os.listdir('.')}")
    
    success = crear_archivos_de_ejemplo()
    
    if success:
        print("\n🎉 ¡SCRIPT COMPLETADO EXITOSAMENTE!")
        print("📤 Los archivos deberían aparecer en el próximo commit")
    else:
        print("\n💥 SCRIPT FALLÓ")
