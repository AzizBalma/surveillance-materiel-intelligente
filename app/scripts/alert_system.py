import os
import json
import logging
from datetime import datetime
from typing import Optional, Callable

os.makedirs("alerts", exist_ok=True)

class AlertSystem:
    def __init__(self):
        self.alert_history = []
        self.alert_cooldowns = {
            "camera_intrusion": 300,
            "network_intrusion": 60,
            "system_anomaly": 300,
            "camera_simulation": 600
        }
        self.last_alert_time = {}
        self.emit_callback: Optional[Callable[[dict], None]] = None

    def set_emit_callback(self, fn: Callable[[dict], None]):
        self.emit_callback = fn

    def send_alert(self, message: str, alert_type: str, data: dict = None) -> bool:
        now = datetime.utcnow()
        cooldown = self.alert_cooldowns.get(alert_type, 300)
        last = self.last_alert_time.get(alert_type)
        if last and (now - last).total_seconds() < cooldown:
            return False

        alert = {
            "id": len(self.alert_history) + 1,
            "timestamp": now.isoformat(),
            "formatted_time": now.strftime("%Y-%m-%d %H:%M:%S"),
            "type": alert_type,
            "message": message,
            "data": data or {},
            "priority": self._determine_priority(alert_type, data)
        }

        logging.warning(f"🚨 ALERTE [{alert_type}] {message} | {data}")
        self.alert_history.append(alert)
        self._save_alert(alert)
        self.last_alert_time[alert_type] = now

        if self.emit_callback:
            try:
                self.emit_callback(alert)
            except Exception as e:
                logging.error(f"Erreur emit alert: {e}")

        return True

    def _determine_priority(self, alert_type, data):
        mapping = {
            "network_intrusion": "HIGH",
            "camera_intrusion": "HIGH",
            "system_anomaly": "MEDIUM",
            "camera_simulation": "LOW"
        }
        p = mapping.get(alert_type, "MEDIUM")
        if alert_type == "system_anomaly" and data:
            if data.get("cpu_usage", 0) > 95 or data.get("memory_usage", 0) > 95:
                p = "HIGH"
        return p

    def _save_alert(self, alert):
        try:
            with open("alerts/alerts.jsonl", "a") as f:
                f.write(json.dumps(alert, default=str) + "\n")
            with open(f"alerts/{alert['type']}_alerts.jsonl", "a") as f:
                f.write(json.dumps(alert, default=str) + "\n")
        except Exception as e:
            logging.error(f"Erreur sauvegarde alerte: {e}")

    def get_recent_alerts(self, count=50):
        return list(reversed(self.alert_history))[:count]

    def get_alert_count(self):
        return len(self.alert_history)
