FROM python:3.11-slim

WORKDIR /app

# Installation des dépendances système pour PostgreSQL
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc libpq-dev && rm -rf /var/lib/apt/lists/*

# 1. On copie le dossier partagé (depuis la racine du projet)
COPY shared /app/shared

# 2. On copie les fichiers spécifiques (depuis le dossier du service)
COPY services/ecriture/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# On copie tout le contenu du dossier ecriture directement dans /app
COPY services/ecriture/ .

EXPOSE 5001

# Maintenant app.py est bien à la racine de /app dans l'image
CMD ["python", "app.py"]