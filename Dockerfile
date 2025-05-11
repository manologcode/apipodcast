FROM python:3.9-slim

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

RUN useradd --create-home myuser
WORKDIR /app

COPY --chown=myuser:myuser ./app/requirements.txt /app/

# RUN echo "update" > /tmp/update_trigger

RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

USER myuser

# Copia el código de la app después de instalar dependencias
COPY --chown=myuser:myuser ./app /app/


# Ejecuta Gunicorn con parámetros de seguridad
# CMD ["gunicorn", "-k", "uvicorn.workers.UvicornWorker", "-w", "4", "-b", "0.0.0.0:5000", \
#      "--limit-request-line", "4094", "--limit-request-field_size", "8190", \
#      "--timeout", "30", "--worker-tmp-dir", "/dev/shm", \
#      "--forwarded-allow-ips", "*", "--access-logfile", "-"]

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "5000"]
