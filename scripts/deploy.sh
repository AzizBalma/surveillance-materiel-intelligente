#!/bin/bash
set -e
echo "Création des dossiers ..."
mkdir -p data models alerts logs visualizations

echo "Construire et démarrer le conteneur..."
docker-compose down --remove-orphans || true
docker-compose up --build -d

echo "Attente 5s..."
sleep 5
docker-compose ps
echo "Logs (tail 50) :"
docker-compose logs --tail=50
