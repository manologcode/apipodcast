# crud.py
from typing import Optional
from sqlalchemy.orm import Session
import models
import schemas
from datetime import datetime
import uuid # Para generar GUIDs

# --- Funciones para Podcasts ---

def get_podcast(db: Session, podcast_id: int):
    return db.query(models.Podcast).filter(models.Podcast.id == podcast_id).first()

def get_podcast_by_slug(db: Session, slug: str):
     return db.query(models.Podcast).filter(models.Podcast.feed_url_slug == slug).first()

def get_podcasts(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Podcast).offset(skip).limit(limit).all()

def create_podcast(db: Session, podcast: schemas.PodcastCreate, image_url: Optional[str] = None):
    db_podcast = models.Podcast(
        title=podcast.title,
        description=podcast.description,
        author=podcast.author,
        language=podcast.language,
        category=podcast.category,
        feed_url_slug=podcast.feed_url_slug,
        image_url=image_url # Guardamos la ruta de la imagen subida
    )
    db.add(db_podcast)
    db.commit()
    db.refresh(db_podcast)
    return db_podcast

def update_podcast(db: Session, podcast_id: int, podcast: schemas.PodcastUpdate, image_url: Optional[str] = None):
    db_podcast = get_podcast(db, podcast_id)
    if db_podcast:
        update_data = podcast.model_dump(exclude_unset=True)
        if image_url is not None:
            update_data['image_url'] = image_url

        for key, value in update_data.items():
            setattr(db_podcast, key, value)

        db.add(db_podcast)
        db.commit()
        db.refresh(db_podcast)
    return db_podcast

def delete_podcast(db: Session, podcast_id: int):
    db_podcast = get_podcast(db, podcast_id)
    if db_podcast:
        db.delete(db_podcast)
        db.commit()
    return db_podcast

# --- Funciones para Episodios ---

def get_episode(db: Session, episode_id: int):
    return db.query(models.Episode).filter(models.Episode.id == episode_id).first()

def get_episodes_for_podcast(db: Session, podcast_id: int, skip: int = 0, limit: int = 100):
    return db.query(models.Episode).filter(models.Episode.podcast_id == podcast_id).offset(skip).limit(limit).all()

def create_episode(
    db: Session,
    episode: schemas.EpisodeCreate,
    podcast_id: int,
    audio_url: str, # Ruta del archivo de audio
    audio_length: int, # Tamaño del archivo
    audio_type: str, # Tipo MIME
    duration: Optional[str] = None, # Duración opcional
    image_url: Optional[str] = None # Add image_url parameter
):
    # Generar un GUID único para el episodio
    guid = str(uuid.uuid4())

    db_episode = models.Episode(
        **episode.model_dump(), # Desempaquetar los campos del esquema
        podcast_id=podcast_id,
        audio_url=audio_url,
        audio_length=audio_length,
        audio_type=audio_type,
        duration=duration,
        pub_date=datetime.utcnow(), # Usar la fecha actual como fecha de publicación
        guid=guid,
        image_url=image_url # Save the image URL
    )
    db.add(db_episode)
    db.commit()
    db.refresh(db_episode)
    return db_episode

def update_episode(db: Session, episode_id: int, episode: schemas.EpisodeUpdate, audio_url: Optional[str] = None, audio_length: Optional[int] = None, audio_type: Optional[str] = None):
    db_episode = get_episode(db, episode_id)
    if db_episode:
        update_data = episode.model_dump(exclude_unset=True)

        if audio_url is not None:
            update_data['audio_url'] = audio_url
        if audio_length is not None:
            update_data['audio_length'] = audio_length
        if audio_type is not None:
            update_data['audio_type'] = audio_type

        for key, value in update_data.items():
             # Evitar actualizar el GUID a menos que se especifique explícitamente y con cuidado
            if key == 'guid' and not update_data.get('guid'):
                 continue
            setattr(db_episode, key, value)

        db.add(db_episode)
        db.commit()
        db.refresh(db_episode)
    return db_episode

def delete_episode(db: Session, episode_id: int):
    db_episode = get_episode(db, episode_id)
    if db_episode:
        db.delete(db_episode)
        db.commit()
    return db_episode
