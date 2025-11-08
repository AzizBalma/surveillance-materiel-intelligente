import psutil
import subprocess
import platform

class SystemMonitor:
    def __init__(self, alert_system=None):
        self.alert_system = alert_system

    def collect(self):
        """Collecte les métriques système en temps réel."""
        metrics = {}

        # 🔹 Utilisation CPU
        metrics["cpu_usage"] = psutil.cpu_percent(interval=None)

        # 🔹 Utilisation mémoire
        memory = psutil.virtual_memory()
        metrics["memory_usage"] = memory.percent

        # 🔹 Nombre de processus
        metrics["process_count"] = len(psutil.pids())

        # 🔹 Température CPU (si supportée)
        try:
            temps = psutil.sensors_temperatures()
            if temps:
                # On prend le premier capteur disponible
                for name, entries in temps.items():
                    metrics["temperature"] = round(entries[0].current, 1)
                    break
            else:
                metrics["temperature"] = "N/A"
        except Exception:
            metrics["temperature"] = "N/A"

        # 🔹 Réseau (octets envoyés / reçus)
        net = psutil.net_io_counters()
        metrics["bytes_sent"] = net.bytes_sent
        metrics["bytes_recv"] = net.bytes_recv

        # 🔹 Clé USB connectée (Linux)
        try:
            output = subprocess.check_output("lsblk -o NAME,TYPE | grep 'disk'", shell=True).decode()
            usb_connected = any("sd" in line for line in output.splitlines())
            metrics["usb_connected"] = "Oui" if usb_connected else "Non"
        except Exception:
            metrics["usb_connected"] = "Inconnu"

        # 🔹 Optionnel : alertes sur surchauffe ou surcharge
        if self.alert_system:
            if metrics["cpu_usage"] > 90:
                self.alert_system.add_alert("cpu_warning", "Utilisation CPU > 90%")
            if metrics["memory_usage"] > 90:
                self.alert_system.add_alert("memory_warning", "Utilisation RAM > 90%")
            if isinstance(metrics["temperature"], (int, float)) and metrics["temperature"] > 75:
                self.alert_system.add_alert("temp_warning", f"Température élevée: {metrics['temperature']}°C")

        return metrics
