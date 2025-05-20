# main.py
import os
import shutil
from fastapi import FastAPI, Depends, HTTPException, UploadFile, File, Form, Request, Security
from fastapi.responses import Response, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials # Import security components
from sqlalchemy.orm import Session
from typing import List, Optional
from pathlib import Path
import mimetypes
import uuid # Import uuid for unique filenames
# from mutagen.mp3 import MP3 # Podrías usar esto para leer duración y otros tags
# from mutagen.id3 import ID3 # Para tags ID3

import crud
import models
import schemas
import database
import feed_generator
from audio_util import duration_mp3

# Directorios para guardar archivos subidos
# Asegúrate de que existan
BASE_DIR = Path(__file__).parent
STATIC_DIR = BASE_DIR / "static"
FILES_DIR = STATIC_DIR / "files"
TEMPLATES_DIR = BASE_DIR / "templates" # Define templates directory

# Crear directorios si no existen
for _dir in [STATIC_DIR, FILES_DIR, TEMPLATES_DIR]: # Include templates directory
    _dir.mkdir(parents=True, exist_ok=True)

# Configuración de la base URL (importante para generar URLs completas en el feed y API)
# Deberías cambiar esto a la URL pública de tu aplicación
BASE_URL = os.getenv("BASE_URL", "http://localhost:5002")
TITLE_PODCAST = os.getenv("TITLE_PODCAST", "Podcasts")
SUBTITLE_PODCAST = os.getenv("SUBTITLE_PODCAST", "Tus historias en voz")

# Configurar Jinja2Templates
templates = Jinja2Templates(directory=TEMPLATES_DIR)

# Define security scheme
security_scheme = HTTPBearer()

# Define token verification dependency
def verify_token(credentials: HTTPAuthorizationCredentials = Security(security_scheme)):
    """Verifies the provided token against the environment variable."""
    api_token = os.getenv("API_TOKEN")
    if not api_token:
        # This should ideally be checked at startup, but as a fallback:
        raise HTTPException(status_code=500, detail="API token not configured on the server.")
    if credentials.credentials != api_token:
        raise HTTPException(status_code=401, detail="Invalid or missing API token")
    return credentials.credentials # Return the token if valid


app = FastAPI(
    title="Podcast Manager API",
    description="API para gestionar podcasts y generar feeds RSS",
    version="1.0.0"
)

# Montar el directorio estático para servir archivos
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

# Crear las tablas en la base de datos al iniciar la aplicación
@app.on_event("startup")
def on_startup():
    models.Base.metadata.create_all(bind=database.engine)


# --- Funciones de Utilidad para Archivos ---

async def save_upload_file(upload_file: UploadFile, destination_dir: Path):
    """Guarda un archivo subido y devuelve la ruta relativa dentro de static/"""
    try:
        # Generar un nombre de archivo único
        file_extension = Path(upload_file.filename).suffix
        unique_filename = f"{uuid.uuid4()}{file_extension}"
        file_path = destination_dir / unique_filename
        # print(f"Saving file to: {file_path}") # Debug
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(upload_file.file, buffer)
        # Devolver la ruta relativa dentro del directorio estático para guardarla en DB
        relative_path = file_path.relative_to(STATIC_DIR)
        return str(relative_path)
    finally:
        await upload_file.close()

def get_file_size(relative_path: str):
    """Obtiene el tamaño de un archivo guardado en bytes"""
    full_path = STATIC_DIR / relative_path
    if full_path.exists():
        return full_path.stat().st_size
    return 0

def get_mime_type(relative_path: str):
    """Obtiene el tipo MIME de un archivo guardado"""
    full_path = STATIC_DIR / relative_path
    mime_type, _ = mimetypes.guess_type(full_path)
    return mime_type or "application/octet-stream" # Devuelve un tipo genérico si no se puede adivinar

# Opcional: Función para calcular duración de audio (requiere librería externa como mutagen)
# def get_audio_duration(relative_path: str):
#     """Obtiene la duración de un archivo de audio (requiere mutagen)"""
#     full_path = STATIC_DIR / relative_path
#     try:
#         audio = MP3(full_path)
#         return audio.info.length # Duración en segundos (float)
#     except Exception:
#         return None


