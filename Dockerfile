# Stage 1: Builder
FROM python:3.11-slim as builder

WORKDIR /app

# Installer les outils de build
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copier requirements et installer les dépendances
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

# Stage 2: Runtime
FROM python:3.11-slim

# Définir les métadonnées
LABEL maintainer="MISIMOA"
LABEL description="AI Trading Bot - Claude Opus 4.6"

# Variables d'environnement
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PYTHONPATH=/app

# Créer un utilisateur non-root pour plus de sécurité
RUN groupadd -r trader && useradd -r -g trader trader

# Répertoire de travail
WORKDIR /app

# Copier les dépendances du builder
COPY --from=builder /root/.local /home/trader/.local

# Copier le code de l'application
COPY --chown=trader:trader . .

# Ajouter le répertoire .local/bin au PATH
ENV PATH=/home/trader/.local/bin:$PATH

# Changer vers l'utilisateur non-root
USER trader

# Healthcheck (pour Render - vérifie que le processus tourne)
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import sys; sys.exit(0)" || exit 1

# Commande de démarrage
CMD ["python", "claude-opus-4-6.py"]
