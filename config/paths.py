"""
Gestion centralisée des chemins du projet.
Tous les modules doivent importer les chemins depuis ce fichier.
"""
import sys
from pathlib import Path

# Racine du projet (détection automatique)
PROJECT_ROOT = Path(__file__).parent.parent.resolve()

# Ajouter le dossier app au PYTHONPATH
sys.path.insert(0, str(PROJECT_ROOT / "app"))

# === STRUCTURE DES DOSSIERS ===

# Application
APP_DIR = PROJECT_ROOT / "app"
CORE_DIR = APP_DIR / "core"
ML_DIR = APP_DIR / "ml"
WEB_DIR = APP_DIR / "web"
TEMPLATES_DIR = APP_DIR / "templates"
STATIC_DIR = APP_DIR / "static"

# Données
DATA_DIR = PROJECT_ROOT / "data"
DATA_RAW_DIR = DATA_DIR / "raw"
DATA_PROCESSED_DIR = DATA_DIR / "processed"
DATA_SCRIPTS_DIR = DATA_DIR / "scripts"

# Modèles
MODELS_DIR = PROJECT_ROOT / "models"
VISION_MODEL_DIR = MODELS_DIR
ML_MODELS_DIR = MODELS_DIR / "ml"

# Outputs
OUTPUTS_DIR = PROJECT_ROOT / "outputs"
LOGS_DIR = OUTPUTS_DIR / "logs"
ALERTS_DIR = OUTPUTS_DIR / "alerts"
DETECTIONS_DIR = OUTPUTS_DIR / "detections"

# Visualisations
VIZ_DIR = PROJECT_ROOT / "visualizations"
VIZ_ML_DIR = VIZ_DIR / "ml"

# === FICHIERS SPÉCIFIQUES ===

# Modèles ML
VISION_MODEL = VISION_MODEL_DIR / "best.onnx"
CLASSIFIER_MODEL = ML_MODELS_DIR / "classifier.joblib"
IFOREST_MODEL = ML_MODELS_DIR / "iforest.joblib"
KMEANS_MODEL = ML_MODELS_DIR / "kmeans.joblib"
SCALER_MODEL = ML_MODELS_DIR / "scaler.joblib"

# Données
COMBINED_DATASET = DATA_PROCESSED_DIR / "donnees_ml_combined.csv"
RAW_DATASET = DATA_RAW_DIR / "donnees_ml.csv"
SIMULATED_DATASET = DATA_RAW_DIR / "simulated_ml_data.csv"

# Logs
SURVEILLANCE_LOG = LOGS_DIR / "surveillance.log"
ALERTS_LOG = ALERTS_DIR / "alerts.jsonl"

# === FONCTIONS UTILITAIRES ===

def ensure_directories():
    """Crée tous les dossiers nécessaires s'ils n'existent pas."""
    directories = [
        OUTPUTS_DIR, LOGS_DIR, ALERTS_DIR, DETECTIONS_DIR,
        DATA_RAW_DIR, DATA_PROCESSED_DIR, DATA_SCRIPTS_DIR,
        ML_MODELS_DIR, VIZ_ML_DIR, STATIC_DIR
    ]
    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)

def get_alert_log_path(alert_type):
    """Retourne le chemin du fichier de log pour un type d'alerte."""
    ensure_directories()
    return ALERTS_DIR / f"{alert_type}_alerts.jsonl"

def get_detection_image_path(timestamp):
    """Génère le chemin pour une image de détection."""
    ensure_directories()
    return DETECTIONS_DIR / f"detection_{timestamp}.jpg"

def get_model_path(model_name):
    """Retourne le chemin d'un modèle ML."""
    return ML_MODELS_DIR / f"{model_name}.joblib"

# Créer les dossiers au chargement du module
ensure_directories()

# Pour debug
if __name__ == "__main__":
    print(f"Racine du projet: {PROJECT_ROOT}")
    print(f"Modèle vision: {VISION_MODEL}")
    print(f"Dossier alertes: {ALERTS_DIR}")
