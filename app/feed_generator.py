# feed_generator.py
import xml.etree.ElementTree as ET
from typing import List
import models
from datetime import datetime
from email.utils import formatdate # Para formatear la fecha en RFC 2822 (compatible con RFC 822)


def generate_rss_feed(podcast: models.Podcast, episodes: List[models.Episode], base_url: str):
    # Crear el elemento raíz <rss> con namespaces
    rss = ET.Element("rss",
                     version="2.0",
                     attrib={"xmlns:itunes": "http://www.itunes.com/dtds/podcast-1.0.dtd",
                             "xmlns:content": "http://purl.org/rss/1.0/modules/content/"})

    # Crear el elemento <channel>
    channel = ET.SubElement(rss, "channel")

    # Información del Podcast (channel)
    ET.SubElement(channel, "title").text = podcast.title
    # La URL del link debe ser la URL del sitio web asociado al podcast,
    # no necesariamente la del feed. Usamos la base_url por simplicidad.
    ET.SubElement(channel, "link").text = f"{base_url}/{podcast.feed_url_slug}"
    ET.SubElement(channel, "description").text = podcast.description
    ET.SubElement(channel, "language").text = podcast.language
    ET.SubElement(channel, "lastBuildDate").text = formatdate(usegmt=True)

    # Tags específicos de iTunes para el Canal
    ET.SubElement(channel, "{http://www.itunes.com/dtds/podcast-1.0.dtd}author").text = podcast.author
    if podcast.category:
         # Puedes necesitar tags <itunes:category> anidados para subcategorías
        ET.SubElement(channel, "{http://www.itunes.com/dtds/podcast-1.0.dtd}category", text=podcast.category)
    if podcast.image_url:
        full_image_url = f"{base_url}/static/files/{podcast.image_url.split('/')[-1]}" # Asumimos que image_url es una ruta relativa dentro de static/files
        ET.SubElement(channel, "{http://www.itunes.com/dtds/podcast-1.0.dtd}image", href=full_image_url)
        # También puedes incluir una etiqueta <image> estándar de RSS si lo deseas
        # img = ET.SubElement(channel, "image")
        # ET.SubElement(img, "url").text = full_image_url
        # ET.SubElement(img, "title").text = podcast.title
        # ET.SubElement(img, "link").text = base_url # Enlaces a la página del podcast

    # Añadir episodios (items)
    for episode in episodes:
        item = ET.SubElement(channel, "item")
        ET.SubElement(item, "title").text = episode.title
        ET.SubElement(item, "description").text = episode.description # Puede ser HTML si usas CDATA y content:encoded
        ET.SubElement(item, "pubDate").text = formatdate(episode.pub_date.timestamp(), usegmt=True)

        # Tag <enclosure> es crucial para podcasts
        full_audio_url = f"{base_url}/static/files/{episode.audio_url.split('/')[-1]}" # Asumimos que audio_url es una ruta relativa dentro de static/files
        ET.SubElement(item, "enclosure",
                     url=full_audio_url,
                     length=str(episode.audio_length),
                     type=episode.audio_type)

        # GUID (Global Unique Identifier) - debe ser único para cada episodio
        # Usar la URL del audio es común, pero usar un ID o UUID es más seguro si la URL cambia
        ET.SubElement(item, "guid").text = episode.guid # Usamos el guid guardado en DB

        # Tags específicos de iTunes para el Item
        ET.SubElement(item, "{http://www.itunes.com/dtds/podcast-1.0.dtd}author").text = podcast.author # O el autor del episodio si es diferente
        if episode.duration:
             ET.SubElement(item, "{http://www.itunes.com/dtds/podcast-1.0.dtd}duration").text = episode.duration # Formato HH:MM:SS o segundos

        # Puedes añadir <content:encoded> si tu descripción tiene HTML/formato
        # content_encoded = ET.SubElement(item, "{http://purl.org/rss/1.0/modules/content/}encoded")
        # content_encoded.text = f"<![CDATA[{episode.description}]]>"


    # Convertir el árbol XML a una cadena con formato (opcional, pero útil para legibilidad)
    # ET.indent(rss, space="  ") # Requiere Python 3.9+
    xml_string = ET.tostring(rss, encoding='utf-8', xml_declaration=True).decode('utf-8')

    # Alternativa para indentación en versiones < 3.9 o si no funciona:
    # import minidom
    # dom = minidom.parseString(ET.tostring(rss))
    # xml_string = dom.toprettyxml(indent="  ")


    return xml_string
