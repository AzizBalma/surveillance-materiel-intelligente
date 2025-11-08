"""
Script de Migration Automatique - Surveillance Matériel
Réorganise le projet sans casser les chemins existants
Usage: python migrate_project.py
"""

import os
import shutil
import sys
from pathlib import Path
from datetime import datetime
import re

class ColorPrint:
    """Classe pour afficher des messages colorés dans le terminal."""
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

    @staticmethod
    def print_header(msg):
        print(f"\n{ColorPrint.HEADER}{ColorPrint.BOLD}{msg}{ColorPrint.ENDC}")
    
    @staticmethod
    def print_success(msg):
        print(f"{ColorPrint.OKGREEN}✓ {msg}{ColorPrint.ENDC}")
    
    @staticmethod
    def print_info(msg):
        print(f"{ColorPrint.OKBLUE}ℹ {msg}{ColorPrint.ENDC}")
    
    @staticmethod
    def print_warning(msg):
        print(f"{ColorPrint.WARNING}⚠ {msg}{ColorPrint.ENDC}")
    
    @staticmethod
    def print_error(msg):
        print(f"{ColorPrint.FAIL}✗ {msg}{ColorPrint.ENDC}")


class ProjectMigrator:
    """Classe principale pour la migration du projet."""
    
    def __init__(self, project_root=None):
        self.root = Path(project_root) if project_root else Path.cwd()
        self.backup_dir = self.root.parent / f"{self.root.name}_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.dry_run = False
        
    def check_project_structure(self):
        """Vérifie que nous sommes dans le bon projet."""
        ColorPrint.print_header("🔍 VÉRIFICATION DE LA STRUCTURE DU PROJET")
        
        required_files = ["app/main.py", "models/best.onnx", "data"]
        missing = []
        
        for file in required_files:
            if not (self.root / file).exists():
                missing.append(file)
        
        if missing:
            ColorPrint.print_error(f"Structure incorrecte. Fichiers manquants: {missing}")
            return False
        
        ColorPrint.print_success("Structure du projet valide")
        return True
    
    def create_backup(self):
        """Crée une sauvegarde complète du projet."""
        ColorPrint.print_header("📦 CRÉATION DE LA SAUVEGARDE")
        
        try:
            # Exclure les dossiers inutiles
            def ignore_patterns(dir, files):
                return ['__pycache__', 'venv', 'env', '.git', 'node_modules']
            
            shutil.copytree(
                self.root, 
                self.backup_dir,
                ignore=ignore_patterns,
                dirs_exist_ok=True
            )
            ColorPrint.print_success(f"Sauvegarde créée: {self.backup_dir}")
            return True
        except Exception as e:
            ColorPrint.print_error(f"Erreur lors de la sauvegarde: {e}")
            return False
    
    def create_new_structure(self):
        """Crée la nouvelle structure de dossiers."""
        ColorPrint.print_header("🏗️ CRÉATION DE LA NOUVELLE STRUCTURE")
        
        new_dirs = [
            "config",
            "app/core",
            "app/ml", 
            "app/web",
            "app/utils",
            "app/static/css",
            "app/static/js",
            "app/static/images",
            "data/raw",
            "data/processed",
            "data/scripts",
            "outputs/logs",
            "outputs/alerts",
            "outputs/detections",
            "scripts",
            "tests",
            "docs",
        ]
        
        for dir_path in new_dirs:
            full_path = self.root / dir_path
            full_path.mkdir(parents=True, exist_ok=True)
            
            # Créer __init__.py pour les packages Python
            if dir_path.startswith("app/") or dir_path == "config":
                init_file = full_path / "__init__.py"
                if not init_file.exists():
                    init_file.write_text("")
        
        ColorPrint.print_success(f"Créé {len(new_dirs)} nouveaux dossiers")
        return True
    
    def migrate_files(self):
        """Migre les fichiers vers leur nouvelle location."""
        ColorPrint.print_header("📦 MIGRATION DES FICHIERS")
        
        migrations = {
            # Scripts core
            "app/scripts/camera.py": "app/core/camera.py",
            "app/scripts/system_monitor.py": "app/core/system_monitor.py",
            "app/scripts/network_detector.py": "app/core/network_detector.py",
            "app/scripts/alert_system.py": "app/core/alert_system.py",
            
            # ML
            "app/scripts/ml/predictor.py": "app/ml/predictor.py",
            "app/scripts/ml/train_models.py": "app/ml/train_models.py",
            "app/scripts/ml/train_models_or.py": "app/ml/train_models_original.py",
            "app/scripts/trainer/train_supervided.py": "app/ml/train_supervised.py",
            "app/scripts/trainer/unsupervised.py": "app/ml/train_unsupervised.py",
            
            # Data
            "data/combinaison_dataset.py": "data/scripts/combine_datasets.py",
            "simulation_données.py": "data/scripts/generate_simulated_data.py",
            "data/donnees_ml.csv": "data/raw/donnees_ml.csv",
            "data/simulated_ml_data.csv": "data/raw/simulated_ml_data.csv",
            "data/donnees_ml_combined.csv": "data/processed/donnees_ml_combined.csv",
            
            # Logs et alertes
            "app/logs/surveillance.log": "outputs/logs/surveillance.log",
            
            # Docker
            "docker-compose.yml": "docker/docker-compose.yml",
            "deploy.sh": "scripts/deploy.sh",
            
            # Documentation
            "images": "docs/images",
        }
        
        migrated_count = 0
        
        for source, dest in migrations.items():
            src_path = self.root / source
            dest_path = self.root / dest
            
            if src_path.exists():
                try:
                    dest_path.parent.mkdir(parents=True, exist_ok=True)
                    
                    if src_path.is_dir():
                        if dest_path.exists():
                            shutil.rmtree(dest_path)
                        shutil.copytree(src_path, dest_path)
                    else:
                        shutil.copy2(src_path, dest_path)
                    
                    ColorPrint.print_success(f"{source} → {dest}")
                    migrated_count += 1
                except Exception as e:
                    ColorPrint.print_warning(f"Erreur: {source} - {e}")
        
        # Migrer toutes les alertes
        alerts_src = self.root / "app/alerts"
        if alerts_src.exists():
            for alert_file in alerts_src.glob("*.jsonl"):
                dest = self.root / "outputs/alerts" / alert_file.name
                shutil.copy2(alert_file, dest)
                migrated_count += 1
        
        # Migrer les détections
        detections_src = self.root / "app/visualizations"
        if detections_src.exists():
            for img_file in detections_src.glob("detection_*.jpg"):
                dest = self.root / "outputs/detections" / img_file.name
                shutil.copy2(img_file, dest)
                migrated_count += 1
        
        ColorPrint.print_success(f"Migré {migrated_count} fichiers")
        return True
    
    def create_paths_module(self):
        """Crée le module config/paths.py."""
        ColorPrint.print_header("⚙️ CRÉATION DU MODULE DE CHEMINS")
        
        paths_content = '''"""
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
'''
        
        paths_file = self.root / "config/paths.py"
        paths_file.write_text(paths_content, encoding='utf-8')
        
        ColorPrint.print_success("Module config/paths.py créé")
        return True
    
    def update_imports(self):
        """Met à jour tous les imports dans les fichiers Python."""
        ColorPrint.print_header("🔄 MISE À JOUR DES IMPORTS")
        
        # Mapping des anciens imports vers les nouveaux
        import_mappings = {
            r'from scripts\.': 'from app.core.',
            r'from scripts\.ml\.': 'from app.ml.',
            r'import scripts\.': 'import app.core.',
            r'from app\.scripts\.': 'from app.core.',
            r'from app\.scripts\.ml\.': 'from app.ml.',
        }
        
        # Trouver tous les fichiers Python
        python_files = []
        for pattern in ['app/**/*.py', 'data/scripts/*.py', 'scripts/*.py']:
            python_files.extend(self.root.glob(pattern))
        
        updated_count = 0
        
        for py_file in python_files:
            if '__pycache__' in str(py_file) or 'venv' in str(py_file):
                continue
            
            try:
                content = py_file.read_text(encoding='utf-8')
                original_content = content
                
                # Appliquer tous les mappings
                for old_pattern, new_import in import_mappings.items():
                    content = re.sub(old_pattern, new_import, content)
                
                # Ajouter l'import du module paths si nécessaire
                if 'app/alerts' in content or 'app/logs' in content or 'models/' in content:
                    if 'from config.paths import' not in content:
                        # Ajouter après les imports standards
                        lines = content.split('\n')
                        import_index = 0
                        for i, line in enumerate(lines):
                            if line.startswith('import ') or line.startswith('from '):
                                import_index = i + 1
                        
                        lines.insert(import_index, '\nfrom config.paths import *\n')
                        content = '\n'.join(lines)
                
                if content != original_content:
                    py_file.write_text(content, encoding='utf-8')
                    ColorPrint.print_success(f"Mis à jour: {py_file.relative_to(self.root)}")
                    updated_count += 1
                    
            except Exception as e:
                ColorPrint.print_warning(f"Erreur sur {py_file.name}: {e}")
        
        ColorPrint.print_success(f"Mis à jour {updated_count} fichiers Python")
        return True
    
    def update_path_references(self):
        """Remplace les références de chemins en dur."""
        ColorPrint.print_header("📝 MISE À JOUR DES CHEMINS EN DUR")
        
        path_replacements = {
            r'"app/alerts/"': 'str(ALERTS_DIR) + "/"',
            r'"app/logs/"': 'str(LOGS_DIR) + "/"',
            r'"app/visualizations/"': 'str(DETECTIONS_DIR) + "/"',
            r'"models/ml/"': 'str(ML_MODELS_DIR) + "/"',
            r'"models/best\.onnx"': 'str(VISION_MODEL)',
            r'"data/donnees_ml_combined\.csv"': 'str(COMBINED_DATASET)',
            r'[\'"]app/alerts/': 'str(ALERTS_DIR) + "/',
        }
        
        python_files = list(self.root.glob('app/**/*.py'))
        updated_count = 0
        
        for py_file in python_files:
            if '__pycache__' in str(py_file):
                continue
            
            try:
                content = py_file.read_text(encoding='utf-8')
                original_content = content
                
                for old_path, new_path in path_replacements.items():
                    content = re.sub(old_path, new_path, content)
                
                if content != original_content:
                    py_file.write_text(content, encoding='utf-8')
                    updated_count += 1
                    
            except Exception as e:
                ColorPrint.print_warning(f"Erreur: {e}")
        
        ColorPrint.print_success(f"Mis à jour {updated_count} références de chemins")
        return True
    
    def create_gitignore(self):
        """Crée un fichier .gitignore complet."""
        ColorPrint.print_header("📄 CRÉATION DU .gitignore")
        
        gitignore_content = '''# Python
__pycache__/
*.py[cod]
*$py.class
*.so
*.pyc
.Python
env/
venv/
ENV/
build/
dist/
*.egg-info/

# IDEs
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Project specific
outputs/logs/*.log
outputs/alerts/*.jsonl
outputs/detections/*.jpg
!outputs/**/.gitkeep

# Models (optional - décommenter pour versionner)
# *.onnx
# models/**/*.joblib
# models/**/*.pkl

# Environment
.env
config/config.local.yaml

# Data
data/raw/*.csv
!data/raw/.gitkeep
data/processed/*.csv
!data/processed/.gitkeep

# Temporary
*.tmp
*.bak
*~

# Backup
*_backup_*/
'''
        
        gitignore_file = self.root / ".gitignore"
        gitignore_file.write_text(gitignore_content, encoding='utf-8')
        
        ColorPrint.print_success(".gitignore créé")
        return True
    
    def create_env_example(self):
        """Crée un fichier .env.example."""
        ColorPrint.print_header("📄 CRÉATION DU .env.example")
        
        env_content = '''# Configuration de l'application
FLASK_ENV=production
SECRET_KEY=your_secret_key_here
DEBUG=False

# Caméra
CAMERA_DEVICE=0
CAMERA_RESOLUTION_WIDTH=640
CAMERA_RESOLUTION_HEIGHT=480
DETECTION_CONFIDENCE=0.6

# Monitoring
MONITORING_INTERVAL=5
CPU_THRESHOLD=90
MEMORY_THRESHOLD=90
TEMP_THRESHOLD=80

# Alertes
ALERT_COOLDOWN=300

# Chemins (optionnel - utilise config/paths.py par défaut)
# MODEL_PATH=models/
# LOG_PATH=outputs/logs/
'''
        
        env_file = self.root / ".env.example"
        env_file.write_text(env_content, encoding='utf-8')
        
        ColorPrint.print_success(".env.example créé")
        return True
    
    def cleanup_old_structure(self):
        """Nettoie l'ancienne structure."""
        ColorPrint.print_header("🧹 NETTOYAGE DE L'ANCIENNE STRUCTURE")
        
        # Supprimer les __pycache__
        pycache_count = 0
        for pycache in self.root.rglob('__pycache__'):
            shutil.rmtree(pycache, ignore_errors=True)
            pycache_count += 1
        
        ColorPrint.print_success(f"Supprimé {pycache_count} dossiers __pycache__")
        
        # Supprimer les anciens dossiers vides
        old_dirs = [
            "app/scripts/ml",
            "app/scripts/trainer",
            "app/scripts",
            "app/alerts",
            "app/logs",
            "app/visualizations/ml",
            "app/visualizations",
        ]
        
        removed_count = 0
        for old_dir in old_dirs:
            dir_path = self.root / old_dir
            if dir_path.exists():
                try:
                    # Vérifier si vide
                    if not any(dir_path.iterdir()):
                        dir_path.rmdir()
                        ColorPrint.print_info(f"Supprimé: {old_dir}")
                        removed_count += 1
                except Exception as e:
                    ColorPrint.print_warning(f"Ne peut pas supprimer {old_dir}: {e}")
        
        ColorPrint.print_success(f"Supprimé {removed_count} dossiers vides")
        return True
    
    def create_keepfiles(self):
        """Crée des fichiers .gitkeep dans les dossiers vides."""
        keep_dirs = [
            "outputs/logs",
            "outputs/alerts", 
            "outputs/detections",
            "data/raw",
            "data/processed",
            "tests",
            "docs",
        ]
        
        for dir_path in keep_dirs:
            full_path = self.root / dir_path
            if full_path.exists():
                (full_path / ".gitkeep").touch()
    
    def verify_structure(self):
        """Vérifie que la nouvelle structure est correcte."""
        ColorPrint.print_header("✅ VÉRIFICATION DE LA NOUVELLE STRUCTURE")
        
        required_structure = {
            "config/paths.py": "fichier",
            "app/core": "dossier",
            "app/ml": "dossier",
            "outputs/logs": "dossier",
            "outputs/alerts": "dossier",
            "models/best.onnx": "fichier",
        }
        
        all_good = True
        for path, type_ in required_structure.items():
            full_path = self.root / path
            
            if type_ == "fichier" and not full_path.is_file():
                ColorPrint.print_error(f"Fichier manquant: {path}")
                all_good = False
            elif type_ == "dossier" and not full_path.is_dir():
                ColorPrint.print_error(f"Dossier manquant: {path}")
                all_good = False
            else:
                ColorPrint.print_success(f"OK: {path}")
        
        return all_good
    
    def run(self):
        """Exécute la migration complète."""
        ColorPrint.print_header("🚀 DÉBUT DE LA MIGRATION AUTOMATIQUE")
        ColorPrint.print_info(f"Dossier du projet: {self.root}")
        
        # Demander confirmation
        print("\nCette opération va réorganiser votre projet.")
        print(f"Une sauvegarde sera créée dans: {self.backup_dir}")
        response = input("\nContinuer? (o/n): ")
        
        if response.lower() not in ['o', 'oui', 'y', 'yes']:
            ColorPrint.print_warning("Migration annulée")
            return False
        
        try:
            # Étapes de migration
            steps = [
                ("Vérification", self.check_project_structure),
                ("Sauvegarde", self.create_backup),
                ("Nouvelle structure", self.create_new_structure),
                ("Migration fichiers", self.migrate_files),
                ("Module paths", self.create_paths_module),
                ("Imports", self.update_imports),
                ("Chemins", self.update_path_references),
                (".gitignore", self.create_gitignore),
                (".env.example", self.create_env_example),
                (".gitkeep", self.create_keepfiles),
                ("Nettoyage", self.cleanup_old_structure),
                ("Vérification finale", self.verify_structure),
            ]
            
            for step_name, step_func in steps:
                if not step_func():
                    ColorPrint.print_error(f"Échec à l'étape: {step_name}")
                    return False
            
            # Succès!
            ColorPrint.print_header("✅ MIGRATION TERMINÉE AVEC SUCCÈS!")
            
            print(f"\n📁 Sauvegarde: {self.backup_dir}")
            print("\n🎯 Prochaines étapes:")
            print("  1. Tester l'application:")
            print("     python app/main.py")
            print("\n  2. Si tout fonctionne:")
            print(f"     - Vous pouvez supprimer la sauvegarde: {self.backup_dir}")
            print("\n  3. Commit les changements:")
            print("     git add .")
            print("     git commit -m 'Restructuration du projet'")
            
            return True
            
        except Exception as e:
            ColorPrint.print_error(f"ERREUR CRITIQUE: {e}")
            ColorPrint.print_warning(f"Restaurez depuis: {self.backup_dir}")
            return False


def main():
    """Point d'entrée principal."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Migre automatiquement la structure du projet surveillance-matériel"
    )
    parser.add_argument(
        'project_path',
        nargs='?',
        default='.',
        help='Chemin vers le dossier du projet (défaut: dossier actuel)'
    )
    
    args = parser.parse_args()
    
    migrator = ProjectMigrator(args.project_path)
    success = migrator.run()
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()