# --- Endpoints de la API ---

@app.get("/", response_class=HTMLResponse)
def read_root(request: Request, db: Session = Depends(database.get_db)):
    """
    Displays a list of available podcasts.
    """
    data={'title': TITLE_PODCAST, 'subtitle': SUBTITLE_PODCAST}
    podcasts = crud.get_podcasts(db)
    return templates.TemplateResponse("index.html", {"request": request, "podcasts": podcasts, "data":data})


# --- Endpoints para Podcasts ---

@app.post("/podcasts/", response_model=schemas.Podcast, dependencies=[Depends(verify_token)]) # Apply security dependency
async def create_podcast(
    db: Session = Depends(database.get_db),
    title: str = Form(...),
    description: str = Form(...),
    author: str = Form(...),
    language: str = Form("es"),
    category: Optional[str] = Form(None),
    feed_url_slug: str = Form(...),
    image_file: UploadFile = File(...)
):
    # Verificar si el slug ya existe
    db_podcast_slug = crud.get_podcast_by_slug(db, slug=feed_url_slug)
    if db_podcast_slug:
        raise HTTPException(status_code=400, detail="Podcast with this feed slug already exists")

    # Guardar la imagen subida
    image_relative_path = await save_upload_file(image_file, FILES_DIR)

    podcast_create_schema = schemas.PodcastCreate(
        title=title,
        description=description,
        author=author,
        language=language,
        category=category,
        feed_url_slug=feed_url_slug
    )

    return crud.create_podcast(db=db, podcast=podcast_create_schema, image_url=image_relative_path)

@app.get("/podcasts/", response_model=List[schemas.Podcast])
def read_podcasts(skip: int = 0, limit: int = 100, db: Session = Depends(database.get_db)):
    podcasts = crud.get_podcasts(db, skip=skip, limit=limit)
    return podcasts

@app.get("/podcasts/{podcast_id}", response_model=schemas.Podcast)
def read_podcast(podcast_id: int, db: Session = Depends(database.get_db)):
    db_podcast = crud.get_podcast(db, podcast_id=podcast_id)
    if db_podcast is None:
        raise HTTPException(status_code=404, detail="Podcast not found")
    return db_podcast

@app.put("/podcasts/{podcast_id}", response_model=schemas.Podcast, dependencies=[Depends(verify_token)]) # Apply security dependency
async def update_podcast(
    podcast_id: int,
    db: Session = Depends(database.get_db),
    title: Optional[str] = Form(None),
    description: Optional[str] = Form(None),
    author: Optional[str] = Form(None),
    language: Optional[str] = Form(None),
    category: Optional[str] = Form(None),
    feed_url_slug: Optional[str] = Form(None), # Considerar si permitir actualizar el slug
    image_file: Optional[UploadFile] = File(None)
):
    db_podcast = crud.get_podcast(db, podcast_id=podcast_id)
    if db_podcast is None:
        raise HTTPException(status_code=404, detail="Podcast not found")

    # Verificar si el nuevo slug ya existe y no es el del podcast actual
    if feed_url_slug is not None and feed_url_slug != db_podcast.feed_url_slug:
         db_podcast_slug = crud.get_podcast_by_slug(db, slug=feed_url_slug)
         if db_podcast_slug:
              raise HTTPException(status_code=400, detail="Podcast with this feed slug already exists")


    image_relative_path = None
    if image_file:
        # Opcional: Eliminar la imagen antigua si existe
        if db_podcast.image_url and (STATIC_DIR / db_podcast.image_url).exists():
            os.remove(STATIC_DIR / db_podcast.image_url)
        image_relative_path = await save_upload_file(image_file, FILES_DIR)

    # Crear un schema de actualización solo con los campos proporcionados
    update_data = {
        "title": title,
        "description": description,
        "author": author,
        "language": language,
        "category": category,
        "feed_url_slug": feed_url_slug
    }
    # Filtrar Nones y campos no configurados explícitamente
    update_schema_data = {k: v for k, v in update_data.items() if v is not None}

    podcast_update_schema = schemas.PodcastUpdate(**update_schema_data)

    return crud.update_podcast(db=db, podcast_id=podcast_id, podcast=podcast_update_schema, image_url=image_relative_path)


