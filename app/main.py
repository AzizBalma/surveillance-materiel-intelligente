# app/main.py
import eventlet
eventlet.monkey_patch()

import os
import logging
import time
from threading import Thread
from flask import Flask, render_template, jsonify, Response, send_file
from flask_socketio import SocketIO

from app.core.alert_system import AlertSystem
from app.core.system_monitor import SystemMonitor
from app.core.camera import Camera
from app.core.ml.predictor import Predictor

# Logging
os.makedirs("logs", exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.FileHandler("logs/surveillance.log"), logging.StreamHandler()]
)

app = Flask(__name__, template_folder="templates", static_folder="static")
socketio = SocketIO(app, cors_allowed_origins="*", async_mode="eventlet")

# Modules
alert_system = AlertSystem()
system_monitor = SystemMonitor(alert_system)
camera = Camera(alert_system, conf_threshold=0.5)
predictor = Predictor()

# --- Ensure add_alert compatibility ---
if not hasattr(alert_system, "add_alert") and hasattr(alert_system, "send_alert"):
    def _add_alert(alert_type, message, payload=None):
        try:
            return alert_system.send_alert(message, alert_type, payload)
        except Exception as e:
            logging.error("Fallback add_alert->send_alert failed: %s", e)
            return False
    alert_system.add_alert = _add_alert

# set emit callback if available
try:
    alert_system.set_emit_callback(lambda a: socketio.emit('new_alert', a))
except Exception:
    pass

state = {"metrics": {}, "alerts": []}

# Détecteur d'anomalies avec messages clairs
class SimpleAnomalyDetector:
    def __init__(self):
        self.anomaly_history = []
        
    def detect_anomalies(self, metrics, ml_predictions):
        """Détection simple avec messages clairs"""
        anomalies = []
        
        # 1. Vérification des seuils avec messages explicites
        cpu_usage = metrics.get('cpu_usage', 0)
        if cpu_usage > 90:
            anomalies.append({
                'type': 'cpu_attack',
                'severity': 'CRITICAL',
                'message': '🚨 CPU CRITIQUE - Attaque ou surcharge détectée',
                'cause': f'CPU utilisé à {cpu_usage}% (seuil: 90%)',
                'details': 'Le processeur est anormalement sollicité. Risque de cryptojacking ou malware.'
            })
        elif cpu_usage > 80:
            anomalies.append({
                'type': 'cpu_high',
                'severity': 'HIGH', 
                'message': '⚠️ CPU ÉLEVÉ - Surveillance requise',
                'cause': f'CPU utilisé à {cpu_usage}% (seuil: 80%)',
                'details': 'Utilisation CPU anormalement élevée pour la période actuelle.'
            })
            
        memory_usage = metrics.get('memory_usage', 0)
        if memory_usage > 90:
            anomalies.append({
                'type': 'memory_leak', 
                'severity': 'CRITICAL',
                'message': '🚨 MÉMOIRE CRITIQUE - Fuite mémoire détectée',
                'cause': f'Mémoire utilisée à {memory_usage}% (seuil: 90%)',
                'details': 'La mémoire RAM est saturée. Risque de crash système.'
            })
        elif memory_usage > 85:
            anomalies.append({
                'type': 'memory_high',
                'severity': 'HIGH',
                'message': '⚠️ MÉMOIRE ÉLEVÉE - Attention requise', 
                'cause': f'Mémoire utilisée à {memory_usage}% (seuil: 85%)',
                'details': 'Utilisation mémoire anormalement élevée.'
            })
            
        temperature = metrics.get('temperature', 0)
        if temperature > 80:
            anomalies.append({
                'type': 'thermal_emergency',
                'severity': 'CRITICAL', 
                'message': '🚨 SURCHAUFFE CRITIQUE - Arrêt imminent',
                'cause': f'Température CPU à {temperature}°C (seuil: 80°C)',
                'details': 'Le système risque de surchauffer. Arrêt d\'urgence recommandé.'
            })
        elif temperature > 75:
            anomalies.append({
                'type': 'thermal_warning',
                'severity': 'HIGH',
                'message': '⚠️ TEMPÉRATURE ÉLEVÉE - Refroidissement requis',
                'cause': f'Température CPU à {temperature}°C (seuil: 75°C)',
                'details': 'Le système chauffe anormalement.'
            })
            
        tcp_conn = metrics.get('tcp_conn', metrics.get('process_count', 0))
        if tcp_conn > 200:
            anomalies.append({
                'type': 'network_intrusion',
                'severity': 'HIGH',
                'message': '⚠️ ACTIVITÉ RÉSEAU SUSPECTE',
                'cause': f'{tcp_conn} connexions TCP actives (seuil: 200)',
                'details': 'Nombre anormal de connexions réseau. Possible intrusion.'
            })
            
        usb_status = str(metrics.get('usb_connected', 'Non')).lower()
        if usb_status in ('oui', 'yes', 'true', '1'):
            anomalies.append({
                'type': 'usb_breach',
                'severity': 'MEDIUM', 
                'message': '🔌 PÉRIPHÉRIQUE USB DÉTECTÉ',
                'cause': 'Device USB branché sans autorisation',
                'details': 'Un périphérique USB a été connecté hors surveillance.'
            })
        
        # 2. Vérification des prédictions ML avec messages clairs
        iforest_anomaly = ml_predictions.get('iforest_anomaly')
        iforest_score = ml_predictions.get('iforest_score', 0)
        
        if iforest_anomaly:
            anomalies.append({
                'type': 'ml_anomaly',
                'severity': 'HIGH',
                'message': '🤖 COMPORTEMENT ANORMAL DÉTECTÉ PAR IA',
                'cause': f'Score d\'anomalie: {iforest_score:.3f}',
                'details': 'L\'intelligence artificielle a détecté un comportement système inhabituel.'
            })
            
        return anomalies

