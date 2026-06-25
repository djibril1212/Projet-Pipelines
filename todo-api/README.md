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

## Structure du projet

```
todo-api/
├── app.py            # Application Flask + endpoints CRUD
├── test_app.py       # Tests unitaires pytest
├── requirements.txt  # Dépendances
├── .gitignore        # Exclut todos.db, venv, cache...
└── README.md         # Ce fichier
```

> ⚠️ Le fichier `todos.db` ne doit **pas** être livré (exclu par `.gitignore`).
> Aucun secret (mot de passe, token) n'est présent dans le code.
