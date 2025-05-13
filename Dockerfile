FROM python:3.9-slim

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Install build-essential and ffmpeg (which includes ffprobe)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

RUN useradd --create-home --uid 1000 myuser
WORKDIR /app

COPY --chown=myuser:myuser ./app/requirements.txt /app/

RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

USER myuser

# Copy the application code after installing dependencies
COPY --chown=myuser:myuser ./app /app/

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "5000"]

