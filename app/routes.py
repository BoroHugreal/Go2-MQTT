# app/routes.py
# -*- coding: utf-8 -*-
"""
Routes Flask robustes, sécurisées et refactorisées pour contrôle robot.
"""

from flask import Blueprint, request, render_template, flash, redirect, url_for, jsonify, Response, abort
from flask_wtf.csrf import CSRFProtect
from .mqtt_sender import send_command
from .mqtt_ack_listener import last_ack
from .mqtt_position_listener import last_position
from .mqtt_state_listener import get_state, get_mqtt_status
from .mqtt_video_listener import get_last_frame, get_video_status
import logging
import time

csrf = CSRFProtect()
bp = Blueprint('api', __name__)
logger = logging.getLogger(__name__)

def gen_frames():
    while True:
        frame = get_last_frame()
        if frame is not None:
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
        else:
            # Si aucune frame n'est dispo, attends un peu
            time.sleep(0.05)

@bp.route('/robot_video')
def robot_video():
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@bp.route('/video_status')
def video_status():
    mqtt_status = get_video_status()
    has_frame = get_last_frame() is not None
    return jsonify({
        "mqtt_connected": mqtt_status,
        "has_frame": has_frame
    })

@bp.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        command = request.form.get('command')
        if command:
            send_command(command)
            flash(f"Commande envoyée : {command}", "success")
            logger.info(f"Commande envoyée via formulaire : {command}")
        else:
            flash("Aucune commande sélectionnée.", "warning")
        return redirect(url_for('api.index'))

    ack_info = None
    if last_ack.get("command"):
        ack_info = f"Le robot a confirmé la commande : {last_ack['command']} (statut : {last_ack['status']})"
    return render_template('index.html', ack_info=ack_info)

@bp.route('/joystick', methods=['POST'])
@csrf.exempt
def joystick_control():
    data = request.get_json(force=True)
    if not data:
        abort(400, description="Données JSON manquantes")

    jtype = data.get('type')
    stop = data.get('stop', False)
    key = data.get('key')

    if stop:
        if jtype in ('direction', 'turn'):
            send_command('StopTurn')
            logger.debug("Commande envoyée: StopTurn")
        else:
            send_command('StopMove')
            logger.debug("Commande envoyée: StopMove (stop)")
    else:
        if jtype == 'direction':
            send_command('Turn')
            logger.debug("Commande envoyée: Turn")
        elif jtype == 'move':
            if key == 'forward':
                send_command('Forward')
                logger.debug("Commande envoyée: Forward")
            elif key == 'backward':
                send_command('Backward')
                logger.debug("Commande envoyée: Backward")
            else:
                send_command('Move')
                logger.debug("Commande envoyée: Move")
        elif jtype == 'turn':
            if key == 'left':
                send_command('TurnLeft')
                logger.debug("Commande envoyée: TurnLeft")
            elif key == 'right':
                send_command('TurnRight')
                logger.debug("Commande envoyée: TurnRight")
            else:
                send_command('Turn')
                logger.debug("Commande envoyée: Turn")
        else:
            send_command('Move')
            logger.debug("Commande envoyée: Move (default)")

    return '', 204

@bp.route('/set_path', methods=['POST'])
@csrf.exempt
def set_path():
    path_coords = request.get_json(force=True)
    if not path_coords or not isinstance(path_coords, list):
        abort(400, description="Données de chemin invalides")

    logger.info(f"Nouveau chemin reçu: {path_coords}")
    # from .mqtt_sender import send_path
    # send_path(path_coords)
    return jsonify({"status": "ok"}), 200

@bp.route('/robot_position')
def robot_position():
    if not last_position:
        return jsonify({"error": "Position non disponible"}), 404
    return jsonify(last_position)

@bp.route('/robot_state')
def robot_state():
    state = get_state()
    if not state or state.get("mode") == "inconnu":
        return jsonify({"error": "État non disponible"}), 404
    return jsonify(state)

@bp.route('/robot_state/export')
def robot_state_export():
    state = get_state()
    if not state or state.get("mode") == "inconnu":
        return jsonify({"error": "État non disponible"}), 404
    response = jsonify(state)
    response.headers["Content-Disposition"] = "attachment; filename=robot_state.json"
    return response

@bp.route('/mqtt_status')
def mqtt_status():
    status = get_mqtt_status()
    return jsonify({"connected": status})

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

# Plus besoin de release_resources() pour la vidéo locale