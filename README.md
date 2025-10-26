# 🦷 dentIAnews

Un repositorio que recopila automáticamente noticias en inglés sobre Inteligencia Artificial aplicada a la odontología.

## ¿Cómo funciona?

Este proyecto utiliza un *workflow* de **GitHub Actions** que se ejecuta cada hora para:

1.  Consultar la API de [NewsAPI](https://newsapi.org/) en busca de artículos recientes sobre "AI in Dentistry".
2.  Compilar los resultados.
3.  Crear o actualizar un archivo Markdown (`.md`) para el día actual con todas las noticias encontradas.

## ¿Dónde están las noticias?

Puedes encontrar todos los artículos recopilados, organizados por fecha, dentro de la carpeta `/noticias`.