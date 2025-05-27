#!/bin/bash

# Active l'environnement virtuel si besoin
# source venv/bin/activate

export FLASK_ENV=development

export FLASK_DEBUG=1

# Indique à Flask comment créer l'app : module + fonction factory
export FLASK_APP="app:create_app"

flask run --host=0.0.0.0 --port=5001
