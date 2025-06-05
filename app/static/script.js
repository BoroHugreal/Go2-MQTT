        // Gestion du thème
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

        // Initialisation de la carte
        const pathCoords = [
            [48.777164396, 2.375696799],
            [48.777266135, 2.375488087],
            [48.777245920, 2.375302510],
            [48.777219946, 2.374943893]
        ];

        const map = L.map('map').setView(pathCoords[0], 19);
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            maxZoom: 22,
        }).addTo(map);

        // Initialisation du joystick
        const joystick = nipplejs.create({
            zone: document.getElementById('joystick-direction'),
            mode: 'static',
            position: {left: '50%', top: '50%'},
            color: '#007bff',
            size: 140
        });

        joystick.on('move', function (evt, data) {
            if (data && data.direction) {
                console.log('Joystick:', data.angle.degree, data.direction.angle);
                // Ici vous pouvez envoyer les commandes au robot
            }
        });

        joystick.on('end', function () {
            console.log('Joystick arrêté');
            // Arrêter le mouvement du robot
        });

        // Gestion des touches du clavier
        let activeKeys = new Set();

        document.addEventListener('keydown', function(e) {
            if (e.repeat) return;
            
            const key = e.key;
            if (['ArrowUp', 'ArrowDown', 'ArrowLeft', 'ArrowRight'].includes(key)) {
                e.preventDefault();
                activeKeys.add(key);
                
                // Visual feedback
                const keyMap = {
                    'ArrowUp': 'up',
                    'ArrowDown': 'down', 
                    'ArrowLeft': 'left',
                    'ArrowRight': 'right'
                };
                
                const element = document.querySelector(`.arrow-key.${keyMap[key]}`);
                if (element) {
                    element.style.background = 'var(--accent)';
                    element.style.color = 'white';
                }
                
                console.log('Touche pressée:', key);
                // Envoyer commande au robot
            }
        });

        document.addEventListener('keyup', function(e) {
            const key = e.key;
            if (activeKeys.has(key)) {
                activeKeys.delete(key);
                
                // Remove visual feedback
                const keyMap = {
                    'ArrowUp': 'up',
                    'ArrowDown': 'down',
                    'ArrowLeft': 'left', 
                    'ArrowRight': 'right'
                };
                
                const element = document.querySelector(`.arrow-key.${keyMap[key]}`);
                if (element) {
                    element.style.background = '';
                    element.style.color = '';
                }
                
                console.log('Touche relâchée:', key);
                // Arrêter commande au robot
            }
        });

        // Fonctions de contrôle
        function robotStop() {
            console.log('Robot STOP');
            alert('Commande STOP envoyée au robot');
        }

        function robotPause() {
            console.log('Robot PAUSE');
            alert('Commande PAUSE envoyée au robot');
        }

        function resetDistance() {
            document.getElementById('distance-value').textContent = '0.00';
            document.getElementById('distance-unit').textContent = 'm';
        }

        // Variables pour le tracé de chemin
        let drawingPath = false;
        let newPathCoords = [];
        let newPathLine = null;

        function toggleDrawing() {
            drawingPath = !drawingPath;
            document.getElementById('toggle-drawing').textContent = drawingPath ? "Arrêter le tracé" : "Activer le tracé";
            document.getElementById('send-path').disabled = !drawingPath;
            document.getElementById('clear-path').disabled = !drawingPath;
        }

        function sendPath() {
            if (newPathCoords.length < 2) {
                alert("Tracez au moins deux points !");
                return;
            }
            console.log('Chemin envoyé:', newPathCoords);
            alert("Chemin envoyé au robot !");
            toggleDrawing();
        }

        function clearPath() {
            newPathCoords = [];
            if (newPathLine) {
                map.removeLayer(newPathLine);
                newPathLine = null;
            }
        }

        map.on('click', function(e) {
            if (drawingPath) {
                newPathCoords.push([e.latlng.lat, e.latlng.lng]);
                if (newPathLine) {
                    newPathLine.setLatLngs(newPathCoords);
                } else {
                    newPathLine = L.polyline(newPathCoords, {color: 'green', weight: 4, dashArray: '5,10'}).addTo(map);
                }
            }
        });

// ========================
// Statut MQTT (header)
// ========================
function updateMqttStatus() {
    fetch('/mqtt_status')
        .then(response => response.json())
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
        .catch(() => {
            const statusElement = document.getElementById('mqtt-status-val');
            statusElement.textContent = 'Erreur';
            statusElement.className = 'mqtt-disconnected';
        });
}
setInterval(updateMqttStatus, 3000);
updateMqttStatus();

