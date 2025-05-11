# schemas.py
from pydantic import BaseModel, HttpUrl
from typing import List, Optional
from datetime import datetime

# Esquemas Base
class EpisodeBase(BaseModel):
    title: str
    description: str
    # duration: Optional[str] # No se pide en el POST/PUT porque se asume que se puede calcular o es opcional
    # pub_date: Optional[datetime] # Se genera automáticamente

class PodcastBase(BaseModel):
    title: str
    description: str
    author: str
    language: str = "es"
    category: Optional[str] = None
    feed_url_slug: str # Un identificador único para la URL del feed (ej: 'mi-super-podcast')

# Esquemas para Creación
class EpisodeCreate(EpisodeBase):
    # Para la creación de episodio se sube el archivo de audio y la duración puede ser opcional
    pass # No se incluyen los campos de archivo aquí, se manejan por separado en el endpoint

class PodcastCreate(PodcastBase):
    # Para la creación de podcast se sube el archivo de imagen
    pass # No se incluye el campo de archivo aquí

# Esquemas para Actualización
class EpisodeUpdate(EpisodeBase):
    audio_url: Optional[str] = None
    audio_length: Optional[int] = None
    audio_type: Optional[str] = None
    duration: Optional[str] = None
    pub_date: Optional[datetime] = None
    guid: Optional[str] = None

class PodcastUpdate(PodcastBase):
    image_url: Optional[str] = None
    feed_url_slug: Optional[str] = None # Podría actualizarse, pero con cuidado si ya se ha distribuido el feed

# Esquemas de Respuesta (lo que la API devuelve)
class Episode(EpisodeBase):
    id: int
    podcast_id: int
    audio_url: str
    audio_length: int
    audio_type: str
    duration: Optional[str]
    pub_date: datetime
    guid: str

    class Config:
        orm_mode = True # Permite leer datos directamente de un modelo SQLAlchemy

class Podcast(PodcastBase):
    id: int
    image_url: Optional[str]
    feed_url_slug: str
    episodes: List[Episode] = [] # Incluir una lista de episodios en la respuesta del podcast

    class Config:
        orm_mode = True