# Initialisation du détecteur
anomaly_detector = SimpleAnomalyDetector()

# Routes
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/alerts")
def alerts_page():
    try:
        alerts = alert_system.get_recent_alerts(200)
    except Exception:
        alerts = getattr(alert_system, "alert_history", [])[:200]
    return render_template("alerts.html", alerts=alerts, update_time=time.strftime("%Y-%m-%d %H:%M:%S"))

@app.route("/api/status")
def api_status():
    return jsonify({
        "system_metrics": state.get("metrics", {}),
        "alerts": alert_system.get_recent_alerts(20)
    })

@app.route("/video_feed")
def video_feed():
    if hasattr(camera, "generator_mjpeg"):
        return Response(camera.generator_mjpeg(), mimetype='multipart/x-mixed-replace; boundary=frame')
    return "No MJPEG", 404

@app.route("/api/image/<path:filename>")
def api_image(filename):
    safe = os.path.basename(filename)
    path = os.path.join("visualizations", safe)
    if os.path.exists(path):
        return send_file(path, mimetype='image/jpeg')
    return ("Not found", 404)

# Threads
def camera_worker():
    try:
        camera.run_loop()
    except Exception as e:
        logging.error(f"Camera thread error: {e}")

def background_worker():
    while True:
        try:
            metrics = system_monitor.collect()
            state["metrics"] = metrics
            socketio.emit('system_update', {'system_metrics': metrics})
        except Exception as e:
            logging.error(f"Background thread error: {e}")
        time.sleep(5)

def ml_worker():
    logging.info("ML worker started with clear anomaly detection")
    
    while True:
        try:
            metrics = state.get("metrics") or {}
            if metrics:
                # Préparation des features pour le ML
                sample = {
                    "cpu_util": float(metrics.get("cpu_usage", 0)),
                    "mem_util": float(metrics.get("memory_usage", 0)),
                    "temp_cpu": float(metrics.get("temperature") if isinstance(metrics.get("temperature"), (int,float)) else 0),
                    "net_in_bytes": float(metrics.get("bytes_recv", 0)),
                    "net_out_bytes": float(metrics.get("bytes_sent", 0)),
                    "tcp_conn": float(metrics.get("process_count", 0)),
                    "user_active": float(metrics.get("user_active", 0)) if metrics.get("user_active") is not None else 0.0,
                    "usb_event": 1.0 if str(metrics.get("usb_connected","Non")).lower() in ("oui","yes","true","1") else 0.0
                }

                # Prédiction ML
                try:
                    ml_predictions = predictor.score(sample)
                except Exception as e:
                    logging.error("Predictor.score failed: %s", e)
                    ml_predictions = {}

                # Détection d'anomalies avec messages clairs
                anomalies = anomaly_detector.detect_anomalies(metrics, ml_predictions)
                
                # Émettre les mises à jour ML standard
                socketio.emit('ml_update', {'ml': ml_predictions})
                
                # Si anomalies détectées, émettre l'alerte avancée
                if anomalies:
                    # Trier par sévérité (CRITICAL d'abord)
                    severity_order = {'CRITICAL': 3, 'HIGH': 2, 'MEDIUM': 1, 'LOW': 0}
                    anomalies.sort(key=lambda x: severity_order.get(x['severity'], 0), reverse=True)
                    
                    anomaly_report = {
                        'timestamp': time.strftime("%Y-%m-%d %H:%M:%S"),
                        'total_anomalies': len(anomalies),
                        'critical_count': len([a for a in anomalies if a['severity'] == 'CRITICAL']),
                        'anomalies': anomalies
                    }
                    
                    # Émettre l'alerte pour l'interface
                    socketio.emit('advanced_anomaly', {
                        'report': anomaly_report
                    })
                    
                    # Déclencher les alertes système
                    for anomaly in anomalies:
                        try:
                            alert_system.add_alert(
                                f"anomaly_{anomaly['type']}",
                                f"{anomaly['message']} - {anomaly['cause']}",
                                {
                                    'severity': anomaly['severity'],
                                    'details': anomaly['details'],
                                    'timestamp': time.strftime("%Y-%m-%d %H:%M:%S")
                                }
                            )
                        except Exception as e:
                            logging.error("Unable to push anomaly alert: %s", e)

        except Exception as e:
            logging.error(f"ML worker error: {e}")
        
        time.sleep(10)

if __name__ == "__main__":
    Thread(target=camera_worker, daemon=True).start()
    Thread(target=background_worker, daemon=True).start()
    Thread(target=ml_worker, daemon=True).start()

    logging.info("🚀 Starting Surveillance System with Clear Anomaly Detection")
    socketio.run(app, host="0.0.0.0", port=5000, debug=False)
