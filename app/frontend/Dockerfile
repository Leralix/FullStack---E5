FROM tiangolo/uvicorn-gunicorn-fastapi:python3.10
# Installer Node.js pour MDB
# Utiliser une version LTS plus récente de Node.js

# Définir le répertoire de travail pour les instructions suivantes
WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt


COPY ./app /app