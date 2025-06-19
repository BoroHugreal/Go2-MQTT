// ========================
// Gestion du thème
// ========================
document.addEventListener("DOMContentLoaded", function() {
    const toggle = document.getElementById('theme-toggle');
    const html = document.documentElement;
    const savedTheme = localStorage.getItem('theme');
    if (savedTheme === 'dark' || (!savedTheme && window.matchMedia('(prefers-color-scheme: dark)').matches)) {
        html.classList.add('dark');
        toggle.checked = true;
    }
    toggle.addEventListener('change', function() {
        if (this.checked) {
            html.classList.add('dark');
            localStorage.setItem('theme', 'dark');
        } else {
            html.classList.remove('dark');
            localStorage.setItem('theme', 'light');
        }
    });
});

// ========================
// Commandes rapides (formulaire)
// ========================
document.getElementById('command-form').addEventListener('submit', function(e) {
    e.preventDefault();
    const command = document.getElementById('command').value;
    const feedback = document.getElementById('command-feedback');
    fetch('/', {
        method: 'POST',
        body: new FormData(this)
    }).then(res => {
        if (res.ok) {
            feedback.textContent = "Commande envoyée avec succès !";
            feedback.className = "feedback success";
        } else {
            feedback.textContent = "Erreur lors de l'envoi de la commande.";
            feedback.className = "feedback error";
        }
        setTimeout(() => feedback.textContent = "", 3000);
    });
});

// ========================
// Carte Google Maps & tracé de chemin
// ========================

let map;
let drawingPath = false;
let newPathCoords = [];
let newPathPolyline = null;

window.initMap = function() {
    // Centrage sur l'endroit souhaité
    const center = {lat: 48.777164396, lng: 2.375696799};
    map = new google.maps.Map(document.getElementById('map'), {
        zoom: 19,
        center: center,
        mapTypeId: 'satellite'
    });

    // Gestion du clic pour tracer le chemin
    map.addListener('click', function(e) {
        if (!drawingPath) return;
        const latlng = {lat: e.latLng.lat(), lng: e.latLng.lng()};
        newPathCoords.push(latlng);

        if (newPathPolyline) {
            newPathPolyline.setPath(newPathCoords);
        } else {
            newPathPolyline = new google.maps.Polyline({
                path: newPathCoords,
                geodesic: true,
                strokeColor: '#00cc00',
                strokeOpacity: 1.0,
                strokeWeight: 4,
                map: map
            });
        }
    });
};

window.toggleDrawing = function() {
    drawingPath = !drawingPath;
    document.getElementById('toggle-drawing').textContent = drawingPath ? "Arrêter le tracé" : "Activer le tracé";
    document.getElementById('send-path').disabled = !drawingPath;
    document.getElementById('clear-path').disabled = !drawingPath;
    if (!drawingPath) clearPath();
};

window.sendPath = function() {
    if (newPathCoords.length < 2) {
        alert("Tracez au moins deux points !");
        return;
    }
    // Conversion en tableau de [lat, lng] pour compatibilité backend
    const coordsToSend = newPathCoords.map(pt => [pt.lat, pt.lng]);
    fetch('/set_path', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify(coordsToSend)
    })
    .then(res => res.json())
    .then(data => {
        if (data.status === "ok") {
            alert("Chemin envoyé au robot !");
            clearPath();
            toggleDrawing();
        } else {
            alert("Erreur lors de l'envoi du chemin !");
        }
    });
};

window.clearPath = function() {
    newPathCoords = [];
    if (newPathPolyline) {
        newPathPolyline.setMap(null);
        newPathPolyline = null;
    }
};

window.exportPath = function(format) {
    if (newPathCoords.length < 2) {
        alert("Rien à exporter !");
        return;
    }
    let dataStr = "";
    if (format === "csv") {
        dataStr = "lat,lng\n" + newPathCoords.map(pt => `${pt.lat},${pt.lng}`).join("\n");
    } else if (format === "geojson") {
        dataStr = JSON.stringify({
            type: "LineString",
            coordinates: newPathCoords.map(pt => [pt.lng, pt.lat])
        }, null, 2);
    } else if (format === "kml") {
        dataStr = `<?xml version="1.0" encoding="UTF-8"?><kml xmlns="http://www.opengis.net/kml/2.2"><Placemark><LineString><coordinates>${newPathCoords.map(pt => pt.lng+","+pt.lat+",0").join(" ")}</coordinates></LineString></Placemark></kml>`;
    }
    const blob = new Blob([dataStr], {type: "text/plain"});
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `path.${format}`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
};

// ========================
// Export du chemin (exemple simple)
// ========================
window.exportPath = function(format) {
    if (newPathCoords.length < 2) {
        alert("Rien à exporter !");
        return;
    }
    let dataStr = "";
    if (format === "csv") {
        dataStr = "lat,lng\n" + newPathCoords.map(pt => pt.join(",")).join("\n");
    } else if (format === "geojson") {
        dataStr = JSON.stringify({
            type: "LineString",
            coordinates: newPathCoords.map(pt => [pt[1], pt[0]])
        }, null, 2);
    } else if (format === "kml") {
        dataStr = `<?xml version="1.0" encoding="UTF-8"?><kml xmlns="http://www.opengis.net/kml/2.2"><Placemark><LineString><coordinates>${newPathCoords.map(pt => pt[1]+","+pt[0]+",0").join(" ")}</coordinates></LineString></Placemark></kml>`;
    }
    const blob = new Blob([dataStr], {type: "text/plain"});
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `path.${format}`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
};

