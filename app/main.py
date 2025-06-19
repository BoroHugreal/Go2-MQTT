# app/main.py
from flask import Response, Blueprint, request, render_template, flash, redirect, url_for, jsonify, abort
from flask_wtf.csrf import CSRFProtect
from .mqtt_sender import send_path, send_command, check_mqtt_connection
import logging

csrf = CSRFProtect()
bp = Blueprint('api', __name__)
logger = logging.getLogger(__name__)

COMMANDS = [
    "Stand", "Sit", "Forward", "Backward", "TurnLeft", "TurnRight", "StopMove", "Pause",
    "Dance", "GetUp", "Rest", "Stretch", "Shake", "Wave", "PushUp"
]

@bp.route('/', methods=['GET', 'POST'])
@csrf.exempt
def index():
    if request.method == 'POST':
        command = request.form.get('command')
        if command:
            success = send_command(command)
            if success:
                flash(f"Commande envoyée : {command}", "success")
                logger.info(f"Commande envoyée : {command}")
            else:
                flash("Erreur lors de l'envoi de la commande.", "danger")
        else:
            flash("Aucune commande sélectionnée.", "warning")
        return redirect(url_for('api.index'))
    return render_template('index.html', commands=COMMANDS)

@bp.route('/set_path', methods=['POST'])
@csrf.exempt
def set_path():
    path_coords = request.get_json(force=True)
    if not path_coords or not isinstance(path_coords, list):
        abort(400, description="Données de chemin invalides")
    logger.info(f"Nouveau chemin reçu : {path_coords}")
    success = send_path(path_coords)
    if not success:
        return jsonify({"status": "error", "message": "Échec de publication MQTT"}), 500
    return jsonify({"status": "ok"}), 200

@bp.route('/mqtt_status')
def mqtt_status():
    connected = check_mqtt_connection()
    return jsonify({"connected": connected})

@bp.route('/robot_stop', methods=['POST'])
@csrf.exempt
def robot_stop():
    send_command('StopMove')
    logger.info("Commande envoyée: StopMove (robot_stop)")
    return jsonify({"status": "ok", "message": "Robot stoppé"})

@bp.route('/robot_pause', methods=['POST'])
@csrf.exempt
def robot_pause():
    send_command('Pause')
    logger.info("Commande envoyée: Pause (robot_pause)")
    return jsonify({"status": "ok", "message": "Robot en pause"})

@bp.route('/robot_video')
def robot_video():
    def gen_frames():
        import time
        while True:
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + b'' + b'\r\n')
            time.sleep(0.1)
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@bp.route('/video_status')
def video_status():
    # Simule un statut vidéo (à adapter plus tard)
    return jsonify({
        "mqtt_connected": check_mqtt_connection(),
        "has_frame": False
    })

@bp.route('/send_command', methods=['POST'])
@csrf.exempt
def send_command_api():
    data = request.get_json(force=True)
    command = data.get('command')
    if not command:
        return jsonify({"status": "error", "message": "Commande manquante"}), 400
    success = send_command(command)
    if not success:
        return jsonify({"status": "error", "message": "Échec de publication MQTT"}), 500
    return jsonify({"status": "ok", "message": f"Commande {command} envoyée"})

@bp.route('/joystick', methods=['POST'])
@csrf.exempt
def joystick_control():
    data = request.get_json(force=True)
    if not data:
        return jsonify({"status": "error", "message": "Données manquantes"}), 400

    jtype = data.get('type')
    stop = data.get('stop', False)
    key = data.get('key')

    if stop:
        send_command('StopMove')
    else:
        if jtype == 'direction':
            if key in ['up', 'forward']:
                send_command('Forward')
            elif key in ['down', 'backward']:
                send_command('Backward')
            elif key in ['left']:
                send_command('TurnLeft')
            elif key in ['right']:
                send_command('TurnRight')
            else:
                send_command('Move')
        elif jtype == 'move':
            if key == 'forward':
                send_command('Forward')
            elif key == 'backward':
                send_command('Backward')
            else:
                send_command('Move')
        elif jtype == 'turn':
            if key == 'left':
                send_command('TurnLeft')
            elif key == 'right':
                send_command('TurnRight')
            else:
                send_command('Turn')
        else:
            send_command('Move')

    return jsonify({"status": "ok"}), 200