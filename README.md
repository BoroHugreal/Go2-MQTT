# Go2-MQTT Control Panel #
Go2-MQTT est une interface web complète pour piloter, surveiller et programmer un robot quadrupède Go2 (Unitree Robotics) via MQTT, avec retour temps réel, cartographie, joystick, clavier, vidéo, et outils de debug.

# Sommaire #
 - Fonctionnalités
 - Squelette du projet
 - Installation
 - Configuration
 - Explication des fichiers
 - Architecture technique
 - Utilisation
 - Outils de développement
 - FAQ & Dépannage

# Fonctionnalités #
 - Contrôle temps réel du robot Go2 via MQTT (commandes, joystick, clavier)
 - Cartographie Google Maps : tracé de chemins, export, envoi au robot
 - Flux vidéo embarqué (MJPEG, simulé ou réel)
 - Statut MQTT et robot en direct (connecté/déconnecté)
 - Outils de debug (écoute de topics MQTT, analyse des messages)
 - Interface moderne (responsive, dark/light mode)

# Squelette du projet #
Go2-MQQT/
│
├── app/
│   ├── __init__.py           # Usine Flask
│   ├── main.py               # Routes Flask (API & Web)
│   ├── mqtt_manager.py       # Connexion MQTT persistante (thread)
│   ├── mqtt_sender.py        # Fonctions d'envoi de commandes/chemin
│   ├── config.py             # Paramètres MQTT (broker, topics, user, mdp)
│
├──dev_tools/
│   └──receiver_debug.py      # Outils dev_tools/debug MQTT (sniffer)
│
├── static/
│   ├── script.js             # JS principal (contrôles, statut, carte, etc.)
│   └── index.css             # Styles CSS
│
├── templates/
│   └── index.html            # Vue principale (interface web)
│
├── run_web.sh                # Script de lancement Flask
├── requirements.txt          # Dépendances Python
└── README.md                 # Ce fichier


# Installation #
1. Clone le repo et place-toi dans le dossier :
- git clone https://github.com/BoroHugreal/Go2-MQQT.git Go2-MQQT
- cd Go2-MQQT

2. Installe les dépendances Python :
- python3 -m venv venv
- source venv/bin/activate
- pip install -r requirements.txt

3. Configure le broker MQTT dans app/config.py (ou via .env pour la prod).
4. Lance le serveur Flask :
- /.run_web.sh (!NE PAS OUBLIER DE METTRE LES DROITS D'EXECUTIONS!)

# Configuration #
app/config.py contient :
 - Adresse du broker MQTT (MQTT_BROKER)
 - Port (MQTT_PORT)
 - Topics (MQTT_TOPIC_COMMAND, MQTT_TOPIC_PATH)
 - Identifiants (MQTT_USER, MQTT_PASSWORD)

Pour la prod, tu peux utiliser un fichier .env ou des variables d’environnement.

# Explication des fichiers #
app/__init__.py
 - Crée l’application Flask et enregistre le blueprint principal.

app/main.py (Toutes les routes web/API)
/ : page principale, formulaire de commande
/set_path : envoi d’un chemin au robot
/mqtt_status : statut temps réel du broker
/robot_stop / /robot_pause : arrêts rapides
/robot_video : flux vidéo MJPEG (simulé ou réel)
/video_status : statut vidéo
/send_command : API POST pour commandes personnalisées
/joystick : API POST pour commandes directionnelles (joystick/clavier)

app/mqtt_manager.py
 - Gère la connexion MQTT persistante dans un thread.
 - Expose mqtt_manager (singleton), utilisé partout dans l’app.
 - Gère reconnexion automatique et statut temps réel.

app/mqtt_sender.py
 - Fonction send_command(name, params=None) : envoie une commande au robot (avec code numérique et params optionnels)
 - Fonction send_path(coords) : envoie un chemin (liste de waypoints)
 - Fonction check_mqtt_connection() : retourne l’état de connexion MQTT
 - Dictionnaire SPORT_CMD : mapping nom de commande → code numérique officiel Go2

dev_tools/receiver_debug.py
 - Sniffer MQTT pour développeur : écoute tous les topics du broker, affiche les messages reçus en temps réel, permet de filtrer, utile pour debug.

static/script.js
 - Contrôles JS : joystick (NippleJS), clavier, statut MQTT, vidéo, carte Google Maps, export de chemins, feedback UI.

static/index.css
 - Styles modernes, responsive, dark/light mode, ergonomie.

templates/index.html
 - Vue principale : interface utilisateur complète, intégration JS/CSS, formulaires, carte, vidéo, feedback.

run_web.sh
 - Script de lancement Flask avec gestion des variables d’environnement.

requirements.txt
 - Dépendances Python : Flask, Flask-WTF, paho-mqtt, etc.

# Architecture technique #
[Utilisateur]
    │
    │  (Navigateur Web)
    ▼
[Flask Backend]  <--- MQTT --->  [Broker MQTT]  <--- MQTT --->  [Robot Go2]
    │
    ├─ REST API (commandes, status, chemins)
    ├─ Web UI (HTML/JS/CSS)
    └─ Thread MQTT persistant (publish/subscribe)

- Frontend : HTML/JS (Google Maps, NippleJS, fetch API)
- Backend : Flask (Python), MQTT (paho-mqtt)
- Robot : Go2, reçoit les commandes via MQTT

# Utilisation #
1. Envoyer une commande rapide :
Sélectionne une commande dans la liste et clique “Envoyer”.
2. Contrôler le robot :
Utilise le joystick ou les flèches du clavier pour piloter en direct.
3. Tracer un chemin :
Clique sur “Activer le tracé”, dessine sur la carte, puis “Envoyer le chemin”.
4. Voir le statut :
Le header affiche l’état MQTT, la batterie, la position, etc.
5.Superviser le trafic MQTT :
Lance python -m dev_tools.receiver_debug dans un terminal pour voir tous les messages échangés.

# Outils de développement #
 - Debug MQTT : app/dev_tools.py (sniffer tous les topics)
 - Logs Flask : affichés dans la console au lancement
 - Logs MQTT : affichés lors des connexions/déconnexions et erreurs de publication

# FAQ & Dépannage #
1. Le front affiche “Déconnecté” alors que le backend est connecté :
Vérifie qu’il n’y a qu’une seule instance de mqtt_manager (pas de double import).
Attends 1-2s après le démarrage du serveur (connexion asynchrone).
Regarde les logs Flask pour voir l’état réel.

2. Aucune commande ne part :
Vérifie la config MQTT (broker, user, mdp).
Vérifie que le robot écoute bien sur le topic robot/commands.

3. La carte ne s’affiche pas :
Vérifie ta clé API Google Maps et que la facturation est activée.

4. Le flux vidéo est vide :
La simulation envoie des images vides : adapte robot_video pour brancher le vrai flux MJPEG du robot.

# Contact & Auteurs #
- Projet réalisé par ALVES MIRANDA Hugo, 
  dans le cadre de mon stage au Laboratoire LISSI 
  (Avril 2025 - Juin2025)
- Basé sur les technologies : Flask, MQTT, Google Maps, NippleJS.

