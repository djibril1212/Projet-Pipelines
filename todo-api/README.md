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

## Structure du projet

```
todo-api/
├── app.py                      # Application Flask + endpoints CRUD
├── test_app.py                 # Tests unitaires pytest
├── requirements.txt            # Dépendances
├── Dockerfile                  # Conteneurisation (non-root, slim)
├── .dockerignore               # Exclut db/venv/cache/tests de l'image
├── trivy-report.json           # Rapport de scan Trivy (complet)
├── trivy-report.txt            # Rapport de scan Trivy (table)
├── sbom.spdx.json              # SBOM format SPDX
├── sbom.cdx.json               # SBOM format CycloneDX
├── .gitignore                  # Exclut todos.db, venv, cache...
└── README.md                   # Ce fichier
```

> ⚠️ Le fichier `todos.db` ne doit **pas** être livré (exclu par `.gitignore`).
> Aucun secret (mot de passe, token) n'est présent dans le code.
