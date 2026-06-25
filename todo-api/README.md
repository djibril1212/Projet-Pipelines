# Todo API — Module 4 (DevSecOps)

API REST minimaliste de gestion de tâches (Todo) développée avec **Flask** et **SQLite**.
Elle expose des endpoints CRUD et est couverte par des tests unitaires **pytest**.

## Prérequis

- Python 3.8+
- pip

## Installation

```bash
cd todo-api

# (recommandé) créer un environnement virtuel
python -m venv .venv
source .venv/bin/activate      # Windows : .venv\Scripts\activate

# installer les dépendances
pip install -r requirements.txt
```

## Lancer l'application

```bash
python app.py
```

L'application :
- démarre sur http://localhost:5000
- crée automatiquement la base SQLite `todos.db` au premier lancement

Le chemin de la base peut être modifié via la variable d'environnement `DB_PATH` :

```bash
DB_PATH=/chemin/vers/ma_base.db python app.py
```

## Exécuter les tests

```bash
pytest test_app.py -v
```

Les tests utilisent une base SQLite **temporaire et isolée** (aucun impact sur `todos.db`).

## Endpoints de l'API

| Méthode | Endpoint            | Description                          | Corps (JSON)                                  |
|---------|---------------------|--------------------------------------|-----------------------------------------------|
| GET     | `/todos`            | Liste toutes les tâches              | —                                             |
| POST    | `/todos`            | Crée une nouvelle tâche              | `{"title": "...", "description": "...", "done": false}` |
| GET     | `/todos/<id>`       | Récupère une tâche par son ID        | —                                             |
| PUT     | `/todos/<id>`       | Met à jour une tâche                 | `{"title": "...", "description": "...", "done": true}` |
| DELETE  | `/todos/<id>`       | Supprime une tâche                   | —                                             |

### Modèle d'une tâche

```json
{
  "id": 1,
  "title": "Apprendre DevSecOps",
  "description": "Module 4 TP",
  "done": false,
  "created_at": "2026-06-25 10:00:00"
}
```

### Codes de réponse

- `200` — succès (GET, PUT, DELETE)
- `201` — tâche créée (POST)
- `400` — requête invalide (corps non JSON ou `title` manquant)
- `404` — tâche introuvable

## Exemples avec curl

```bash
# Créer une tâche
curl -X POST -H "Content-Type: application/json" \
  -d '{"title": "Apprendre DevSecOps", "description": "Module 4 TP"}' \
  http://localhost:5000/todos

# Lister les tâches
curl http://localhost:5000/todos

# Récupérer une tâche
curl http://localhost:5000/todos/1

# Mettre à jour une tâche
curl -X PUT -H "Content-Type: application/json" \
  -d '{"title": "Apprendre DevSecOps - Mise à jour", "done": true}' \
  http://localhost:5000/todos/1

# Supprimer une tâche
curl -X DELETE http://localhost:5000/todos/1
```

## Conteneurisation (Docker)

L'application est conteneurisée via le [Dockerfile](Dockerfile) :
- image de base légère `python:3.11-slim` ;
- `requirements.txt` copié **avant** le code pour optimiser le cache Docker ;
- mise à jour de l'outillage OS et pip (correctifs de sécurité) ;
- exécution en **utilisateur non-root** (`appuser`) ;
- port `5000` exposé.

### Construire l'image

```bash
cd todo-api
docker build -t todo-api .
docker images todo-api      # vérifier que l'image existe
```

### Lancer le conteneur

```bash
# Avec persistance de la base sur l'hôte (volume monté)
docker run -p 5000:5000 -v $(pwd)/todos.db:/app/todos.db todo-api
```

> ⚠️ Sur macOS, le port 5000 est souvent occupé par AirPlay Receiver.
> Utilisez par exemple `-p 5050:5000` puis testez sur http://localhost:5050/todos.

## Analyse de sécurité (Trivy)

### Scanner l'image (vulnérabilités)

```bash
trivy image todo-api                                          # sortie console
trivy image --format json --output trivy-report.json todo-api # rapport JSON
```

Le rapport complet inclut les vulnérabilités de l'image de base (OS Debian) et des
paquets Python. Pour ne garder que les vulnérabilités **corrigeables** :

```bash
trivy image --ignore-unfixed todo-api
```

**Résultat sur ce projet :** **0 CRITICAL** et **0 HIGH** corrigeables.
Les quelques CVE CRITICAL/HIGH restantes proviennent uniquement de paquets OS
(`perl-base`, `ncurses`, `libsqlite3`...) **sans correctif disponible** côté Debian
à ce jour — elles ne sont pas exploitées par l'application et sont à surveiller.

