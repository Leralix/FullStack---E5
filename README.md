# FullStack---E5
Projet final de fullstack à ESIEE Paris (filière DSIA)

## Membres du projet:

Gabriel Moignet

Thibaud Leroux

Samuel Sarfati

## Introduction 
Dans l'objectif de comprendre le fonctionnement d'une API, nous avons décider de réaliser un site internet qui propose des blinds test a partir de playlists spotify. Ce projet est entirèrement dockerisé en un seul docker-compose
Librairies utilisés

- Fast API pour le backend
- Flask pour le frontEnd
- PostgreSQL pour la base de donnée
- Keycloak pour l'authentification



## Instruction pour le lancement:

Renomer le fichier `.env.copy`en `.env`

Pour lancer le projet, executer `docker-compose up -d` a la racide du dossier

Pour mettre en place keycloak sur une nouvelle machine, re-générer les client secret des client `frontend` et `myclient` dans le realm `myrealm`. Sans cela, l'authentification ne sera pas disponible.


Nous remercions MDBootstrap pour avoir permis une création rapide et efficace d'un frontend
