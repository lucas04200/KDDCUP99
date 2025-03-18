# Détection d'Anomalies Réseau KDD Cup 99

Une application web interactive pour la visualisation du trafic réseau et la détection d'anomalies basée sur le dataset KDD Cup 99.

## Aperçu

Ce projet implémente un système de visualisation de trafic réseau en temps réel avec détection d'anomalies. Il se compose d'une interface web qui affiche les connexions réseau du dataset KDD Cup 99 et d'un agent de détection d'anomalies basé sur le machine learning qui analyse le trafic en temps réel.

## Architecture

Le système est construit sur trois composants principaux :

1. **Interface Web** : Une application Streamlit qui visualise les connexions réseau et fournit des fonctionnalités interactives telles que le filtrage, le zoom et les détails des événements.

2. **Agent de Détection d'Anomalies** : Un module de machine learning qui analyse le trafic réseau en temps réel et génère des alertes pour les menaces potentielles.

3. **Backend FastAPI** : Une API qui gère la communication entre l'interface et l'agent de détection.

L'ensemble du système est conteneurisé avec Docker et déployé via Azure DevOps.

## Fonctionnalités

- Visualisation du trafic réseau en temps réel
- Mode playback pour revoir les sessions passées
- Interaction utilisateur via filtres et zoom
- Détection d'anomalies utilisant Random Forest (précision de 95%)
- Temps de réponse rapide (~50ms)
- Scalabilité pour gérer des milliers d'événements par seconde

## Technologies

| Composant | Technologie |
|-----------|------------|
| Interface Web | Streamlit |
| API Backend | FastAPI (Python) |
| Détection d'Anomalies | Scikit-learn |
| Conteneurisation | Docker |
| Déploiement | Azure DevOps |

## Méthodologie

### Prétraitement des Données

- Nettoyage : Suppression des valeurs aberrantes
- Feature Engineering : Sélection des caractéristiques les plus pertinentes
- Encodage et normalisation : Préparation des données pour l'entraînement du modèle

### Détection des Anomalies

L'agent est entraîné sur le dataset KDD Cup 99 en utilisant Random Forest. Il classifie les connexions en temps réel et génère des alertes pour les anomalies.

### Développement de l'Interface Web

L'interface permet :
- Une visualisation dynamique des flux réseau
- Un mode playback pour rejouer des sessions passées
- Une interaction utilisateur via filtres et zoom

## Points de Terminaison API

- `POST /predict` : Classification des données KDD Cup 99 à l'aide du modèle entraîné
- `GET /data` : Récupération des données du fichier CSV

## Déploiement

### Conteneurisation Docker

L'application est entièrement conteneurisée avec Docker :
- Chaque module (backend et frontend) est isolé dans son propre conteneur
- Docker Compose orchestre les conteneurs
- Cette approche assure portabilité, scalabilité et facilité de gestion

### CI/CD avec Azure DevOps

Une VM Linux configurée avec Docker et Docker Compose sert d'environnement d'exécution. Le pipeline CI/CD :
1. Récupère le dernier code de GitHub à chaque push sur la branche principale
2. Construit et met à jour les images Docker
3. Démarre ou met à jour les conteneurs

Cette approche assure un déploiement rapide, sécurisé et automatisé.

## Performances

- Précision de détection : ~95% avec Random Forest
- Temps de réponse de l'API : ~50ms
- Scalabilité : Gère des milliers d'événements par seconde

## Accès

- Interface Web : [https://kddcup99.ddns.net/](https://kddcup99.ddns.net/)
- Code Source : [https://github.com/lucas04200/KDDCUP99](https://github.com/lucas04200/KDDCUP99)

## Installation et Configuration

### Prérequis

- Docker et Docker Compose
- Git

### Étapes d'Installation

1. Cloner le dépôt :
   ```
   git clone https://github.com/lucas04200/KDDCUP99.git
   cd KDDCUP99
   ```

2. Construire et démarrer les conteneurs :
   ```
   docker-compose up -d
   ```

3. Accéder à l'interface web à l'adresse `http://localhost:8501`

## Équipe

- Équipe 5