### Générer le SBOM (Software Bill of Materials)

```bash
# Format SPDX (conformité)
trivy image --format spdx-json --output sbom.spdx.json todo-api

# Format CycloneDX (alternative)
trivy image --format cyclonedx --output sbom.cdx.json todo-api

# Inspecter le contenu (nécessite jq)
jq . sbom.spdx.json | less
```

Les SBOM listent l'ensemble des paquets de l'image (~118), leurs versions,
licences et identifiants `purl`.

## Publication sur DockerHub

### Se connecter

```bash
docker login        # saisir identifiant + token DockerHub (jamais le mot de passe en clair)
```

> 🔒 Bonne pratique : créer un **Access Token** (DockerHub → Account Settings → Personal
> access tokens) plutôt que d'utiliser son mot de passe. Ne jamais committer ce token.

### Taguer l'image

```bash
# Tag mouvant + tag immuable (versionné)
docker tag todo-api <username>/todo-api:latest
docker tag todo-api <username>/todo-api:v1.0.0
```

### Pousser les images

```bash
docker push <username>/todo-api:latest
docker push <username>/todo-api:v1.0.0
```

Image visible ensuite sur `https://hub.docker.com/r/<username>/todo-api` avec les deux tags.

## Déploiement

### Option 1 — Docker (sur un serveur)

```bash
docker pull <username>/todo-api:v1.0.0
docker run -d -p 80:5000 \
  -v /chemin/vers/todos.db:/app/todos.db \
  --name todo-app \
  <username>/todo-api:v1.0.0
```

Application accessible sur `http://<ip_serveur>/todos`.

### Option 2 — Docker Compose (recommandé)

Un fichier [docker-compose.yml](docker-compose.yml) est fourni. Il monte la base en
volume, redémarre automatiquement le conteneur et ajoute un *healthcheck*.

```bash
# Optionnel : définir l'utilisateur et le tag
export DOCKERHUB_USER=<username>
export TAG=v1.0.0

docker compose up -d        # démarrer
docker compose ps           # vérifier l'état
docker compose logs -f      # suivre les logs
docker compose down         # arrêter
```

Application accessible sur `http://localhost/todos`.

### Option 3 — Kubernetes (exemple)

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: todo-api
spec:
  replicas: 2
  selector:
    matchLabels: { app: todo-api }
  template:
    metadata:
      labels: { app: todo-api }
    spec:
      containers:
        - name: todo-api
          image: <username>/todo-api:v1.0.0
          ports:
            - containerPort: 5000
          securityContext:
            runAsNonRoot: true
---
apiVersion: v1
kind: Service
metadata:
  name: todo-api
spec:
  selector: { app: todo-api }
  ports:
    - port: 80
      targetPort: 5000
  type: LoadBalancer
```

```bash
kubectl apply -f deployment.yaml
```

> ℹ️ SQLite (fichier local) ne convient pas à plusieurs réplicas qui écrivent en
> parallèle. Pour une vraie mise à l'échelle, migrer vers une base réseau
> (PostgreSQL/MySQL) ou utiliser un seul réplica.

## Bonnes pratiques appliquées

- **Image légère** : base `python:3.11-slim`.
- **Sécurité runtime** : exécution en utilisateur **non-root** (`appuser`).
- **Supply-chain** : scan Trivy (0 CRITICAL/HIGH corrigeable) + SBOM SPDX & CycloneDX.
- **Tags immuables** : `v1.0.0` en plus de `latest` pour la traçabilité des releases.
- **Cache Docker optimisé** : `requirements.txt` copié avant le code.
- **Pas de secret dans l'image / le dépôt** : token DockerHub via `docker login` uniquement.
- **Résilience** : `restart: unless-stopped` + *healthcheck* dans Docker Compose.

## Structure du projet

```
todo-api/
├── app.py                      # Application Flask + endpoints CRUD
├── test_app.py                 # Tests unitaires pytest
├── requirements.txt            # Dépendances
├── Dockerfile                  # Conteneurisation (non-root, slim)
├── .dockerignore               # Exclut db/venv/cache/tests de l'image
├── docker-compose.yml          # Déploiement Docker Compose
├── trivy-report.json           # Rapport de scan Trivy (complet)
├── trivy-report.txt            # Rapport de scan Trivy (table)
├── sbom.spdx.json              # SBOM format SPDX
├── sbom.cdx.json               # SBOM format CycloneDX
├── .gitignore                  # Exclut todos.db, venv, cache...
└── README.md                   # Ce fichier
```

> ⚠️ Le fichier `todos.db` ne doit **pas** être livré (exclu par `.gitignore`).
> Aucun secret (mot de passe, token) n'est présent dans le code.