// ========================
// Statut vidéo (Go2)
// ========================
function updateVideoStatus() {
    fetch('/video_status')
        .then(r => r.json())
        .then(data => {
            const el = document.getElementById('video-status-val');
            if (data.mqtt_connected && data.has_frame) {
                el.textContent = "Flux actif";
                el.style.color = "#28a745";
            } else if (data.mqtt_connected) {
                el.textContent = "En attente du flux...";
                el.style.color = "#ffc107";
            } else {
                el.textContent = "MQTT déconnecté";
                el.style.color = "#dc3545";
            }
        })
        .catch(() => {
            const el = document.getElementById('video-status-val');
            el.textContent = "Erreur";
            el.style.color = "#dc3545";
        });
}
setInterval(updateVideoStatus, 4000);
updateVideoStatus();

// ========================
// Robustesse flux vidéo MJPEG
// ========================
const videoImg = document.getElementById('robot-video');
if (videoImg) {
    videoImg.onerror = function() {
        setTimeout(() => {
            videoImg.src = '/robot_video?' + new Date().getTime();
        }, 2000);
    };
}

// ========================
// Export du tracé (CSV, GeoJSON, KML)
// ========================
// Suppose que newPathCoords contient le chemin dessiné (ex: [[lat,lng], ...])
function exportPath(format) {
    if (!window.newPathCoords || newPathCoords.length === 0) {
        alert('Aucun tracé à exporter. Tracez un chemin d\'abord.');
        return;
    }
    const timestamp = new Date().toISOString().slice(0, 19).replace(/:/g, '-');
    let filename, content, mimeType;

    switch (format) {
        case 'csv':
            filename = `trace_go2_${timestamp}.csv`;
            content = generateCSV(newPathCoords);
            mimeType = 'text/csv';
            break;
        case 'geojson':
            filename = `trace_go2_${timestamp}.geojson`;
            content = generateGeoJSON(newPathCoords);
            mimeType = 'application/json';
            break;
        case 'kml':
            filename = `trace_go2_${timestamp}.kml`;
            content = generateKML(newPathCoords);
            mimeType = 'application/vnd.google-earth.kml+xml';
            break;
        default:
            alert('Format non supporté');
            return;
    }
    downloadFile(content, filename, mimeType);
}

function generateCSV(path) {
    let csv = 'Latitude,Longitude,Point\n';
    path.forEach((point, index) => {
        csv += `${point[0]},${point[1]},${index + 1}\n`;
    });
    return csv;
}

function generateGeoJSON(path) {
    const geojson = {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "properties": {
                    "name": "Tracé du robot Go2",
                    "timestamp": new Date().toISOString(),
                    "points_count": path.length
                },
                "geometry": {
                    "type": "LineString",
                    "coordinates": path.map(point => [point[1], point[0]])
                }
            }
        ]
    };
    return JSON.stringify(geojson, null, 2);
}

function generateKML(path) {
    const coordinates = path.map(point => `${point[1]},${point[0]},0`).join(' ');
    const kml = `<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://www.opengis.net/kml/2.2">
  <Document>
    <name>Tracé du robot Go2</name>
    <description>Tracé généré le ${new Date().toLocaleString()}</description>
    <Placemark>
      <name>Parcours du robot</name>
      <LineString>
        <coordinates>${coordinates}</coordinates>
      </LineString>
    </Placemark>
  </Document>
</kml>`;
    return kml;
}

function downloadFile(content, filename, mimeType) {
    const blob = new Blob([content], { type: mimeType });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
}

// Simulation de mise à jour des données
setInterval(function() {
    const battery = Math.floor(Math.random() * 30) + 70;
    const speed = (Math.random() * 2).toFixed(2);
    document.getElementById('header-battery-val').textContent = battery;
    document.getElementById('speed-value').textContent = speed;
}, 3000);

document.querySelectorAll('nav a[href^="#"]').forEach(link => {
    link.addEventListener('click', function(e) {
        const targetId = this.getAttribute('href').replace('#', '');
        const target = document.getElementById(targetId);
        if (target) {
            e.preventDefault();
            target.scrollIntoView({ behavior: 'smooth' });
            setTimeout(() => target.focus(), 600); // met le focus après le scroll
        }
    });
});