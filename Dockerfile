FROM tiangolo/uvicorn-gunicorn-fastapi:python3.10
LABEL authors="leralix"

COPY requirements.txt requirements.txt
ADD requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY src/ .

