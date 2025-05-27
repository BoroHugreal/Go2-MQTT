from flask import Blueprint, request, render_template, flash, redirect, url_for, jsonify, Response
from .mqtt_sender import send_command
from .mqtt_ack_listener import last_ack
from .mqtt_position_listener import last_position
from .mqtt_state_listener import last_state
import cv2

# -*- coding: utf-8 -*-
"""
Routes pour l'API de contrôle du robot Go2
"""
# app/routes.py
bp = Blueprint('api', __name__)

# Route principale pour l'interface utilisateur
@bp.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        command = request.form.get('command')
        if command:
            send_command(command)
            flash(f"Commande envoyée : {command}", "success")
        else:
            flash("Aucune commande sélectionnée.", "warning")
        return redirect(url_for('api.index'))
    ack_info = None
    if last_ack["command"]:
        ack_info = f"Le robot a confirmé la commande : {last_ack['command']} (statut : {last_ack['status']})"
    return render_template('index.html', ack_info=ack_info)

# Route pour envoyer une commande au robot
@bp.route('/joystick', methods=['POST'])
def joystick_control():
    data = request.get_json()
    # Ici, traduire les données du joystick en commandes robot Go2
    if data.get('stop'):
        send_command('StopMove')
    else:
        # Mapper angle/direction à une commande Move personnalisée si besoin
        send_command('Move')
    return '', 204

# Route pour définir un chemin pour le robot
@bp.route('/set_path', methods=['POST'])
def set_path():
    path_coords = request.get_json()
    print(f"Nouveau chemin reçu: {path_coords}")
    # Si tu veux publier sur MQTT, décommente et adapte la ligne ci-dessous :
    # from .mqtt_sender import send_path
    # send_path(path_coords)
    return jsonify({"status": "ok"}), 200

# Route pour obtenir l'état de l'accusé de réception
@bp.route('/robot_position')
def robot_position():
    # Retourne la dernière position du robot
    if not last_position:
        return jsonify({"error": "Position non disponible"}), 404
    return jsonify(last_position)

# Route pour obtenir l'état du robot
@bp.route('/robot_state')
def robot_state():
    # Retourne le dernier état du robot
    if not last_state:
        return jsonify({"error": "État non disponible"}), 404
    return jsonify(last_state)

# Ouvre la caméra ou le flux vidéo du robot (modifie l'URL/ID selon ton matériel)
# Exemple pour caméra USB : cap = cv2.VideoCapture(0)
# Exemple pour flux RTSP : cap = cv2.VideoCapture("rtsp://ip_du_robot/stream")
cap = cv2.VideoCapture(0)  # À adapter à ton cas réel

def gen_frames():
    while True:
        success, frame = cap.read()
        if not success:
            break
        else:
            # Encode l'image en JPEG
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            # MJPEG : multipart/x-mixed-replace
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

# Route pour afficher le flux vidéo du robot
@bp.route('/robot_video')
def robot_video():
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')