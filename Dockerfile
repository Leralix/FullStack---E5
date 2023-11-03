FROM tiangolo/uvicorn-gunicorn-fastapi:python3.10

LABEL authors="leralix"

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Ensuite, copiez le reste de votre code d'application.
COPY database.py .
COPY main.py .
COPY models.py .
COPY static/ static/
COPY templates/ templates/

# Vous pouvez définir une variable d'environnement pour dire à FastAPI où
# trouver les fichiers statiques, si vous utilisez FastAPI pour les servir.
ENV STATIC_PATH /app/static

# Les commandes pour lancer l'application restent les mêmes.