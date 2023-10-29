FROM tiangolo/uvicorn-gunicorn-fastapi:python3.10
LABEL authors="leralix"
WORKDIR ./src


COPY requirements.txt .
RUN pip install -r requirements.txt

COPY src/ .