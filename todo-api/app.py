from flask import Flask, request, jsonify
import sqlite3
import os

app = Flask(__name__)

# Configuration de la base de données
DB_PATH = os.getenv('DB_PATH', 'todos.db')


def get_db():
    """Retourne une connexion à la base de données SQLite."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # Permet d'accéder aux colonnes par nom
    return conn


def init_db():
    """Initialise la table 'todos' si elle n'existe pas."""
    conn = get_db()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS todos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT,
            done BOOLEAN NOT NULL DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()


@app.route('/todos', methods=['GET'])
def get_todos():
    """Récupère toutes les tâches."""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM todos')
    todos = [
        {
            'id': row['id'],
            'title': row['title'],
            'description': row['description'],
            'done': bool(row['done']),
            'created_at': row['created_at']
        }
        for row in cursor.fetchall()
    ]
    conn.close()
    return jsonify(todos)


@app.route('/todos', methods=['POST'])
def create_todo():
    """Crée une nouvelle tâche."""
    if not request.is_json:
        return jsonify({'error': 'Request must be JSON'}), 400

    data = request.get_json()
    if 'title' not in data:
        return jsonify({'error': 'Title is required'}), 400

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        'INSERT INTO todos (title, description, done) VALUES (?, ?, ?)',
        (data['title'], data.get('description', ''), data.get('done', False))
    )
    conn.commit()
    todo_id = cursor.lastrowid
    conn.close()

    return jsonify({
        'id': todo_id,
        'title': data['title'],
        'description': data.get('description', ''),
        'done': data.get('done', False)
    }), 201


@app.route('/todos/<int:todo_id>', methods=['GET'])
def get_todo(todo_id):
    """Récupère une tâche par son ID."""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM todos WHERE id = ?', (todo_id,))
    row = cursor.fetchone()
    conn.close()

    if row is None:
        return jsonify({'error': 'Todo not found'}), 404

    return jsonify({
        'id': row['id'],
        'title': row['title'],
        'description': row['description'],
        'done': bool(row['done']),
        'created_at': row['created_at']
    })


@app.route('/todos/<int:todo_id>', methods=['PUT'])
def update_todo(todo_id):
    """Met à jour une tâche."""
    if not request.is_json:
        return jsonify({'error': 'Request must be JSON'}), 400

    data = request.get_json()
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        'UPDATE todos SET title = ?, description = ?, done = ? WHERE id = ?',
        (data.get('title'), data.get('description'), data.get('done'), todo_id)
    )
    conn.commit()
    rowcount = cursor.rowcount
    conn.close()

    if rowcount == 0:
        return jsonify({'error': 'Todo not found'}), 404

    return jsonify({'message': 'Todo updated'})


@app.route('/todos/<int:todo_id>', methods=['DELETE'])
def delete_todo(todo_id):
    """Supprime une tâche."""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM todos WHERE id = ?', (todo_id,))
    conn.commit()
    rowcount = cursor.rowcount
    conn.close()

    if rowcount == 0:
        return jsonify({'error': 'Todo not found'}), 404

    return jsonify({'message': 'Todo deleted'})


if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000, debug=True)
