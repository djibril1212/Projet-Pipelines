# Utiliser une image de base légère
FROM python:3.11-slim

# Variables d'environnement Python (logs non bufferisés, pas de .pyc)
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# Définir le répertoire de travail
WORKDIR /app

# Mettre à jour les paquets OS de l'image de base (correctifs de sécurité)
RUN apt-get update && apt-get upgrade -y \
    && rm -rf /var/lib/apt/lists/*

# Copier requirements.txt EN PREMIER pour profiter du cache Docker
# (cette couche n'est reconstruite que si requirements.txt change)
COPY requirements.txt .

# Mettre à jour l'outillage pip/setuptools/wheel (corrige plusieurs CVE HIGH)
# puis installer les dépendances de l'application
RUN pip install --no-cache-dir --upgrade pip setuptools wheel \
    && pip install --no-cache-dir -r requirements.txt

# Copier le reste du code de l'application
COPY app.py .

# Créer un utilisateur non-root et lui donner les droits sur /app
RUN useradd -m appuser && chown -R appuser /app
USER appuser

# Exposer le port 5000
EXPOSE 5000

# Lancer l'application
CMD ["python", "app.py"]