@app.delete("/podcasts/{podcast_id}", dependencies=[Depends(verify_token)]) # Apply security dependency
def delete_podcast(podcast_id: int, db: Session = Depends(database.get_db)):
    db_podcast = crud.get_podcast(db, podcast_id=podcast_id)
    if db_podcast is None:
        raise HTTPException(status_code=404, detail="Podcast not found")

    # Opcional: Eliminar archivos asociados (imagen y audios de episodios)
    if db_podcast.image_url and (STATIC_DIR / db_podcast.image_url).exists():
         os.remove(STATIC_DIR / db_podcast.image_url)
    for episode in db_podcast.episodes:
        if (STATIC_DIR / episode.audio_url).exists():
            os.remove(STATIC_DIR / episode.audio_url)

    crud.delete_podcast(db=db, podcast_id=podcast_id)
    return {"detail": "Podcast deleted successfully"}


# --- Endpoints para Episodios ---

@app.post("/podcasts/{podcast_id}/episodes/", response_model=schemas.Episode, dependencies=[Depends(verify_token)]) # Apply security dependency
async def create_episode_for_podcast(
    podcast_id: int,
    db: Session = Depends(database.get_db),
    title: str = Form(...),
    description: str = Form(...),
    duration: Optional[str] = Form(None), # Duración en formato HH:MM:SS
    audio_file: UploadFile = File(...)
):
    db_podcast = crud.get_podcast(db, podcast_id=podcast_id)
    if db_podcast is None:
        raise HTTPException(status_code=404, detail="Podcast not found")

    # Guardar el archivo de audio
    audio_relative_path = await save_upload_file(audio_file, FILES_DIR)

    # Obtener información del archivo
    audio_length = get_file_size(audio_relative_path)
    audio_type = get_mime_type(audio_relative_path)

    # Si no se proporciona duración, intenta calcularla (requiere mutagen u otra lib)
    duration_str = duration
    if not duration_str:
       full_path = STATIC_DIR / audio_relative_path
       duration_str = duration_mp3(full_path)

    episode_create_schema = schemas.EpisodeCreate(
        title=title,
        description=description,
        duration=duration_str # Usar la duración proporcionada o calculada
    )

    return crud.create_episode(
        db=db,
        episode=episode_create_schema,
        podcast_id=podcast_id,
        audio_url=audio_relative_path,
        audio_length=audio_length,
        audio_type=audio_type,
        duration=duration_str 
    )

@app.get("/podcasts/{podcast_id}/episodes/", response_model=List[schemas.Episode])
def read_episodes_for_podcast(podcast_id: int, skip: int = 0, limit: int = 100, db: Session = Depends(database.get_db)):
    db_podcast = crud.get_podcast(db, podcast_id=podcast_id)
    if db_podcast is None:
        raise HTTPException(status_code=404, detail="Podcast not found")
    episodes = crud.get_episodes_for_podcast(db, podcast_id=podcast_id, skip=skip, limit=limit)
    return episodes

@app.get("/episodes/{episode_id}", response_model=schemas.Episode)
def read_episode(episode_id: int, db: Session = Depends(database.get_db)):
    db_episode = crud.get_episode(db, episode_id=episode_id)
    if db_episode is None:
        raise HTTPException(status_code=404, detail="Episode not found")
    return db_episode

@app.get("/episode/{episode_id}", response_class=HTMLResponse, name="read_episode_detail")
def read_episode_detail(episode_id: int, request: Request, db: Session = Depends(database.get_db)):
    """
    Displays details of a specific episode.
    """
    db_episode = crud.get_episode(db, episode_id=episode_id)
    if db_episode is None:
        raise HTTPException(status_code=404, detail="Episode not found")

    # You might also want to fetch the parent podcast details to link back
    db_podcast = crud.get_podcast(db, podcast_id=db_episode.podcast_id)

    return templates.TemplateResponse("episode_detail.html", {"request": request, "episode": db_episode, "podcast": db_podcast})


