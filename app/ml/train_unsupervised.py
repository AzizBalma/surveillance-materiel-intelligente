import pandas as pd
import numpy as np
import joblib
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import IsolationForest
from sklearn.cluster import KMeans
from yellowbrick.cluster import KElbowVisualizer, SilhouetteVisualizer
import os
import logging

# Configuration logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class EnhancedAnomalyDetector:
    def __init__(self):
        self.model_dir = '/app/models'
        self.visual_dir = '/app/visualizations'
        os.makedirs(self.model_dir, exist_ok=True)
        os.makedirs(self.visual_dir, exist_ok=True)
        self.isolation_forest = None
        self.scaler = None
        self.kmeans = None

    def train_models(self, df):
        logging.info("🎯 Préparation des données pour ML")
        # Colonnes pertinentes
        features = ['cpu_util','mem_util','temp_cpu','net_in_bytes','net_out_bytes','tcp_conn','user_active','usb_event']
        X = df[features].fillna(0)
        
        self.scaler = StandardScaler()
        X_scaled = self.scaler.fit_transform(X)
        
        # Isolation Forest
        self.isolation_forest = IsolationForest(contamination=0.1, random_state=42)
        self.isolation_forest.fit(X_scaled)
        
        # KMeans
        self.kmeans = KMeans(n_clusters=3, random_state=42)
        self.kmeans.fit(X_scaled)
        
        # Yellowbrick visualisations
        self.visualize_clusters(X_scaled)
        
        return X_scaled

    def visualize_clusters(self, X_scaled):
        try:
            logging.info("📊 Génération visualisations Yellowbrick")
            kmeans = KMeans(random_state=42)
            viz = KElbowVisualizer(kmeans, k=(2,10))
            viz.fit(X_scaled)
            viz.show(outpath=os.path.join(self.visual_dir,'elbow.png'))

            kmeans = KMeans(n_clusters=3, random_state=42)
            viz2 = SilhouetteVisualizer(kmeans)
            viz2.fit(X_scaled)
            viz2.show(outpath=os.path.join(self.visual_dir,'silhouette.png'))
        except Exception as e:
            logging.warning(f"⚠️ Visualisation échouée: {e}")

    def detect_anomalies(self, df):
        features = ['cpu_util','mem_util','temp_cpu','net_in_bytes','net_out_bytes','tcp_conn','user_active','usb_event']
        X = df[features].fillna(0)
        X_scaled = self.scaler.transform(X)
        df['is_anomaly'] = self.isolation_forest.predict(X_scaled)
        df['is_anomaly'] = df['is_anomaly'].apply(lambda x: 1 if x==-1 else 0)
        df['anomaly_score'] = self.isolation_forest.decision_function(X_scaled)
        return df

    def save_models(self):
        joblib.dump(self.isolation_forest, os.path.join(self.model_dir,'if_model.pkl'))
        joblib.dump(self.scaler, os.path.join(self.model_dir,'scaler.pkl'))
        joblib.dump(self.kmeans, os.path.join(self.model_dir,'kmeans.pkl'))
        logging.info("💾 Modèles sauvegardés")
    
    def load_models(self):
        self.isolation_forest = joblib.load(os.path.join(self.model_dir,'if_model.pkl'))
        self.scaler = joblib.load(os.path.join(self.model_dir,'scaler.pkl'))
        self.kmeans = joblib.load(os.path.join(self.model_dir,'kmeans.pkl'))

# -------------------
# Chargement du CSV et entraînement
# -------------------
if __name__ == "__main__":
    csv_path = os.path.join('..','..', '..', 'data', 'donnees_ml.csv')
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"Le fichier {csv_path} est introuvable.")
    
    df = pd.read_csv(csv_path)
    logging.info(f"📥 Données chargées depuis {csv_path}, {len(df)} lignes")

    detector = EnhancedAnomalyDetector()
    detector.train_models(df)
    detector.save_models()
    logging.info("✅ Entraînement terminé et modèles sauvegardés")

    # Optionnel : détecter les anomalies et sauvegarder
    df_anomalies = detector.detect_anomalies(df)
    df_anomalies.to_csv(os.path.join('..', 'data', 'donnee_ml_with_anomalies.csv'), index=False)
    logging.info("💾 Anomalies détectées et sauvegardées dans donnee_ml_with_anomalies.csv")
