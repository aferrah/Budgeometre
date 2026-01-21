FROM python:3.11-slim

WORKDIR /app

# On copie d'abord les dépendances
COPY gateway/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# On copie tout le contenu du dossier gateway (routes, templates, app.py) dans /app
COPY gateway/ .

EXPOSE 5000

# app.py est maintenant bien à la racine de /app dans l'image
CMD ["python", "app.py"]