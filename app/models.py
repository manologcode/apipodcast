# models.py
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship

from database import Base
from datetime import datetime

class Podcast(Base):
    __tablename__ = "podcasts"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(String)
    author = Column(String)
    image_url = Column(String, nullable=True) # Ruta local o URL de la imagen
    language = Column(String, default="es") # e.g., "en", "es"
    category = Column(String, nullable=True) # e.g., "Technology"
    feed_url_slug = Column(String, unique=True, index=True) # Slug para la URL del feed

    episodes = relationship("Episode", back_populates="podcast", cascade="all, delete-orphan")

class Episode(Base):
    __tablename__ = "episodes"

    id = Column(Integer, primary_key=True, index=True)
    podcast_id = Column(Integer, ForeignKey("podcasts.id"))
    title = Column(String, index=True)
    description = Column(String)
    audio_url = Column(String) # Ruta local o URL del archivo de audio
    audio_length = Column(Integer) # Tamaño del archivo en bytes
    audio_type = Column(String) # Tipo MIME del archivo (e.g., "audio/mpeg")
    duration = Column(String, nullable=True) # Duración del episodio (e.g., "HH:MM:SS")
    pub_date = Column(DateTime, default=datetime.utcnow) # Fecha de publicación
    image_url = Column(String, nullable=True) # Ruta local o URL de la imagen
    guid = Column(String, unique=True, index=True) # Identificador único para el episodio

    podcast = relationship("Podcast", back_populates="episodes")
