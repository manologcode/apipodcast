# feed_generator.py
import xml.etree.ElementTree as ET
from typing import List
import models
from datetime import datetime
from email.utils import formatdate


def generate_rss_feed(podcast: models.Podcast, episodes: List[models.Episode], base_url: str):
    # Crear el elemento raíz <rss> con namespaces
    rss = ET.Element("rss",
                     version="2.0",
                     attrib={
                         "xmlns:itunes": "http://www.itunes.com/dtds/podcast-1.0.dtd",
                         "xmlns:content": "http://purl.org/rss/1.0/modules/content/"
                     })

    # Crear el elemento <channel>
    channel = ET.SubElement(rss, "channel")

    # Información del Podcast
    ET.SubElement(channel, "title").text = podcast.title
    ET.SubElement(channel, "link").text = f"{base_url}/{podcast.feed_url_slug}"
    ET.SubElement(channel, "description").text = podcast.description
    ET.SubElement(channel, "language").text = podcast.language
    ET.SubElement(channel, "lastBuildDate").text = formatdate(usegmt=True)

    # iTunes Tags del canal
    ET.SubElement(channel, "{http://www.itunes.com/dtds/podcast-1.0.dtd}author").text = podcast.author
    ET.SubElement(channel, "{http://www.itunes.com/dtds/podcast-1.0.dtd}explicit").text = "no"
    ET.SubElement(channel, "{http://www.itunes.com/dtds/podcast-1.0.dtd}summary").text = podcast.description
    ET.SubElement(channel, "{http://www.itunes.com/dtds/podcast-1.0.dtd}type").text = "episodic"

    if podcast.category:
        ET.SubElement(channel, "{http://www.itunes.com/dtds/podcast-1.0.dtd}category", attrib={"text": podcast.category})

    if podcast.image_url:
        full_image_url = f"{base_url}/static/files/{podcast.image_url.split('/')[-1]}"
        ET.SubElement(channel, "{http://www.itunes.com/dtds/podcast-1.0.dtd}image", attrib={"href": full_image_url})

        # (opcional) <image> estándar RSS
        img = ET.SubElement(channel, "image")
        ET.SubElement(img, "url").text = full_image_url
        ET.SubElement(img, "title").text = podcast.title
        ET.SubElement(img, "link").text = f"{base_url}/{podcast.feed_url_slug}"

    # Episodios
    for episode in episodes:
        item = ET.SubElement(channel, "item")
        ET.SubElement(item, "title").text = episode.title
        ET.SubElement(item, "description").text = episode.description
        ET.SubElement(item, "pubDate").text = formatdate(episode.pub_date.timestamp(), usegmt=True)

        full_audio_url = f"{base_url}/static/files/{episode.audio_url.split('/')[-1]}"
        ET.SubElement(item, "enclosure",
                      attrib={
                          "url": full_audio_url,
                          "length": str(episode.audio_length),
                          "type": episode.audio_type
                      })

        ET.SubElement(item, "guid").text = episode.guid

        # iTunes Tags del episodio
        ET.SubElement(item, "{http://www.itunes.com/dtds/podcast-1.0.dtd}author").text = podcast.author
        if episode.duration:
            ET.SubElement(item, "{http://www.itunes.com/dtds/podcast-1.0.dtd}duration").text = episode.duration

        # (opcional) contenido enriquecido con HTML
        # content_encoded = ET.SubElement(item, "{http://purl.org/rss/1.0/modules/content/}encoded")
        # content_encoded.text = f"<![CDATA[{episode.description}]]>"

    # Convertir a string XML
    xml_string = ET.tostring(rss, encoding='utf-8', xml_declaration=True).decode('utf-8')

    # Si usas Python < 3.9 y quieres que se vea más bonito (opcional):
    # import xml.dom.minidom
    # xml_string = xml.dom.minidom.parseString(xml_string).toprettyxml(indent="  ")

    return xml_string
