import os
import tempfile

import pytest

import app as app_module


@pytest.fixture
def client():
    """Client de test Flask utilisant une base SQLite temporaire et isolée."""
    db_fd, db_path = tempfile.mkstemp(suffix='.db')

    # Redirige l'application vers la base temporaire
    app_module.DB_PATH = db_path
    app_module.app.config['TESTING'] = True

    # Initialise la table 'todos' dans la base temporaire
    app_module.init_db()

    with app_module.app.test_client() as client:
        yield client

    # Nettoyage
    os.close(db_fd)
    os.unlink(db_path)


def test_get_todos_empty(client):
    """La liste est vide au démarrage."""
    response = client.get('/todos')
    assert response.status_code == 200
    assert response.get_json() == []


def test_create_todo(client):
    """Création d'une tâche valide."""
    response = client.post(
        '/todos',
        json={'title': 'Apprendre DevSecOps', 'description': 'Module 4 TP'}
    )
    assert response.status_code == 201
    data = response.get_json()
    assert data['id'] == 1
    assert data['title'] == 'Apprendre DevSecOps'
    assert data['description'] == 'Module 4 TP'
    assert data['done'] is False


def test_create_todo_missing_title(client):
    """La création échoue sans titre."""
    response = client.post('/todos', json={'description': 'Sans titre'})
    assert response.status_code == 400
    assert 'error' in response.get_json()


def test_get_todo_by_id(client):
    """Récupération d'une tâche existante par ID."""
    client.post('/todos', json={'title': 'Tâche 1'})
    response = client.get('/todos/1')
    assert response.status_code == 200
    data = response.get_json()
    assert data['id'] == 1
    assert data['title'] == 'Tâche 1'


def test_get_todo_not_found(client):
    """Récupération d'une tâche inexistante."""
    response = client.get('/todos/999')
    assert response.status_code == 404
    assert 'error' in response.get_json()


def test_update_todo(client):
    """Mise à jour d'une tâche existante."""
    client.post('/todos', json={'title': 'Ancien titre'})
    response = client.put(
        '/todos/1',
        json={'title': 'Nouveau titre', 'description': 'MAJ', 'done': True}
    )
    assert response.status_code == 200
    assert response.get_json()['message'] == 'Todo updated'

    # Vérifie que la modification est persistée
    updated = client.get('/todos/1').get_json()
    assert updated['title'] == 'Nouveau titre'
    assert updated['done'] is True


def test_update_todo_not_found(client):
    """Mise à jour d'une tâche inexistante."""
    response = client.put('/todos/999', json={'title': 'X'})
    assert response.status_code == 404
    assert 'error' in response.get_json()


def test_delete_todo(client):
    """Suppression d'une tâche existante."""
    client.post('/todos', json={'title': 'À supprimer'})
    response = client.delete('/todos/1')
    assert response.status_code == 200
    assert response.get_json()['message'] == 'Todo deleted'

    # La tâche n'existe plus
    assert client.get('/todos/1').status_code == 404


def test_delete_todo_not_found(client):
    """Suppression d'une tâche inexistante."""
    response = client.delete('/todos/999')
    assert response.status_code == 404
    assert 'error' in response.get_json()