@app.put("/episodes/{episode_id}", response_model=schemas.Episode, dependencies=[Depends(verify_token)]) # Apply security dependency
async def update_episode(
    episode_id: int,
    db: Session = Depends(database.get_db),
    title: Optional[str] = Form(None),
    description: Optional[str] = Form(None),
    duration: Optional[str] = Form(None),
    audio_file: Optional[UploadFile] = File(None)
):
    db_episode = crud.get_episode(db, episode_id=episode_id)
    if db_episode is None:
        raise HTTPException(status_code=404, detail="Episode not found")

    audio_relative_path = None
    audio_length = None
    audio_type = None

    if audio_file:
        # Opcional: Eliminar el archivo de audio antiguo si existe
        if db_episode.audio_url and (STATIC_DIR / db_episode.audio_url).exists():
            os.remove(STATIC_DIR / db_episode.audio_url)

        audio_relative_path = await save_upload_file(audio_file, FILES_DIR)
        audio_length = get_file_size(audio_relative_path)
        audio_type = get_mime_type(audio_relative_path)
        # Recalcular duración si se sube un nuevo archivo y no se proporciona duración explícitamente
        # if duration is None:
        #     # Lógica para calcular duración del nuevo archivo
        #     pass


    # Crear un schema de actualización solo con los campos proporcionados
    update_data = {
        "title": title,
        "description": description,
        "duration": duration,
        # guid y pub_date no se actualizan comúnmente, pero podrías añadirlos si necesitas
    }
    update_schema_data = {k: v for k, v in update_data.items() if v is not None}

    episode_update_schema = schemas.EpisodeUpdate(**update_schema_data)

    return crud.update_episode(
        db=db,
        episode_id=episode_id,
        episode=episode_update_schema,
        audio_url=audio_relative_path,
        audio_length=audio_length,
        audio_type=audio_type
    )

@app.delete("/episodes/{episode_id}", dependencies=[Depends(verify_token)]) # Apply security dependency
def delete_episode(episode_id: int, db: Session = Depends(database.get_db)):
    db_episode = crud.get_episode(db, episode_id=episode_id)
    if db_episode is None:
        raise HTTPException(status_code=404, detail="Episode not found")

    # Opcional: Eliminar el archivo de audio asociado
    if db_episode.audio_url and (STATIC_DIR / db_episode.audio_url).exists():
         os.remove(STATIC_DIR / db_episode.audio_url)

    crud.delete_episode(db=db, episode_id=episode_id)
    return {"detail": "Episode deleted successfully"}

# --- Endpoint para el Feed RSS ---

@app.get("/feeds/{feed_url_slug}/rss.xml")
def get_podcast_feed(feed_url_slug: str, request: Request, db: Session = Depends(database.get_db)):
    db_podcast = crud.get_podcast_by_slug(db, slug=feed_url_slug)
    if db_podcast is None:
        raise HTTPException(status_code=404, detail="Podcast feed not found")

    # Recuperar todos los episodios del podcast, ordenados por fecha de publicación (más reciente primero)
    # Asegúrate de que tu modelo Episode tiene un campo pub_date y está indexado o ordenas aquí
    episodes = db.query(models.Episode).filter(models.Episode.podcast_id == db_podcast.id).order_by(models.Episode.pub_date.desc()).all()

    # Construir la base URL dinámica si no está fija
    # base_url = str(request.base_url) # Esto obtiene http://localhost:8000/
    # O usar la BASE_URL fija definida al principio
    base_url = BASE_URL

    xml_content = feed_generator.generate_rss_feed(db_podcast, episodes, base_url)

    return Response(content=xml_content, media_type="application/xml")

# --- Endpoint para Detalles del Podcast y Episodios ---

@app.get("/{feed_url_slug}", response_class=HTMLResponse)
def read_podcast_detail(feed_url_slug: str, request: Request, db: Session = Depends(database.get_db)):
    """
    Displays details of a specific podcast and its episodes.
    """
    db_podcast = crud.get_podcast_by_slug(db, slug=feed_url_slug)
    if db_podcast is None:
        raise HTTPException(status_code=404, detail="Podcast not found")

    # Fetch episodes for the podcast, ordered by publication date
    episodes = db.query(models.Episode).filter(models.Episode.podcast_id == db_podcast.id).order_by(models.Episode.pub_date.desc()).all()

    return templates.TemplateResponse("podcast_detail.html", {"request": request, "podcast": db_podcast, "episodes": episodes})
