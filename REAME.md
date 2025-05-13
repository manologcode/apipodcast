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

existen docker para: linux/amd64, linux/arm64, linux/arm/v7

crear los directorios files y data

```bash
mkdir data files
```
crear el archivo de docker compose con el siguente contencido cambiando el valor de las variable

```bash
services:
  app:
    image: manologcode/apipodcast:linux-amd64

    restart: always
    container_name: apipodcast
    ports:
        - "5002:5000"
    volumes:
        - ./files:/app/static/files
        - ./data:/app/data
    environment:
      - API_TOKEN=your_super_secret_token 
      - BASE_URL=http://localhost:5002
```