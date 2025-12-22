import os


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY") or "budgeometre_secret"
    ECRITURE_SERVICE_URL = os.environ.get("ECRITURE_SERVICE_URL") or "http://localhost:5001"
    LECTURE_SERVICE_URL = os.environ.get("LECTURE_SERVICE_URL") or "http://localhost:5002"
