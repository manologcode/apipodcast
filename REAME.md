# 🎙️ Podcast Publisher API

Una aplicación web para publicar y alojar episodios de podcast de forma automática, a través de una API RESTful. Ideal para creadores que desean gestionar su propio contenido sin depender de plataformas externas. Totalmente autoalojable y preparada para ejecutarse con Docker.

## 🚀 Características

- 📡 Publicación de episodios vía API.
- 💾 Almacenamiento automático de archivos de audio (self-hosted).
- 🧾 Metadatos de episodios (título, descripción, fecha, duración, etc.).
- 🎧 Reproductor embebible y enlaces directos.
- 🐳 Despliegue sencillo con Docker y Docker Compose.
- 🔐 Seguridad con tokens o autenticación.


## 🧑‍💻 Tecnologías

- Backend: FastAPI
- Base de datos: SQLite
- Contenedores: Docker + Docker Compose

## 📦 Instalación rápida (con Docker)

```bash
# Clona el repositorio
git clone https://github.com/<tu-usuario>/<nombre-del-repo>.git
cd <nombre-del-repo>

# Copia el archivo de entorno si existe
cp .env.example .env

# Construye y levanta los contenedores
docker compose up --build

```

services:
  app:
    image: manologcode/api-podcast
    restart: always
    container_name: apipodcast
    ports:
        - "5002:5000"
    volumes:
        - ./files:/app/static/files
    environment:
      - API_TOKEN=your_super_secret_token # <-- REPLACE WITH A STRONG, UNIQUE TOKEN