// ========================
// Joystick (NippleJS) et clavier améliorés
// ========================
// Mapping angle/label NippleJS vers commandes robot
function joystickDirectionToCommand(direction) {
    switch (direction) {
        case 'up': return {type: 'move', key: 'forward'};
        case 'down': return {type: 'move', key: 'backward'};
        case 'left': return {type: 'turn', key: 'left'};
        case 'right': return {type: 'turn', key: 'right'};
        default: return {type: 'move', key: 'forward'};
    }
}

const joystick = nipplejs.create({
    zone: document.getElementById('joystick-direction'),
    mode: 'static',
    position: {left: '50%', top: '50%'},
    color: '#007bff',
    size: 140
});

// Envoi la commande à Flask/MQTT
function sendJoystickCommand(type, key, stop = false) {
    fetch('/joystick', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({type, key, stop})
    });
}

// Joystick NippleJS
joystick.on('move', function (evt, data) {
    if (data && data.direction && data.direction.angle) {
        const mapping = joystickDirectionToCommand(data.direction.angle);
        sendJoystickCommand(mapping.type, mapping.key, false);
    }
});
joystick.on('end', function () {
    // Stoppe le robot quand on relâche le joystick
    sendJoystickCommand('move', null, true);
});

// ========================
// Clavier (flèches)
// ========================
let activeKeys = new Set();
const keyMap = {
    'ArrowUp':   {type: 'move', key: 'forward',  css: 'up'},
    'ArrowDown': {type: 'move', key: 'backward', css: 'down'},
    'ArrowLeft': {type: 'turn', key: 'left',     css: 'left'},
    'ArrowRight':{type: 'turn', key: 'right',    css: 'right'}
};

document.addEventListener('keydown', function(e) {
    if (e.repeat) return;
    const mapping = keyMap[e.key];
    if (mapping) {
        e.preventDefault();
        if (!activeKeys.has(e.key)) {
            activeKeys.add(e.key);
            // Feedback visuel
            const element = document.querySelector(`.arrow-key.${mapping.css}`);
            if (element) {
                element.style.background = 'var(--accent)';
                element.style.color = 'white';
            }
            sendJoystickCommand(mapping.type, mapping.key, false);
        }
    }
});

document.addEventListener('keyup', function(e) {
    const mapping = keyMap[e.key];
    if (mapping && activeKeys.has(e.key)) {
        activeKeys.delete(e.key);
        // Retire le feedback visuel
        const element = document.querySelector(`.arrow-key.${mapping.css}`);
        if (element) {
            element.style.background = '';
            element.style.color = '';
        }
        sendJoystickCommand(mapping.type, mapping.key, true);
    }
});

// ========================
// STOP/PAUSE boutons
// ========================
window.robotStop = function() {
    fetch('/robot_stop', {method: 'POST'})
        .then(res => res.json())
        .then(data => alert(data.message));
};
window.robotPause = function() {
    fetch('/robot_pause', {method: 'POST'})
        .then(res => res.json())
        .then(data => alert(data.message));
};

// ========================
// Statut MQTT (header)
// ========================
function updateMqttStatus() {
    fetch('/mqtt_status')
        .then(response => {
            if (!response.ok) throw new Error('Serveur non disponible');
            return response.json();
        })
        .then(data => {
            const statusElement = document.getElementById('mqtt-status-val');
            if (data.connected) {
                statusElement.textContent = 'Connecté';
                statusElement.className = 'mqtt-connected';
            } else {
                statusElement.textContent = 'Déconnecté';
                statusElement.className = 'mqtt-disconnected';
            }
        })
        .catch(error => {
            const statusElement = document.getElementById('mqtt-status-val');
            statusElement.textContent = 'Erreur réseau';
            statusElement.className = 'mqtt-disconnected';
            console.error("Erreur de connexion MQTT :", error);
        });
}

setInterval(updateMqttStatus, 5000);
updateMqttStatus();

// ========================
// Statut vidéo (rafraîchissement automatique)
// ========================
function updateVideoStatus() {
    fetch('/video_status')
        .then(response => {
            if (!response.ok) throw new Error('Serveur non disponible');
            return response.json();
        })
        .then(data => {
            const statusElement = document.getElementById('video-status-val');
            if (data.has_frame) {
                statusElement.textContent = 'Flux actif';
                statusElement.className = 'video-status-active';
            } else {
                statusElement.textContent = 'Aucune image reçue';
                statusElement.className = 'video-status-inactive';
            }
            if (!data.mqtt_connected) {
                statusElement.textContent = 'MQTT déconnecté';
                statusElement.className = 'video-status-inactive';
            }
        })
        .catch(error => {
            const statusElement = document.getElementById('video-status-val');
            statusElement.textContent = 'Serveur non disponible';
            statusElement.className = 'video-status-inactive';
        });
}

// Rafraîchir le statut vidéo toutes les 3 secondes
setInterval(updateVideoStatus, 3000);
updateVideoStatus(); // Appel initial


// ========================
// Divers
// ========================
window.resetDistance = function() {
    document.getElementById('distance-value').textContent = '0.00';
    document.getElementById('distance-unit').textContent = 'm';
};