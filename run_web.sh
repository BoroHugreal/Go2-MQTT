#!/bin/bash

# source venv/bin/activate

# Forçage de l'environnement si non défini
FLASK_ENV=${FLASK_ENV:-development}
export FLASK_ENV

# Clé secrète si absente
export FLASK_SECRET_KEY=${FLASK_SECRET_KEY:-$(openssl rand -hex 32)}

# Mode debug explicite (désactivé si besoin)
if [ "$FLASK_ENV" = "development" ]; then
  export FLASK_DEBUG=1
  HOST="127.0.0.1"
else
  export FLASK_DEBUG=0
  HOST="0.0.0.0"
fi

export FLASK_APP="app:create_app"

# Lancement sans redémarrage automatique ni debugger PIN
python -m flask run --no-reload --host=$HOST --port=5001