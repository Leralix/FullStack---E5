FROM tiangolo/uvicorn-gunicorn-fastapi:python3.10
# Installer Node.js pour MDB
# Utiliser une version LTS plus récente de Node.js

# Définir le répertoire de travail pour les instructions suivantes
WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

ENV NODE_VERSION 16.14.0
RUN apt-get update && apt-get install -y curl && \
    curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.1/install.sh | bash && \
    export NVM_DIR="$([ -z "${XDG_CONFIG_HOME-}" ] && printf %s "${HOME}/.nvm" || printf %s "${XDG_CONFIG_HOME}/nvm")" && \
    [ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh" && \
    nvm install ${NODE_VERSION} && \
    nvm use ${NODE_VERSION} && \
    nvm alias default ${NODE_VERSION} && \
    ln -s "/root/.nvm/versions/node/v${NODE_VERSION}/bin/node" /usr/bin/node && \
    ln -s "/root/.nvm/versions/node/v${NODE_VERSION}/bin/npm" /usr/bin/npm && \
    ln -s "/root/.nvm/versions/node/v${NODE_VERSION}/bin/npx" /usr/bin/npx


COPY ./app /app

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "5000", "--reload"]