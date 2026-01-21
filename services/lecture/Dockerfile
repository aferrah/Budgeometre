FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc libpq-dev && rm -rf /var/lib/apt/lists/*

# 1. On copie le dossier partagé
COPY shared /app/shared

# 2. On copie les fichiers spécifiques au service lecture
COPY services/lecture/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY services/lecture/ .

EXPOSE 5002

CMD ["python", "app.py"]